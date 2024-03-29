import configparser
import os
import warnings
import pandas as pd
import numpy as np
import geopandas as gpd
import tqdm
from glassfibre.inputs import parameters
from glassfibre.preprocessing import (
    lca_manufacturing, lca_eolt, 
    lca_trans, 
    lca_operations)

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'utf-8-sig')


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
        
        capex = (item['dslam_usd'] + item['civil_usd'] 
                 + (item['transportation_usd']) 
                 + (item['installation_usd'] * length)
                 + (item['rpu_usd'] * unit) 
                 + (item['mdf_unit_usd'] * unit))
        
        opex = (item['rent_usd'] + item['staff_usd'] 
                + item['power_usd'] + item['regulatory_usd'] 
                + item['customer_usd'] + item['other_costs_usd'])
        year_costs = []

        for time in np.arange(1, item['assessment_period_year']):  

            yearly_opex = opex / (((item['discount_rate_percent'] / 100) + 1) ** time)
            year_costs.append(yearly_opex)

        total_cost_ownership = capex + sum(year_costs) + opex


        return total_cost_ownership


def capacity_per_user(monthly_traffic, traffic_hour):
    """
    This function calculate the 
    number of Mbps required per 
    user (Rt) in time (t).

    30 Monthly traffic in Gigabytes 
       per month per user
    1024 x 8  Conversion of Gigabytes to bits
    30     Number of days in a month (30)
    3600  Seconds in hour

    Parameters
    ----------
    traffic_hour : int.
        Number of days in a month.

    Returns
    -------
    monthly_traffic : int
        Monthly traffic per user in GB
    mbps_per_user : float
        Capacity per user Mbps/user.
    """ 
    mbps_per_user = (monthly_traffic * 
                    1024 * (1 / 30) * 
                    (traffic_hour / 100) * 
                    (1 / 3600))
    

    return mbps_per_user


def ssa_summary(iso3):
    """
    This function calculate 
    country geotype characteristics.
    
    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating geotype characteristics for {}.'.format(iso3))
    df_merged = gpd.GeoDataFrame()
    pop_folder = os.path.join(DATA_RESULTS, iso3, 'population')
    
    for root, _, files in os.walk(pop_folder):

        for file in files:

            if file.endswith('.csv'):
                
                file_path = os.path.join(pop_folder, '{}_population_results.csv'.format(iso3))
                df = pd.read_csv(file_path)
                df = df[['iso3', 'area', 'population']]
                df[['pop_density', 'geotype']] = ''
                for i in range(len(df)):

                    df['pop_density'].loc[i] = ((df['population'].loc[i])
                        / (df['area'].loc[i]))
                    
                    if df['pop_density'].loc[i] >= 1000:

                        df['geotype'].loc[i] = 'urban'
                    
                    elif df['pop_density'].loc[i] >= 500 and df['pop_density'].loc[i] <= 1000:
                        
                        df['geotype'].loc[i] = 'suburban'

                    elif df['pop_density'].loc[i] >= 50 and df['pop_density'].loc[i] <= 500:

                        df['geotype'].loc[i] = 'rural'

                    else:

                        df['geotype'].loc[i] = 'remote'

            df_merged = pd.concat([df_merged, df], ignore_index = True)
            
            average_pop = df_merged.groupby(['iso3', 'geotype']
                          )['population'].sum().reset_index()
            
            average_area = df_merged.groupby(['iso3', 'geotype']
                           )['area'].sum().reset_index()
    
    fileout = '{}_geotype_population.csv'.format(iso3)
    fileout_1 = '{}_geotype_total_area.csv'.format(iso3)
    folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    path_out_1 = os.path.join(folder_out, fileout_1)

    average_pop.to_csv(path_out, index = False) 
    average_area.to_csv(path_out_1, index = False)
    

    return None  


def capacity_user(iso3):
    """
    This function calculate 
    total demand per km^2.
    
    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating demand values {}.'.format(iso3))
    df_merged = gpd.GeoDataFrame()
    demand_folder = os.path.join(DATA_RESULTS, iso3, 'demand')
    
    for root, _, files in os.walk(demand_folder):

        for file in files:

            if file.endswith('.csv'):
                
                file_path = os.path.join(demand_folder, 
                            '{}_demand_results.csv'.format(iso3))
                
                df = pd.read_csv(file_path)
                df = df[['iso3', 'GID_1', 'area', 
                         'adoption_scenario', 'pop_density', 
                         'geotype', 'users_area_sqkm']]
                
                df[['monthly_traffic', 'speed_mbps_per_user', 'demand_mbps_sqkm']] = ''
                monthly_traffics = [10, 20, 30, 40]

                for idx, country in countries.iterrows():
                        
                    if not country['iso3'] == iso3:

                        continue

                    traffic = countries['traffic_hour'].loc[idx]

                    for monthly_traffic in monthly_traffics:

                        for i in range(len(df)):
                            
                            df['monthly_traffic'].loc[i] = monthly_traffic
                            df['speed_mbps_per_user'].loc[i] = capacity_per_user(
                                                        monthly_traffic, traffic)
                            df['demand_mbps_sqkm'].loc[i] = ((df['users_area_sqkm'].loc[i]) 
                                                            * (df['speed_mbps_per_user'].loc[i])) 

                        df_merged = pd.concat([df_merged, df], ignore_index = True)   
    
    fileout = '{}_demand_user.csv'.format(iso3)
    folder_out = os.path.join(DATA_RESULTS, iso3, 'demand')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)

    df_merged.to_csv(path_out, index = False)
    

    return None


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


if __name__ == '__main__':

    for idx, country in countries.iterrows():
            
        if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
            
        #if not country['iso3'] == 'RWA':
            
            continue 
        demand(countries['iso3'].loc[idx])
        capacity_user(countries['iso3'].loc[idx])
        ssa_summary(countries['iso3'].loc[idx])