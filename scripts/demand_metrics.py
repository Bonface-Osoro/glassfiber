import configparser
import os
import warnings
import pandas as pd
import numpy as np
import geopandas as gpd

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 'SSA')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'utf-8-sig')
southern = ['AGO', 'ZMB', 'ZWE', 'NAM', 'BWA', 'ZAF', 'LSO', 
            'SWZ', 'MOZ', 'MWI']

central = ['CMR', 'CAF', 'TCD', 'COD', 'GNQ', 'GAB', 'STP', 'COG']

eastern = ['BDI', 'COM', 'DJI', 'ERI', 'ETH', 'SWZ', 'MDG', 
           'KEN', 'MUS', 'SDN', 'SYC', 'SOM', 'SSD', 'UGA', 
           'TZA']

west = ['BEN', 'BFA', 'CPV', 'CIV', 'GMB', 'GHA', 'GIN', 
        'GNB', 'LBR', 'MLI', 'MRT', 'NER', 'NGA', 'SEN', 
        'SLE', 'TGO']

def generate_demand_metrics(iso3):
    """
    This function generates demand metrics for a single country.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating demand metrics for {}'.format(iso3))
    file = os.path.join(DATA_RESULTS, iso3, 'population', 
                        '{}_population_results.csv'.format(iso3))
    settlement_folder_in = os.path.join(DATA_PROCESSED, iso3, 'settlements')
    df = pd.read_csv(file)
    df.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
    df = df[['GID_2', 'area']]

    merged_shapefile = gpd.GeoDataFrame()
    for file_name in os.listdir(settlement_folder_in):

        if file_name.endswith('access_settlements.shp'):

            file_path = os.path.join(settlement_folder_in, file_name)
            gdf = gpd.read_file(file_path)
            gdf.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
            gdf = gdf[['iso3', 'GID_2', 'population', 'geometry', 'type']]

            merged_df = pd.merge(gdf, df, on = 'GID_2', how = 'inner')
            merged_df['pop_den_km'] = ''
            for i in range(len(merged_df)):

                merged_df['pop_den_km'].loc[i] = (
                    merged_df['population'].loc[i] / merged_df['area'].loc[i])
            
            merged_shapefile = pd.concat([merged_shapefile, merged_df], 
                                        ignore_index = True) 
            
            folder_out = os.path.join(DATA_RESULTS, iso3, 'population')
            fileout = '{}_demand_metrics.shp'.format(iso3)
            if not os.path.exists(folder_out):
                
                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, fileout)
            merged_shapefile.to_file(path_out, index = False)


    return None


def combine_shapefiles():
    """
    This function combines shapefiles of individual country into a single one.
    """
    isos = os.listdir(DATA_RESULTS)
    combined_gdf = gpd.GeoDataFrame()
    combined_df = pd.DataFrame()
    
    for iso3 in isos:

        print('Combining data for {}'.format(iso3))
        shapefile_path = os.path.join(DATA_RESULTS, iso3, 'population')

        for root, _, files in os.walk(shapefile_path):

            for file in files:

                if file.endswith('.shp'):

                    file_path = os.path.join(root, file)
                    gdf = gpd.read_file(file_path)
                    gdf[['region', 'total_area_revenue']] = ''
                    
                    for i in range(len(gdf)):

                        if iso3 in southern:

                            gdf['region'].loc[i] = 'southern'
                        
                        elif iso3 in central:

                            gdf['region'].loc[i] = 'central'

                        elif iso3 in eastern:

                            gdf['region'].loc[i] = 'eastern'

                        else:

                            gdf['region'].loc[i] = 'west'
                        
                        for idx, country in countries.iterrows():
            
                            if not country['iso3'] == iso3:

                                continue

                            arpu = countries['arpu'].loc[idx]

                            gdf['total_area_revenue'].loc[i] = (
                                (gdf['population'].loc[i]) * (arpu))
                            
                    combined_gdf = pd.concat([combined_gdf, gdf], 
                                                ignore_index = True) 
                    combined_df = pd.concat([combined_df, gdf], ignore_index = 
                                            True)
                    
                    fileout = 'SSA_demand_metrics.shp'
                    filename = 'SSA_demand_metrics.csv'
                    folder_out = os.path.join(DATA_AFRICA, 'shapefiles')
                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    path_out1 = os.path.join(DATA_AFRICA, filename)
                    combined_gdf.to_file(path_out, index = False)
                    combined_df.to_csv(path_out1, index = False)


    return None


def combine_fiber_shapefiles(metric):
    """
    This function combines shapefiles of individual country into a single one.

    Parameters
    ----------
    metric : string
        Network level and shape being quantified'
    """
    isos = os.listdir(DATA_PROCESSED)
    combined_gdf = gpd.GeoDataFrame()
    
    for iso3 in isos:

        print('Combining data for {}'.format(iso3))
        shapefile_path = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                      'combined')

        for root, _, files in os.walk(shapefile_path):

            for file in files:

                if file.endswith('{}.shp'.format(metric)):

                    file_path = os.path.join(root, file)
                    gdf = gpd.read_file(file_path)
                    gdf['region'] = ''
                    
                    for i in range(len(gdf)):

                        if iso3 in southern:

                            gdf['region'].loc[i] = 'southern'
                        
                        elif iso3 in central:

                            gdf['region'].loc[i] = 'central'

                        elif iso3 in eastern:

                            gdf['region'].loc[i] = 'eastern'

                        else:

                            gdf['region'].loc[i] = 'west'

                    combined_gdf = pd.concat([combined_gdf, gdf], 
                                                ignore_index = True) 
                    
                    fileout = 'SSA_{}.shp'.format(metric)
                    folder_out = os.path.join(DATA_AFRICA, 'shapefiles')
                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    combined_gdf.to_file(path_out, index = False)
    return None


def combine_existing_fiber_shapefiles(metric):
    """
    This function exclusively combines existing fiber shapefiles of an 
    individual country into a single one.
    """
    isos = os.listdir(DATA_PROCESSED)
    combined_gdf = gpd.GeoDataFrame()
    
    for iso3 in isos:

        print('Combining data for {}'.format(iso3))
        shapefile_path = os.path.join(DATA_PROCESSED, iso3, 'network_existing')

        for root, _, files in os.walk(shapefile_path):

            for file in files:

                if file.endswith('{}.shp'.format(metric)):

                    file_path = os.path.join(root, file)
                    gdf = gpd.read_file(file_path)
                    gdf['region'] = ''
                    
                    for i in range(len(gdf)):

                        if iso3 in southern:

                            gdf['region'].loc[i] = 'southern'
                        
                        elif iso3 in central:

                            gdf['region'].loc[i] = 'central'

                        elif iso3 in eastern:

                            gdf['region'].loc[i] = 'eastern'

                        else:

                            gdf['region'].loc[i] = 'west'

                    combined_gdf = pd.concat([combined_gdf, gdf], 
                                                ignore_index = True) 
                    
                    fileout = 'SSA_{}.shp'.format(metric)
                    folder_out = os.path.join(DATA_AFRICA, 'shapefiles')
                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    combined_gdf.to_file(path_out, index = False)
    return None

def combine_africa_shapefile():
    """
    This function combines the African boundary shapefile with the demand 
    metrics
    """
    file = os.path.join(DATA_AFRICA, 'shapefiles', 'SSA_demand_metrics.shp')
    file_1 = os.path.join(DATA_RAW, 'Africa_Boundaries', 'SSA_combined_shapefile.shp')
    gdf = gpd.read_file(file)
    gdf = gdf[['iso3', 'GID_2', 'population', 'type', 'area', 'pop_den_km', 
                 'region', 'total_area']]
    gdf1 = gpd.read_file(file_1)
    gdf1 = gdf1[['GID_1', 'GID_2', 'geometry']]

    merged_df = gdf.merge(gdf1, on = 'GID_2')
    merged_df = gpd.GeoDataFrame(merged_df, geometry = 'geometry')
    merged_df.crs = 'EPSG:4326'
    folder_out = os.path.join(DATA_AFRICA, 'shapefiles')

    fileout = 'SSA_gid_2_demand_metrics.shp'
    path_out = os.path.join(folder_out, fileout)
    merged_df.to_file(path_out, index = False)


    return None

combine_africa_shapefile()
#combine_shapefiles()
'''for idx, country in countries.iterrows():
        
    if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    #if not country['iso3'] == 'RWA':

        continue

    generate_demand_metrics(countries['iso3'].loc[idx])
combine_fiber_shapefiles('combined_regional_nodes')
combine_fiber_shapefiles('combined_regional_edges')
combine_fiber_shapefiles('combined_access_nodes')
combine_fiber_shapefiles('combined_access_edges')
combine_existing_fiber_shapefiles('core_nodes_existing')
combine_existing_fiber_shapefiles('core_edges_existing')'''