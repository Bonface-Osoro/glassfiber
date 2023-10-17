import configparser
import os
import warnings
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')

class PointsGenerator:

    """
    This class generates points for each polygon
    """

    def __init__(self, country_iso3):
        """
        A class constructor

        Arguments
        ---------
        country_iso3 : string
            Country iso3 to be processed.
        """
        self.country_iso3 = country_iso3

    def generate_points(self):
        
        """
        This function generates geospatial points for 
        every region.
        """
        regions = os.path.join(DATA_PROCESSED, self.country_iso3, 'regions')
        region_1 = os.path.join(regions, 'regions_1_{}.shp'.format(self.country_iso3))
        gdf1 = gpd.read_file(region_1)
        gdf1 = gdf1.to_dict('records')
        region_2 = os.path.join(regions, 'regions_2_{}.shp'.format(self.country_iso3)) 

        if os.path.exists(region_2):

            gdf2 = gpd.read_file(region_2)
            gdf2 = gdf2.to_dict('records')

            for myitem in tqdm(gdf1, desc = 'Generating geospatial points for {}'. format(self.country_iso3)):

                my_points = []

                for myitem2 in gdf2:

                    if myitem['GID_1'] == myitem2['GID_1']:

                        my_points.append({
                            'geometry': {
                                'type':'Point',
                                'coordinates': myitem2['geometry'].representative_point()   
                            },
                            'properties': {
                                'GID_2': myitem2['GID_2']
                            }
                        })
                
                mypoints = gpd.GeoDataFrame.from_features(my_points, crs='epsg:4326')

                folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'gid_points')
                fileout = '{}.shp'.format(myitem['GID_1'])

                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                
                mypoints.to_file(path_out, driver = 'ESRI Shapefile')

        else:

            regions = os.path.join(DATA_PROCESSED, self.country_iso3)
            region_2 = os.path.join(regions, 'national_outline.shp')  
            gdf2 = gpd.read_file(region_2) 
            
               
            gdf2 = gdf2.to_dict('records')

            for myitem in tqdm(gdf2, desc = 'Generating geospatial points for {}'. format(self.country_iso3)):

                my_points = []

                for myitem2 in gdf1:

                    if myitem['GID_0'] == myitem2['GID_0']:

                        my_points.append({
                            'geometry': {
                                'type':'Point',
                                'coordinates': myitem2['geometry'].representative_point()   
                            },
                            'properties': {
                                'GID_1': myitem2['GID_1']
                            }
                        })
                
                mypoints = gpd.GeoDataFrame.from_features(my_points, crs='epsg:4326')

                folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'gid_points')
                fileout = '{}.shp'.format(myitem2['GID_1'])

                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                
                mypoints.to_file(path_out, driver = 'ESRI Shapefile')


        return None