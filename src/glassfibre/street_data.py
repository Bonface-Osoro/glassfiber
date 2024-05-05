import configparser
import os
import warnings
import shapely
import shutil
import geopandas as gpd
import pandas as pd
import osmnx as ox
from shapely import wkt
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'utf-8-sig')


def download_street_data(iso3):

    """
    This function download the street data for each country.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    ssa_countries = countries

    for idx, ssa in ssa_countries.iterrows():

        if not ssa['iso3'] == iso3:

            continue
        
        print('Extracting street data for {}'.format(iso3))
        roads = ox.graph_from_place(format('{}'.format(ssa['country'])))

        print('Converting extracted {} street data to geodataframe'.format(iso3))
        road_gdf = ox.graph_to_gdfs(roads, nodes = False, edges = True)

        print('Converting extracted {} street geodataframe to csv'.format(iso3))
        fileout = '{}_national_street_data.csv'.format(iso3)
        folder_out = os.path.join(DATA_RAW, 'street_data', iso3)
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        road_gdf.to_csv(path_out, index = False)


    return None


def generate_street_shapefile(iso3):

    """
    This function convert the downloaded csv data into shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    ssa_countries = countries

    for idx, ssa in ssa_countries.iterrows():

        if not ssa['iso3'] == iso3:

            continue
        
        csv_path = os.path.join(DATA_RAW, 'street_data', iso3, 
                                '{}_national_street_data.csv'.format(iso3))
        
        print('Reading CSV street data for {}'.format(iso3))
        df = pd.read_csv(csv_path)
        df = df[['highway', 'length', 'geometry']]
        df['iso3'] = ''

        print('Processing CSV street data for {}'.format(iso3))
        df['iso3'] = iso3
        df['geometry'] = df['geometry'].apply(lambda x: shapely.wkt.loads(x))
        gdf = gpd.GeoDataFrame(data = df, geometry = df['geometry'], crs = 4329)

        filename = '{}_street_data.shp'.format(iso3)
        folder_out = os.path.join(DATA_RAW, 'street_data', iso3)

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, filename)
        gdf.to_file(path_out, crs = 'EPSG:4326')


    return None


def process_region_street(iso3):
    """
    Function to process the street data at regional level.  

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    regions = os.path.join(DATA_PROCESSED, iso3, 'regions', 
                           'regions_1_{}.shp'.format(iso3))
    
    for idx, country in countries.iterrows():

        if not country["iso3"] == iso3:

            continue

        regions = gpd.read_file(regions)
        gid = 'GID_1'

        for idx, region in regions.iterrows():
            
            gdf_region = regions
            gid_id = region[gid]

            file_in = os.path.join(DATA_RAW, 'street_data', iso3, 
                                   '{}_street_data.shp'.format(iso3))

            gdf_street = gpd.read_file(file_in)
            gdf_region = gdf_region[gdf_region[gid] == gid_id]
            print('Intersecting {} street data points'.format(gid_id))
            gdf_street = gpd.overlay(gdf_street, gdf_region, how = 
                                    'intersection')
            
            filename = '{}.shp'.format(gid_id)
            folder_out = os.path.join(DATA_PROCESSED, iso3, 'streets', 
                                    'regions')
            
            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, filename)
            gdf_street.to_file(path_out, crs = 'EPSG:4326')


    return None


def process_subregion_street(iso3):
    """
    Function to process the street data at sub-regional level.  

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    for idx, country in countries.iterrows():

        if not country["iso3"] == iso3:

            continue

        region_path = os.path.join(DATA_PROCESSED, iso3, 'regions', 
                            'regions_2_{}.shp'.format(iso3))
        region_path_2 = os.path.join('results', 'processed', iso3, 'regions', 
                                    'regions_1_{}.shp'.format(iso3))

        if os.path.exists(region_path):

            regions = gpd.read_file(region_path)
            gid = 'GID_2'

        else:

            regions = gpd.read_file(region_path_2)
            gid = 'GID_1'

        for idx, region in regions.iterrows():

            gid_id = region[gid]
            gdf_region = regions

            file_in = os.path.join(DATA_RAW, 'street_data', iso3, 
                                   '{}_street_data.shp'.format(iso3))

            gdf_street = gpd.read_file(file_in)
            gdf_region = gdf_region[gdf_region[gid] == gid_id]
            print('Intersecting {} street data points'.format(gid_id))
            gdf_street = gpd.overlay(gdf_street, gdf_region, how = 
                                     'intersection')
            
            filename = '{}.shp'.format(gid_id)
            folder_out = os.path.join(DATA_PROCESSED, iso3, 'streets', 
                                      'sub_regions')

            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, filename)
            gdf_street.to_file(path_out, crs = 'EPSG:4326')

    
    return None

def combine_street_csv(iso3):
    """
    This function combines street data generated for countries whose data cannot 
    be downloaded at once.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """

    combined_df = pd.DataFrame()
    csv_path = os.path.join(DATA_RAW, 'street_data', iso3)

    print('Merging {} csv files'.format(iso3))
    for root, _, files in os.walk(csv_path):

        for file in files:

            if file.endswith('.csv'):

                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)

                combined_df = pd.concat([combined_df, df], ignore_index = True)

                fileout = '{}_national_street_data.csv'.format(iso3)
                folder_out = os.path.join(DATA_RAW, 'street_data', iso3)
                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                combined_df.to_csv(path_out, index = False) 

    
    return None


def generate_region_nodes(iso3):
    """
    This function aggregates sub-regional settlement nodes within a region

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating {} regional settlement nodes'.format(iso3))
    regions = os.path.join(DATA_PROCESSED, iso3, 'regions', 
                           'regions_1_{}.shp'.format(iso3))
    
    for idx, country in countries.iterrows():

        if not country["iso3"] == iso3:

            continue

        regions = gpd.read_file(regions)
        gid = 'GID_1'

        for idx, region in regions.iterrows():
            
            gdf_region = regions
            gid_id = region[gid]

            file_in = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                      'combined', '{}_combined_access_nodes.shp'.format(iso3))

            gdf_settlement = gpd.read_file(file_in)
            gdf_region = gdf_region[gdf_region[gid] == gid_id]
            gdf_settlement = gpd.overlay(gdf_settlement, gdf_region, how = 
                                    'intersection')
            
            filename = '{}.shp'.format(gid_id)
            folder_out = os.path.join(DATA_PROCESSED, iso3, 
                        'buffer_routing_zones', 'pcsf_regional_nodes')
            try:
                gdf_settlement = gdf_settlement[['iso3', 'GID_1', 'GID_2', 
                                'population', 'type', 'lon', 'lat', 'geometry']]
            except:
                gdf_settlement.rename(columns = {'GID_1_1': 'GID_1', 'GID_1_2': 'GID_2'}, inplace = True)
                gdf_settlement = gdf_settlement[['iso3', 'GID_1', 'GID_2', 
                                'population', 'type', 'lon', 'lat', 'geometry']]
            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, filename)
            gdf_settlement.to_file(path_out, crs = 'EPSG:4326')


    return None


def generate_sub_region_nodes(iso3):
    """
    This function aggregates sub-regional settlement nodes within a subregion

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating {} sub-regional settlement nodes'.format(iso3))
    
    for idx, country in countries.iterrows():

        if not country["iso3"] == iso3:

            continue

        region_path = os.path.join('results', 'processed', iso3, 'regions', 
                                   'regions_2_{}.shp'.format(iso3)) 
        
        region_path_2 = os.path.join('results', 'processed', iso3, 'regions', 
                                   'regions_1_{}.shp'.format(iso3))        
        if os.path.exists(region_path):

            regions = gpd.read_file(region_path)
            gid = 'GID_2'

        else:

            regions = gpd.read_file(region_path_2)
            gid = 'GID_1'

        for idx, region in regions.iterrows():
            
            gdf_region = regions
            gid_id = region[gid]

            file_in = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                      'combined', '{}_combined_access_nodes.shp'.format(iso3))

            gdf_settlement = gpd.read_file(file_in)
            gdf_region = gdf_region[gdf_region[gid] == gid_id]
            gdf_settlement = gpd.overlay(gdf_settlement, gdf_region, how = 
                                    'intersection')
            
            filename = '{}.shp'.format(gid_id)
            folder_out = os.path.join(DATA_PROCESSED, iso3, 
                        'buffer_routing_zones', 'pcsf_subregional_nodes')
            
            try:
                gdf_settlement = gdf_settlement[['iso3', 'GID_1', 'GID_2_2', 
                                'population', 'type', 'lon', 'lat', 'geometry']]
                gdf_settlement.rename(columns = {'GID_2_2': 'GID_2'}, 
                                      inplace = True)
            except:
                gdf_settlement.rename(columns = {'GID_1_1': 'GID_1', 'GID_1_2': 'GID_2'}, inplace = True)
                gdf_settlement = gdf_settlement[['iso3', 'GID_1', 'GID_2', 
                                'population', 'type', 'lon', 'lat', 'geometry']]
            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, filename)
            gdf_settlement.to_file(path_out, crs = 'EPSG:4326')


    return None


for idx, country in countries.iterrows():
        
    #if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    if not country['iso3'] == 'GMB':

        continue
    
    
    #download_street_data(countries['iso3'].loc[idx])
    #combine_street_csv(countries['iso3'].loc[idx])
    #generate_street_shapefile(countries['iso3'].loc[idx])
    #process_region_street(countries['iso3'].loc[idx])
    #process_subregion_street(countries['iso3'].loc[idx])
    #generate_sub_region_nodes(countries['iso3'].loc[idx])