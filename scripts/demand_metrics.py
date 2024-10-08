import configparser
import os
import warnings
import pandas as pd
import numpy as np
import geopandas as gpd

from glassfibre.preprocessing import population_decile

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

def demand(iso3):
    """
    This function generate demand results for each country.
    
    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating demand results for {} csv'.format(iso3))
    demand_folder = os.path.join(DATA_RESULTS, iso3, 'population', 
                 '{}_demand_metrics.shp'.format(iso3))
    df = gpd.read_file(demand_folder)
    df = df[['GID_2', 'area', 'population']]
    df = df.groupby(['GID_2', 'area'])['population'].sum().reset_index()
    df[['iso3', 'pop_den_km']] = ''

    for i in range(len(df)):

        df['iso3'].loc[i] = iso3
        df['pop_den_km'].loc[i] = df['population'].loc[i] / df['area'].loc[i] 

    for idx, country in countries.iterrows():
            
        if not country['iso3'] == iso3:

            continue

        arpu = countries['arpu'].loc[idx]
        adoption_low = round(countries['adoption_low'].loc[idx], 0)
        df[['low', 'baseline', 'high']] = ''
        df['low_adoption'] = 'low'
        df['baseline_adoption'] = 'baseline'
        df['high_adoption'] = 'high'
        df = pd.melt(df, id_vars = ['iso3', 'GID_2', 'area', 'population', 
            'pop_den_km', ], var_name = 'adoption_scenario', value_vars = 
            ['low', 'baseline', 'high'])
        df = df.drop(columns = ['value'])
        df[['adoption_value', 'users_area_sqkm', 'revenue_per_area', 'geotype']] = ''
        df['pop_den_km'] = df['pop_den_km'].astype(float)

        for i in range(len(df)):

            if df['adoption_scenario'].loc[i] == 'low':

                df['adoption_value'].loc[i] = round((adoption_low / 100), 4)
                df['users_area_sqkm'].loc[i] = (df['adoption_value'].loc[i] 
                                                * df['pop_den_km'].loc[i])
                df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                 * (arpu))
                
            elif df['adoption_scenario'].loc[i] == 'baseline':

                df['adoption_value'].loc[i] = round((adoption_low / 100) + (0.1 
                                              * ((adoption_low / 100))), 4)
                df['users_area_sqkm'].loc[i] = (df['adoption_value'].loc[i] 
                                                * df['pop_den_km'].loc[i])
                df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                 * (arpu))
                
            else:

                df['adoption_value'].loc[i] = round((adoption_low / 100) + (0.2 
                                              * ((adoption_low / 100))), 4)
                df['users_area_sqkm'].loc[i] = (df['adoption_value'].loc[i] 
                                                * df['pop_den_km'].loc[i])
                df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                 * (arpu))

            df['geotype'].loc[i] = population_decile(df['pop_den_km'].loc[i])
                
        df = df[['iso3', 'GID_2', 'area', 'population', 'adoption_scenario',
                 'adoption_value', 'pop_den_km', 'geotype', 'users_area_sqkm', 
                 'revenue_per_area']]

    fileout = '{}_demand_results.csv'.format(iso3)
    folder_out = os.path.join(DATA_RESULTS, iso3, 'demand')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)

    df.to_csv(path_out, index = False)
    

    return None         


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
                    gdf[['total_area_revenue']] = ''
                    
                    for i in range(len(gdf)):
                        
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


def generate_population_decile():

    """
    This function generates population decile for each country and combine them 
    together.
    """

    isos = os.listdir(DATA_RESULTS)
    merged_data = pd.DataFrame()
    merged_data_1 = pd.DataFrame()
    print('Generating population deciles')

    for iso3 in isos:

        base_directory = os.path.join(DATA_RESULTS, iso3, 'population') 

        for root, _, files in os.walk(base_directory):

            for file in files:

                if file.endswith('_population_results.csv'):
                    
                    file_path = os.path.join(base_directory, 
                                '{}_population_results.csv'.format(iso3))
                    df = pd.read_csv(file_path)
                    df['pop_density_sqkm'] = df['population'] / df['area']

                    df1 = pd.read_csv(file_path)
                    df1 = df1.groupby(['iso3', 'GID_1']).agg({'population': 
                                        'sum', 'area': 'sum'}).reset_index()
                                                                  
                    df1['pop_density_sqkm'] = df1['population'] / df1['area']

                    df = df[['iso3', 'GID_1', 'GID_2', 'area', 'population', 
                             'pop_density_sqkm']]
                    df1 = df1[['iso3', 'GID_1', 'area', 'population', 
                               'pop_density_sqkm']]
                    merged_data = pd.concat([merged_data, df], 
                                            ignore_index = True)
                    merged_data_1 = pd.concat([merged_data_1, df1], 
                                              ignore_index = True)            
                    
                fileout = 'subregional_population_deciles.csv'
                fileout_1 = 'regional_population_deciles.csv'
                folder_out = os.path.join(DATA_RESULTS, '..', 'SSA')

                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                path_out_1 = os.path.join(folder_out, fileout_1)
                merged_data.to_csv(path_out, index = False)
                merged_data_1.to_csv(path_out_1, index = False)
    
    reg_data = pd.DataFrame()
    subregion_data = pd.DataFrame()

    pop_folder = os.path.join(DATA_RESULTS, '..', 'SSA')
    regional_population = os.path.join(pop_folder, 
                          'regional_population_deciles.csv')
    subregion_population = os.path.join(pop_folder, 
                          'subregional_population_deciles.csv')
    df = pd.read_csv(regional_population)
    df1 = pd.read_csv(subregion_population)
    df = df.sort_values(by = 'pop_density_sqkm', ascending = True)                   
    df['decile_value'] = pd.qcut(df['pop_density_sqkm'], 10, 
                                    labels = False) + 1
    df['decile'] = ""

    df1 = df1.sort_values(by = 'pop_density_sqkm', ascending = True)
    df1['decile_value'] = pd.qcut(df1['pop_density_sqkm'], 10, 
                                    labels = False) + 1
    df1['decile'] = ""

    for i in range(len(df)):

        df['decile'].loc[i] = population_decile(df['decile_value'].loc[i])

    reg_data = pd.concat([reg_data, df], ignore_index = True)  

    for i in range(len(df1)):

        df1['decile'].loc[i] = population_decile(df1['decile_value'].loc[i])
    
    subregion_data = pd.concat([subregion_data, df1], ignore_index = True) 

    filename = 'SSA_regional_population_deciles.csv'
    filename_1 = 'SSA_subregional_population_deciles.csv'

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, filename)
    path_out_1 = os.path.join(folder_out, filename_1)
    reg_data.to_csv(path_out, index = False)
    subregion_data.to_csv(path_out_1, index = False)


    return None


def combine_pcsf_fiber_lines():
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
    
                if file.endswith('{}_combined_pcsf_access_edges.shp'.format(iso3)):

                    file_path = os.path.join(root, file)
                    gdf = gpd.read_file(file_path)
                    combined_gdf = pd.concat([combined_gdf, gdf], 
                                                ignore_index = True) 
                    
                    fileout = 'SSA_combined_pcsf_access_edges.shp'
                    folder_out = os.path.join(DATA_AFRICA, 'shapefiles')
                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    combined_gdf.to_file(path_out, index = False)
    return None


def combine_pcsf_fiber_nodes():
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
    
                if file.endswith('{}_combined_pcsf_subregional_nodes.shp'.format(iso3)):

                    file_path = os.path.join(root, file)
                    gdf = gpd.read_file(file_path)
                    combined_gdf = pd.concat([combined_gdf, gdf], 
                                                ignore_index = True) 
                    
                    fileout = 'SSA_combined_pcsf_access_nodes.shp'
                    folder_out = os.path.join(DATA_AFRICA, 'shapefiles')
                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    combined_gdf.to_file(path_out, index = False)
    return None

for idx, country in countries.iterrows():
        
    if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    #if not country['iso3'] == 'RWA':

        continue

'''generate_demand_metrics(countries['iso3'].loc[idx])
combine_fiber_shapefiles('combined_regional_nodes')
combine_fiber_shapefiles('combined_regional_edges')
combine_fiber_shapefiles('combined_access_nodes')
combine_fiber_shapefiles('combined_access_edges')
combine_existing_fiber_shapefiles('core_nodes_existing')
combine_existing_fiber_shapefiles('core_edges_existing')'''
#generate_population_decile()
#combine_pcsf_fiber_lines()
#combine_pcsf_fiber_nodes()