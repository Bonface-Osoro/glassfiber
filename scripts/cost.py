import configparser
import os
import warnings
import pandas as pd
import numpy as np
import geopandas as gpd
from glassfibre.inputs import parameters
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'latin-1')

def cost_model(length, unit):
    """
    Calculate the total cost of ownership(TCO)
    in US$.

    Parameters
    ----------
    length : float.
        Length of fiber between two nodes.
    unit : int.
        Number of fiber nodes.

    Returns
    -------
    total_cost_ownership : float
            The total cost of ownership.
    """
    for key, item in parameters.items():

        capex = (item['dslam'] + item['civil'] 
                 + (item['transportation']) 
                 + (item['installation'] * length)
                 + (item['rpu'] * unit) 
                 + (item['mdf_unit'] * unit))
        
        opex = (item['rent'] + item['staff'] 
                + item['power'] + item['regulatory'] 
                + item['customer'] + item['other_costs'])
        year_costs = []

        for time in np.arange(1, item['assessment_period']):  

            yearly_opex = opex / (((item['discount_rate'] / 100) + 1) ** time)
            year_costs.append(yearly_opex)

        total_cost_ownership = capex + sum(year_costs) + opex


        return total_cost_ownership


def demand(iso3):
    """
    This function generate demand results 
    for each country.
    
    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating demand results for {} csv'.format(iso3))
    merged_shapefile = gpd.GeoDataFrame()
    line_folder = os.path.join(DATA_RESULTS, iso3, 'gid_points')
    pop_folder = os.path.join(DATA_RESULTS, iso3, 'population', 
                 '{}_population_results.csv'.format(iso3))

    df = pd.read_csv(pop_folder)

    for file_name in os.listdir(line_folder):

        if file_name.endswith('.shp'):

            file_path = os.path.join(line_folder, file_name)
            shapefile = gpd.read_file(file_path)
            shapefile = shapefile.to_crs(crs = 3857) 
            merged_shapefile = pd.concat([merged_shapefile, shapefile], 
                               ignore_index = True)
    try:
        merged_gdf = merged_shapefile.merge(df, left_on = 'GID_2', 
                     right_on = 'GID_1')

    except:

        merged_gdf = merged_shapefile.merge(df, left_on ='GID_1', 
                     right_on='GID_1')
    merged_gdf = merged_gdf.drop(columns = ['geometry_x', 
                 'latitude', 'longitude', 'region'])
    merged_gdf = merged_gdf.rename(columns={'geometry_y': 'geometry'})   
    merged_gdf = merged_gdf[['iso3', 'GID_1','population', 'area', 
                 'geometry']]
    merged_gdf[['area']] = merged_gdf[['area']].round(4)
    df = merged_gdf
    df['pop_density'] = ''
    for i in range(len(df)):

        df['pop_density'].loc[i] = ((df['population'].loc[i])
            / (df['area'].loc[i]))
    
    for idx, country in countries.iterrows():
            
        if not country['iso3'] == iso3:

            continue

        arpu = countries['arpu'].loc[idx]
        adoption_low = round(countries['adoption_low'].loc[idx], 0)
        df[['low', 'baseline', 'high']] = ''
        df['low_adoption'] = 'low'
        df['baseline_adoption'] = 'baseline'
        df['high_adoption'] = 'high'
        df = pd.melt(df, id_vars = ['iso3', 'GID_1', 'area', 'pop_density', 
                'geometry'], var_name = 'adoption_scenario', 
                value_vars = ['low', 'baseline', 'high'])
        df = df.drop(columns = ['value'])
        df[['adoption_value', 'users_area_sqkm', 'revenue_per_area', 'geotype']] = ''

        for i in range(len(df)):

            if df['adoption_scenario'].loc[i] == 'low':
                
                df['adoption_value'].loc[i] = round((adoption_low / 100), 4)
                df['users_area_sqkm'].loc[i] = (df['adoption_value'].loc[i] 
                                                * df['pop_density'].loc[i])
                df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                 * (arpu))
                
            elif df['adoption_scenario'].loc[i] == 'baseline':

                df['adoption_value'].loc[i] = round((adoption_low / 100) + (0.1 
                                              * ((adoption_low / 100))), 4)
                df['users_area_sqkm'].loc[i] = (df['adoption_value'].loc[i] 
                                                * df['pop_density'].loc[i])
                df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                 * (arpu))
                
            else:

                df['adoption_value'].loc[i] = round((adoption_low / 100) + (0.2 
                                              * ((adoption_low / 100))), 4)
                df['users_area_sqkm'].loc[i] = (df['adoption_value'].loc[i] 
                                                * df['pop_density'].loc[i])
                df['revenue_per_area'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                 * (arpu))

            if df['pop_density'].loc[i] >= 1000:

                df['geotype'].loc[i] = 'urban'
            
            elif df['pop_density'].loc[i] >= 500 and df['pop_density'].loc[i] <= 1000:
                
                df['geotype'].loc[i] = 'suburban'

            elif df['pop_density'].loc[i] >= 50 and df['pop_density'].loc[i] <= 500:

                df['geotype'].loc[i] = 'rural'

            else:

                df['geotype'].loc[i] = 'remote'
                
        df = df[['iso3', 'GID_1', 'area', 'adoption_scenario',
                 'adoption_value', 'pop_density', 'geotype', 'users_area_sqkm', 
                 'revenue_per_area', 'geometry']]

    fileout = '{}_demand_results.csv'.format(iso3)
    folder_out = os.path.join(DATA_RESULTS, iso3, 'demand')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)

    df.to_csv(path_out, index = False)
    

    return None            


def fiber_supply(iso3):
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
            
        if not country['iso3'] == 'KEN':

            continue

        for file_name in os.listdir(line_folder):

            if file_name.endswith('_users_results.csv'):

                file_path = os.path.join(line_folder, file_name)
                df = pd.read_csv(file_path)
                df[['tco', 'tco_per_user']] = ''
                unit = df['to'].nunique()
                df_length = df.groupby(['GID_1'])['length'].mean().reset_index()
                total_length = (df_length['length'].sum()) / 1000
                
                tco = cost_model(total_length, unit)

                for i in range(len(df)):

                    df['tco'].loc[i] = tco
                    df['tco_per_user'].loc[i] = ((df['tco'].loc[i]) / 
                                    (df['users_area_sqkm'].loc[i]))

                df = df[['iso3', 'GID_1', 'from', 'to', 'length', 'population', 
                        'area', 'adoption_scenario', 'adoption_value', 'pop_density', 
                        'geotype', 'users_area_sqkm', 'revenue_per_area', 'tco', 
                        'tco_per_user', 'geometry']]
                
                merged_dataframe = pd.concat([merged_dataframe, df], ignore_index = True)

        fileout = '{}_supply_results.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'supply')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)

        merged_dataframe.to_csv(path_out, index = False)
    

    return None


if __name__ == '__main__':

    for idx, country in countries.iterrows():
            
        if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
            
        #if not country['iso3'] == 'CPV':
            
            continue 

        demand(countries['iso3'].loc[idx])
        #fiber_supply(countries['iso3'].loc[idx])