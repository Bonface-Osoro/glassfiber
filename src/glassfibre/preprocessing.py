import configparser
import json
import os
import rasterio
import geopandas as gpd
import pandas as pd
from rasterio.mask import mask
from rasterstats import zonal_stats
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from tqdm import tqdm

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

def remove_small_shapes(x):
    """
    Remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    if x.geometry.type == 'Polygon':

        return x.geometry

    elif x.geometry.type == 'MultiPolygon':

        area1 = 0.01
        area2 = 50

        if x.geometry.area < area1:
            return x.geometry

        if x['GID_0'] in ['CHL','IDN']:

            threshold = 0.01

        elif x['GID_0'] in ['RUS','GRL','CAN','USA']:

            threshold = 0.01

        elif x.geometry.area > area2:

            threshold = 0.1

        else:

            threshold = 0.001

        new_geom = []
        for y in list(x['geometry'].geoms):

            if y.area > threshold:

                new_geom.append(y)

        return MultiPolygon(new_geom)


class ProcessCountry:

    """
    This class process the country folders and
    the national outline shapefile.
    """


    def __init__(self, csv_country, country_iso3):
        """
        A class constructor

        Arguments
        ---------
        csv_country : string
            Name of the country metadata file.
        country_iso3 : string
            Country iso3 to be processed.
        """
        self.csv_country = csv_country
        self.country_iso3 = country_iso3


    def get_countries(self):
        """
        Get all countries.

        Returns
        -------
        countries : dataframe
            Dataframe containing all the country metadata.

        """
        countries = pd.read_csv(self.csv_country, encoding = 'latin-1')

        countries = countries[countries.Exclude == 0]
        
        countries = countries.sample(frac = 1)

        return countries
    

    def process_country_shapes(self):
        """
        This function creates regional folders for each country 
        and then process a national outline shapefile.

        """          
        path = os.path.join('results', 'processed', self.country_iso3)

        if os.path.exists(os.path.join(path, 'national_outline.shp')):

            print('Completed national outline processing')
            
        print('Processing country shapes for {}'.format(self.country_iso3))

        if not os.path.exists(path):

            os.makedirs(path)

        shape_path = os.path.join(path, 'national_outline.shp')

        path = os.path.join('data', 'raw', 'boundaries', 'gadm36_0.shp')

        countries = gpd.read_file(path)

        single_country = countries[countries.GID_0 == self.country_iso3].reset_index()

        single_country = single_country.copy()
        single_country['geometry'] = single_country.geometry.simplify(
            tolerance = 0.01, preserve_topology = True)
        
        single_country['geometry'] = single_country.apply(
            remove_small_shapes, axis = 1)
        
        glob_info_path = os.path.join(self.csv_country)
        load_glob_info = pd.read_csv(glob_info_path, encoding = 'ISO-8859-1', 
                                     keep_default_na = False)
        
        single_country = single_country.merge(load_glob_info, left_on = 'GID_0', 
            right_on = 'iso3')
        
        single_country.to_file(shape_path)

        return print('National outline shapefile processing completed for {}'.format(self.country_iso3))


class ProcessRegions:

    """
    This class process the country folders and
    the national outline shapefile.
    """


    def __init__(self, country_iso3, gid_level):
        """
        A class constructor

        Arguments
        ---------
        country_iso3 : string
            Country iso3 to be processed..
        gid_level : integer
            Gid level to process.
        """
        self.gid_level = gid_level
        self.country_iso3 = country_iso3


    def process_regions(self):
        """
        Function for processing the lowest desired subnational
        regions for the chosen country.
        """
        regions = []

        for regional_level in range(1, int(self.gid_level) + 1): 

            filename = 'regions_{}_{}.shp'.format(regional_level, self.country_iso3)
            folder = os.path.join('results', 'processed', self.country_iso3, 'regions')
            path_processed = os.path.join(folder, filename)

            if os.path.exists(path_processed):

                continue

            print('Processing GID_{} region shapes for {}'.format(regional_level, self.country_iso3))

            if not os.path.exists(folder):

                os.mkdir(folder)

            filename = 'gadm36_{}.shp'.format(regional_level)
            path_regions = os.path.join('data', 'raw', 'boundaries', filename)
            regions = gpd.read_file(path_regions)

            regions = regions[regions.GID_0 == self.country_iso3]

            regions = regions.copy()
            regions['geometry'] = regions.geometry.simplify(
                tolerance=0.005, preserve_topology=True)

            regions['geometry'] = regions.apply(remove_small_shapes, axis = 1)

            try:

                regions.to_file(path_processed, driver = 'ESRI Shapefile')

            except:

                print('Unable to write {}'.format(filename))

                pass

        return None
    

    def process_sub_region_boundaries(self):

        region_path = os.path.join('results', 'processed', self.country_iso3, 'regions', 'regions_{}_{}.shp'.format(2, self.country_iso3)) 
        region_path_2 = os.path.join('results', 'processed', self.country_iso3, 'regions', 'regions_{}_{}.shp'.format(1, self.country_iso3))
        
        if os.path.exists(region_path):

            countries = gpd.read_file(region_path)
            gid = 'GID_2'

        else:

            countries = gpd.read_file(region_path_2)
            gid = 'GID_1'

        for index, row in tqdm(countries.iterrows(), desc = 'Processing sub-region boundaries for {}'.format(self.country_iso3)):

            sub_region_shapefile = gpd.GeoDataFrame([row], crs = countries.crs)

            filename = '{}.shp'.format(row[gid])    

            folder_out = os.path.join('results', 'processed', self.country_iso3, 'boundaries')

            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, filename)

            sub_region_shapefile.to_file(path_out, driver = 'ESRI Shapefile')

        return None


class ProcessPopulation:
    """
    This class process the country folders and
    the national outline shapefile.
    """


    def __init__(self, csv_country, country_iso3, gid_region, pop_tiff):
        """
        A class constructor

        Arguments
        ---------
        csv_country : string
            Name of the country metadata file.
        country_iso3 : string
            Country iso3 to be processed.
        gid_region: string
            GID boundary spatial level to process
        pop_tiff: string
            Filename of the population raster layer

        """
        self.csv_country = csv_country
        self.country_iso3 = country_iso3
        self.pop_tiff = pop_tiff
        self.gid_region = gid_region


    def process_national_population(self):

        """
        This function creates a national population .tiff
        using national boundary files created in 
        process_national_boundary function
        """

        iso3 = self.country_iso3

        filename = self.pop_tiff
        path_pop = os.path.join(filename)
        hazard = rasterio.open(path_pop, 'r+')
        hazard.nodata = 255                       
        hazard.crs.from_epsg(4326) 

        filename = 'national_outline.shp'
        folder = os.path.join('results', 'processed', self.country_iso3)
        
        #then load in our country as a geodataframe
        path_in = os.path.join(folder, filename)
        country_pop = gpd.read_file(path_in, crs = 'epsg:4326')

        #create a new gpd dataframe from our single country geometry
        geo = gpd.GeoDataFrame(gpd.GeoSeries(country_pop.geometry))

        #this line sets geometry for resulting geodataframe
        geo = geo.rename(columns={0:'geometry'}).set_geometry('geometry')

        #convert to json
        coords = [json.loads(geo.to_json())['features'][0]['geometry']]        

        #carry out the clip using our mask
        out_img, out_transform = mask(hazard, coords, crop = True)

        #update our metadata
        out_meta = hazard.meta.copy()
        out_meta.update({'driver': 'GTiff', 'height': out_img.shape[1],
                        'width': out_img.shape[2], 'transform': out_transform,
                        'crs': 'epsg:4326'})
        
        #now we write out at the regional level
        filename_out = 'ppp_2020_1km_Aggregated.tif' 
        folder_out = os.path.join('results', 'processed', iso3, 'population', 'national')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, filename_out)

        with rasterio.open(path_out, 'w', ** out_meta) as dest:

            dest.write(out_img)

        return print('Population processing completed for {}'.format(iso3))
    

    def process_population_tif(self):
        """
        Process population layer.
        
        Parameters
        ----------
        data_name: string
            Filename of the population raster layer
        gid_level: string
            GID boundary spatial level to process
            
        Returns
        -------
        output: dictionary.
            Dictionary containing the country population and grid level
        """
        gid_region = self.gid_region
        iso = self.country_iso3

        filename = 'regions_{}_{}.shp'.format(gid_region, iso)
        path_regions = os.path.join('results', 'processed', iso, 'regions', filename)
        rastername = 'ppp_2020_1km_Aggregated.tif'
        path_raster = os.path.join('results', 'processed', iso, 'population', 'national', rastername)

        boundaries = gpd.read_file(path_regions, crs = 'epsg:4326')

        output = []
        print('Working on {}'.format(iso))
        for idx, boundary in boundaries.iterrows():
    
            with rasterio.open(path_raster) as src:
                
                affine = src.transform
                array = src.read(1)
                array[array <= 0] = 0
                
                population = [i['sum'] for i in zonal_stats(
                    boundary['geometry'], array, nodata = 255,
                    stats = ['sum'], affine = affine)][0]

                #Calculate the central coordinates of each of the polygons
                boundary['centroid'] = boundary['geometry'].centroid
                boundary['longitude'] = boundary['centroid'].x
                boundary['latitude'] = boundary['centroid'].y
                try:
                    output.append({
                        'iso3':boundary['GID_0'],
                        'region':boundary['NAME_1'],
                        'GID_1': boundary['GID_2'],
                        'population': population,
                        'latitude': boundary['latitude'],
                        'longitude': boundary['longitude'],
                        'geometry': boundary['geometry'],
                        'area': (boundary['geometry'].area) * 12309
                    })
                    
                except:
                    output.append({
                        'iso3':boundary['GID_0'],
                        'region':boundary['NAME_1'],
                        'GID_1': boundary['GID_1'],
                        'population': population,
                        'latitude': boundary['latitude'],
                        'longitude': boundary['longitude'],
                        'geometry': boundary['geometry'],
                        'area': (boundary['geometry'].area) * 12309
                    })

        df = pd.DataFrame(output)
        df.dropna(subset = ['population'], inplace = True)
        df['population'] = df['population'].astype(int)
        df[['latitude', 'longitude']] = df[['latitude', 'longitude']].round(4)

        fileout = '{}_population_results.csv'.format(iso)
        folder_out = os.path.join('results', 'final', iso, 'population')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        df.to_csv(path_out, index = False)

        return output