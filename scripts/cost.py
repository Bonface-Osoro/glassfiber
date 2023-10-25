import configparser
import os
import warnings
import pandas as pd
import geopandas as gpd
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'latin-1')

def generate_fiber_line_csv(iso3):
    """
    This function generate a csv file of optimized 
    fiber broadband lines for an individual country
    and merges it with regional populations.
    
    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('processing optimized fiber lines {} csv'.format(iso3))
    merged_shapefile = gpd.GeoDataFrame()
    line_folder = os.path.join(DATA_RESULTS, iso3, 'country_lines')
    pop_folder = os.path.join(DATA_RESULTS, iso3, 'population', '{}_population_results.csv'.format(iso3))

    df = pd.read_csv(pop_folder)

    for file_name in os.listdir(line_folder):

        if file_name.endswith('.shp'):

            file_path = os.path.join(line_folder, file_name)
            shapefile = gpd.read_file(file_path)
            shapefile = shapefile.to_crs(crs = 3857) 
            merged_shapefile = pd.concat([merged_shapefile, shapefile], ignore_index = True)
   
    merged_gdf = merged_shapefile.merge(df, on = 'GID_1')
    merged_gdf = merged_gdf.drop(columns = ['geometry_x', 'latitude', 'longitude', 'region'])
    merged_gdf = merged_gdf.rename(columns={'geometry_y': 'geometry'})   
    merged_gdf = merged_gdf[['iso3', 'GID_1', 'from', 'to', 'length', 
                             'population', 'source', 'area', 'geometry']]
    merged_gdf[['length', 'area']] = merged_gdf[['length', 'area']].round(4)

    fileout = '{}_mst_results.csv'.format(iso3, merged_shapefile).replace('shp', '_')
    folder_out = os.path.join(DATA_RESULTS, iso3, 'demand')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)

    merged_gdf.to_csv(path_out, index = False)
    

    return None            


def fiber_users(iso3):
    """
    This function quantifies 
    the number of projected 
    fiber broadband users

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('processing fiber broadband users {}'.format(iso3))
    merged_dataframe = pd.DataFrame()
    line_folder = os.path.join(DATA_RESULTS, iso3, 'demand')

    for idx, country in countries.iterrows():
            
        if not country['iso3'] == iso3:

            continue

        arpu = countries['arpu'].loc[idx]
        adoption_low = round(countries['adoption_low'].loc[idx], 0)
        
        for file_name in os.listdir(line_folder):

            if file_name.endswith('_mst_results.csv'):

                file_path = os.path.join(line_folder, file_name)
                df = pd.read_csv(file_path)
                df[['low', 'baseline', 'high']] = ''
                df['low_adoption'] = 'low'
                df['baseline_adoption'] = 'baseline'
                df['high_adoption'] = 'high'
                df = pd.melt(df, id_vars = ['iso3', 'GID_1', 'from', 'to', 'length', 
                        'population', 'source', 'area', 'geometry'], var_name = 
                        'adoption_scenario', value_vars = ['low', 
                        'baseline', 'high'])
                df = df.drop(columns = ['value'])
                df[['adoption_value', 'pop_density', 'users_area_sqkm', 'revenue_per_area', 'geotype']] = ''
                for i in range(len(df)):

                    if df['adoption_scenario'].loc[i] == 'low':
                        
                        df['adoption_value'].loc[i] = adoption_low
                        df['pop_density'].loc[i] = round((df['population'].loc[i])
                                                        / (df['area'].loc[i]), 4)
                        df['users_area_sqkm'].loc[i] = round((df['adoption_value'].loc[i] 
                                                        * df['pop_density'].loc[i]), 0)
                        df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) * (arpu)) / df['area'].loc[i]
                        
                    elif df['adoption_scenario'].loc[i] == 'baseline':

                        df['adoption_value'].loc[i] = adoption_low + (0.1 * (adoption_low))
                        df['pop_density'].loc[i] = round((df['population'].loc[i])
                                                        / (df['area'].loc[i]), 4)
                        df['users_area_sqkm'].loc[i] = round((df['adoption_value'].loc[i] 
                                                        * df['pop_density'].loc[i]), 0)
                        df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) * (arpu)) / df['area'].loc[i]
                        
                    else:

                        df['adoption_value'].loc[i] = adoption_low + (0.2 * (adoption_low))
                        df['pop_density'].loc[i] = round((df['population'].loc[i])
                                                        / (df['area'].loc[i]), 4)
                        df['users_area_sqkm'].loc[i] = round((df['adoption_value'].loc[i] 
                                                        * df['pop_density'].loc[i]), 0) 
                        df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) * (arpu)) / df['area'].loc[i]

                    if df['pop_density'].loc[i] >= 1000:

                        df['geotype'].loc[i] = 'urban'
                    
                    elif df['pop_density'].loc[i] >= 500 and df['pop_density'].loc[i] <= 1000:
                        
                        df['geotype'].loc[i] = 'suburban'

                    elif df['pop_density'].loc[i] >= 50 and df['pop_density'].loc[i] <= 500:

                        df['geotype'].loc[i] = 'rural'

                    else:

                        df['geotype'].loc[i] = 'remote'
                        
                df = df[['iso3', 'GID_1', 'from', 'to', 'length', 'population', 
                        'area', 'adoption_scenario', 'adoption_value', 'pop_density', 
                        'geotype', 'users_area_sqkm', 'revenue_per_area', 'geometry']]

                merged_dataframe = pd.concat([merged_dataframe, df], ignore_index = True)

        fileout = '{}_users_results.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'demand')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)

        merged_dataframe.to_csv(path_out, index = False)
    

    return None


for idx, country in countries.iterrows():
        
    if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    #if not country['iso3'] == 'KEN':
        
        continue 

    #generate_fiber_line_csv(countries['iso3'].loc[idx])
    fiber_users(countries['iso3'].loc[idx])