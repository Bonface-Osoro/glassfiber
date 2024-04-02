import configparser
import os
import warnings
import shapely
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


def download_road_data(iso3):

    """
    This function download the road data for each country.

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
        roads = ox.graph_from_place(format(ssa['country']))

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
        for i in range(len(df)):

            df['iso3'].loc[i] = iso3

        df['geometry'] = df['geometry'].apply(lambda x: shapely.wkt.loads(x))
        gdf = gpd.GeoDataFrame(data = df, geometry = df['geometry'], crs = 4329)

        filename = '{}_street_data.shp'.format(iso3)
        folder_out = os.path.join(DATA_RAW, 'street_data', iso3)

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, filename)
        gdf.to_file(path_out, crs = 'EPSG:4326')


    return None


for idx, country in countries.iterrows():
        
    #if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    if not country['iso3'] == 'SLE':

        continue

    #download_road_data(countries['iso3'].loc[idx])
    generate_street_shapefile(countries['iso3'].loc[idx])