import configparser
import os
import warnings
import pyproj
import tqdm
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString
from functools import partial
from shapely.ops import transform
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
DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
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

            yearly_opex = opex / (((item['discount_rate_percent'] / 100) + 1) 
                                  ** time)
            
            year_costs.append(yearly_opex)

        total_cost_ownership = capex + sum(year_costs) + opex


        return total_cost_ownership


def baseline_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions
    """
    print('Processing TCO and emissions for {}'.format(iso3))
    file = os.path.join(DATA_PROCESSED, iso3, 'network_existing', 
                        '{}_core_edges_existing.shp'.format(iso3))
    
    file_2 = os.path.join(DATA_PROCESSED, iso3, 'network_existing', 
                        '{}_core_nodes_existing.shp'.format(iso3))
    
    if os.path.exists(file) and os.path.exists(file_2):

        file_3 = os.path.join(DATA_RESULTS, iso3, 'population', 
                            '{}_population_results.csv'.format(iso3))
        
        df = gpd.read_file(file)
        df1 = gpd.read_file(file_2)
        df2 = pd.read_csv(file_3)
        df2.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
        df2 = df2[['GID_2', 'area']]
        df['length'] = ''
        df1[['tco', 'tco_per_user', 'pop_density', 'users_area_sqkm']] = ''
        for i in range(len(df)):

            line = LineString(df['geometry'].loc[i])
            #1 degree = 111.32km
            length_km = (line.length) * 111.32
            df['length'].loc[i] = length_km

        total_length = df['length'].sum()
        units = df1['id'].nunique()
        df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
            'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
            'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
            'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
            'emissions_kg_per_subscriber', 'strategy']] = ''
        lca_mfg = lca_manufacturing()
        lca_eot = lca_eolt()
        lca_tran = lca_trans()
        lca_ops = lca_operations()
        
        try:

            df1 = pd.merge(df1, df2, on = 'GID_2')

        except:

            df1.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
            df1 = pd.merge(df1, df2, on = 'GID_2')

        for idx, country in countries.iterrows():
                
            if not country['iso3'] == iso3:

                continue

            arpu = countries['arpu'].loc[idx]
            adoption_low = round(countries['adoption_low'].loc[idx], 0)

            for i in range(len(df1)):

                df1['tco'].loc[i] = cost_model(total_length, units)
                
                df1['pop_density'].loc[i] = (df1['population'].loc[i] / 
                                            df1['area'].loc[i])
                
                df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]) * 
                                                (adoption_low / 100))
                
                df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                            / (df1['users_area_sqkm'].loc[i])) 
                                            / units)

                ################# LCA MANUFACTURING PHASE ########################
                df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                    * (total_length))
                df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * units)
                df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * units)
                df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * units)
                df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                    * units)
                df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * units)
                df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                                + df1['aluminium_mfg_ghg'].loc[i] 
                                                + df1['steel_iron_mfg_ghg'].loc[i] 
                                                + df1['plastics_mfg_ghg'].loc[i] 
                                                + df1['other_metals_mfg_ghg'].loc[i] 
                                                + df1['concrete_mfg_ghg'].loc[i])
                
                ####################### LCA TRANSPORTATION PHASE ###################
                df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                    * units)

                ####################### LCA OPERATIONS PHASE #######################
                df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * units) 
                                        + ((lca_ops['base_station_power_kwh'] * 
                                            units) 
                                        / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                        * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                            units) 
                                        / df1['users_area_sqkm'].loc[i]))) * 
                                        0.19338) 
                ####################### LCA END OF LIFE TREATMENT PHASE ############
                df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                    * total_length)
                df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                    units)
                df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                    units)
                df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * units)
                df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                    * units)
                df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * units)
                df1['total_eolt_ghg_kg'].loc[i] = (df1['optic_fiber_eolt_ghg'].loc[i] 
                                                + df1['aluminium_eolt_ghg'].loc[i] 
                                                + df1['steel_iron_eolt_ghg'].loc[i] 
                                                + df1['plastics_eolt_ghg'].loc[i] 
                                                + df1['other_metals_eolt_ghg'].loc[i] 
                                                + df1['concrete_eolt_ghg'].loc[i])
                
                df1['total_ghg_emissions_kg'].loc[i] = (df1['total_mfg_ghg_kg'].loc[i] 
                                                + df1['total_trans_ghg_kg'].loc[i] 
                                                + df1['total_ops_ghg_kg'].loc[i] 
                                                + df1['total_eolt_ghg_kg'].loc[i])
                df1['emissions_kg_per_subscriber'].loc[i] = (
                    df1['total_ghg_emissions_kg'].loc[i] / 
                    df1['users_area_sqkm'].loc[i]) / units
                
                df1['strategy'].loc[i] = 'baseline'
        
        df1.rename(columns = {'GID_0': 'iso3'}, inplace = True)
        totat_ghg = df1[['iso3', 'GID_2', 'population', 'pop_density', 'users_area_sqkm', 
                    'area', 'total_mfg_ghg_kg', 'total_trans_ghg_kg', 
                    'total_ops_ghg_kg', 'total_eolt_ghg_kg', 
                    'total_ghg_emissions_kg', 'emissions_kg_per_subscriber', 
                    'strategy']]
        
        country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                    'emissions_kg_per_subscriber', 'strategy']]
        
        ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()

        country_totat_ghg = pd.DataFrame({'iso3': 
                            [country_totat_ghg['iso3'].iloc[0]], 
                            'total_ghg_emissions_kg': [country_totat_ghg[
                            'total_ghg_emissions_kg'].iloc[0]], 
                            'emissions_kg_per_subscriber': [ghg_avg], 
                            'strategy': [country_totat_ghg['strategy'].iloc[0]]})

        df3 = df1[['iso3', 'GID_2', 'pop_density', 'users_area_sqkm', 
                'optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
                'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
                'total_mfg_ghg_kg', 'strategy']]
        
        total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_2', 'pop_density', 
                'users_area_sqkm', 'total_mfg_ghg_kg', 'strategy'], value_vars = 
                ['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 
                'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 'other_metals_mfg_ghg', 
                'concrete_mfg_ghg',], var_name = 'emission_category', 
                value_name = 'lca_phase_ghg_kg')
        
        df4 = df1[['iso3', 'GID_2', 'pop_density', 'users_area_sqkm', 
                'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
                'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg', 
                'total_eolt_ghg_kg', 'strategy']]
        
        total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_2', 'pop_density',
            'users_area_sqkm', 'total_eolt_ghg_kg', 'strategy'], value_vars = 
            ['optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
            'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg',], 
            var_name = 'emission_category', value_name = 'lca_phase_ghg_kg')
        
        total_tco = df1[['iso3', 'GID_2', 'population', 'pop_density', 
                         'users_area_sqkm', 'tco', 'tco_per_user', 'strategy']]
        fileout = '{}_baseline_emission_results.csv'.format(iso3)
        fileout1 = '{}_baseline_mfg_emission_results.csv'.format(iso3)
        fileout2 = '{}_baseline_eolt_emission_results.csv'.format(iso3)
        fileout3 = '{}_baseline_tco_results.csv'.format(iso3)
        fileout4 = '{}_country_baseline_emission.csv'.format(iso3)

        folder_out = os.path.join(DATA_RESULTS, iso3, 'emissions')
        folder_out1 = os.path.join(DATA_RESULTS, iso3, 'supply')
        folder_out2 = os.path.join(DATA_RESULTS, iso3, 'summary')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        path_out1 = os.path.join(folder_out, fileout1)
        path_out2 = os.path.join(folder_out, fileout2)
        path_out3 = os.path.join(folder_out1, fileout3)
        path_out4 = os.path.join(folder_out2, fileout4)

        totat_ghg.to_csv(path_out, index = False)
        total_mfg.to_csv(path_out1, index = False)
        total_eolt.to_csv(path_out2, index = False)
        total_tco.to_csv(path_out3, index = False)
        country_totat_ghg.to_csv(path_out4, index = False)

    else:

        print('No Existing fiber data available')


    return None


def local_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions for local fiber nodes
    """
    print('Processing TCO and emissions for {}'.format(iso3))
    file = os.path.join(DATA_PROCESSED, iso3, 'network', 
                            '{}_core_edges.shp'.format(iso3))
    file_2 = os.path.join(DATA_PROCESSED, iso3, 'network', 'new_nodes.shp')
        
    if os.path.exists(file) and os.path.exists(file_2):
        
        df = gpd.read_file(file)
        df1 = gpd.read_file(file_2)

    else:

        file_2 = os.path.join(DATA_PROCESSED, iso3, 'network', 'regional_nodes.shp')
        file = os.path.join(DATA_PROCESSED, iso3, 'network', 'regional_edges.shp')
        
        if not os.path.exists(file):

            file = os.path.join(DATA_PROCESSED, iso3, 'network', '{}_core_edges.shp'.format(iso3))
            
        df = gpd.read_file(file)
        df1 = gpd.read_file(file_2)
    
    file_3 = os.path.join(DATA_RESULTS, iso3, 'population', 
                        '{}_population_results.csv'.format(iso3))
    df2 = pd.read_csv(file_3)
    df2.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
    df2 = df2[['GID_2', 'area']]
    df['length'] = ''
    df1[['tco', 'tco_per_user', 'pop_density', 'users_area_sqkm']] = ''
    
    for i in range(len(df)):

        line = LineString(df['geometry'].loc[i])
        #1 degree = 111.32km
        length_km = (line.length) * 111.32
        df['length'].loc[i] = length_km

    total_length = df['length'].sum()
    units = len(df1)
    df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
        'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
        'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
        'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
        'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
        'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
        'emissions_kg_per_subscriber', 'strategy']] = ''
    lca_mfg = lca_manufacturing()
    lca_eot = lca_eolt()
    lca_tran = lca_trans()
    lca_ops = lca_operations()
    
    try:
        
        df1 = pd.merge(df1, df2, on = 'GID_2')

    except:
        
        df1.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
        df1 = pd.merge(df1, df2, on = 'GID_2')
    df1.rename(columns = {'value': 'population'}, inplace = True)

    for idx, country in countries.iterrows():
            
        if not country['iso3'] == iso3:

            continue

        arpu = countries['arpu'].loc[idx]
        adoption_low = round(countries['adoption_low'].loc[idx], 0)
        df1['iso3'] = ''
        
        for i in range(len(df1)):
            
            df1['iso3'].loc[i] = iso3

            df1['tco'].loc[i] = cost_model(total_length, units)
            
            df1['pop_density'].loc[i] = (df1['population'].loc[i] / 
                                        df1['area'].loc[i])
            
            df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]) * 
                                            (adoption_low / 100))
            
            df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) 
                                        / units)

            ################# LCA MANUFACTURING PHASE ########################
            df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                * (total_length))
            df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * units)
            df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * units)
            df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * units)
            df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                * units)
            df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * units)
            df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                            + df1['aluminium_mfg_ghg'].loc[i] 
                                            + df1['steel_iron_mfg_ghg'].loc[i] 
                                            + df1['plastics_mfg_ghg'].loc[i] 
                                            + df1['other_metals_mfg_ghg'].loc[i] 
                                            + df1['concrete_mfg_ghg'].loc[i])
            
            ####################### LCA TRANSPORTATION PHASE ###################
            df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                * units)

            ####################### LCA OPERATIONS PHASE #######################
            df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * units) 
                                    + ((lca_ops['base_station_power_kwh'] * 
                                        units) 
                                    / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                    * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                        units) 
                                    / df1['users_area_sqkm'].loc[i]))) * 
                                    0.19338) 
            ####################### LCA END OF LIFE TREATMENT PHASE ############
            df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                * total_length)
            df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                units)
            df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                units)
            df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * units)
            df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                * units)
            df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * units)
            df1['total_eolt_ghg_kg'].loc[i] = (df1['optic_fiber_eolt_ghg'].loc[i] 
                                            + df1['aluminium_eolt_ghg'].loc[i] 
                                            + df1['steel_iron_eolt_ghg'].loc[i] 
                                            + df1['plastics_eolt_ghg'].loc[i] 
                                            + df1['other_metals_eolt_ghg'].loc[i] 
                                            + df1['concrete_eolt_ghg'].loc[i])
            
            df1['total_ghg_emissions_kg'].loc[i] = (df1['total_mfg_ghg_kg'].loc[i] 
                                            + df1['total_trans_ghg_kg'].loc[i] 
                                            + df1['total_ops_ghg_kg'].loc[i] 
                                            + df1['total_eolt_ghg_kg'].loc[i])
            df1['emissions_kg_per_subscriber'].loc[i] = (
                df1['total_ghg_emissions_kg'].loc[i] / 
                df1['users_area_sqkm'].loc[i]) / units
            
            df1['strategy'].loc[i] = 'local'

    df1.rename(columns = {'GID_0': 'iso3'}, inplace = True)
    totat_ghg = df1[['iso3', 'GID_2', 'population', 'pop_density', 
                'users_area_sqkm', 'area', 'total_mfg_ghg_kg', 
                'total_trans_ghg_kg', 'total_ops_ghg_kg', 
                'total_eolt_ghg_kg', 'total_ghg_emissions_kg', 
                'emissions_kg_per_subscriber', 'strategy']]
    
    country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                'emissions_kg_per_subscriber', 'strategy']]
    
    ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()

    country_totat_ghg = pd.DataFrame({'iso3': 
                        [country_totat_ghg['iso3'].iloc[0]], 
                        'total_ghg_emissions_kg': [country_totat_ghg[
                        'total_ghg_emissions_kg'].iloc[0]], 
                        'emissions_kg_per_subscriber': [ghg_avg], 
                        'strategy': [country_totat_ghg['strategy'].iloc[0]]})

    df3 = df1[['iso3', 'GID_2', 'pop_density', 'users_area_sqkm', 
            'optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'strategy']]
    
    total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_2', 'pop_density', 
            'users_area_sqkm', 'total_mfg_ghg_kg', 'strategy'], value_vars = 
            ['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 
            'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 'other_metals_mfg_ghg', 
            'concrete_mfg_ghg',], var_name = 'emission_category', 
            value_name = 'lca_phase_ghg_kg')
    
    df4 = df1[['iso3', 'GID_2', 'pop_density', 'users_area_sqkm', 
            'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
            'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg', 
            'total_eolt_ghg_kg', 'strategy']]
    
    total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_2', 'pop_density',
        'users_area_sqkm', 'total_eolt_ghg_kg', 'strategy'], value_vars = 
        ['optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
        'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg',], 
        var_name = 'emission_category', value_name = 'lca_phase_ghg_kg')
    
    total_tco = df1[['iso3', 'GID_2', 'population', 'pop_density', 
                    'users_area_sqkm', 'tco', 'tco_per_user', 'strategy']]
    fileout = '{}_local_emission_results.csv'.format(iso3)
    fileout1 = '{}_local_mfg_emission_results.csv'.format(iso3)
    fileout2 = '{}_local_eolt_emission_results.csv'.format(iso3)
    fileout3 = '{}_local_tco_results.csv'.format(iso3)
    fileout4 = '{}_country_local_emission.csv'.format(iso3)

    folder_out = os.path.join(DATA_RESULTS, iso3, 'emissions')
    folder_out1 = os.path.join(DATA_RESULTS, iso3, 'supply')
    folder_out2 = os.path.join(DATA_RESULTS, iso3, 'summary')
    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    path_out1 = os.path.join(folder_out, fileout1)
    path_out2 = os.path.join(folder_out, fileout2)
    path_out3 = os.path.join(folder_out1, fileout3)
    path_out4 = os.path.join(folder_out2, fileout4)

    totat_ghg.to_csv(path_out, index = False)
    total_mfg.to_csv(path_out1, index = False)
    total_eolt.to_csv(path_out2, index = False)
    total_tco.to_csv(path_out3, index = False)
    country_totat_ghg.to_csv(path_out4, index = False)


    return None


def regional_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions for regionalfiber nodes
    """
    print('Processing regional TCO and emissions for {}'.format(iso3))
    
    file = os.path.join(DATA_PROCESSED, iso3, 'regions', 
                        'regions_1_{}.shp'.format(iso3))
    
    file_1 = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 
                        'agglomerations.csv')
    
    file_2 = os.path.join(DATA_RESULTS, iso3, 'country_lines', 
                            '{}.shp'.format(iso3))
    
    df = gpd.read_file(file)
    df = df[['GID_1', 'geometry']]
    df[['area', 'pop_density', 'users_area_sqkm', 'tco', 'tco_per_user']] = ''
    
    df1 = pd.read_csv(file_1)
    df1 = df1.groupby(['GID_1'])['population'].sum().reset_index()

    df = pd.merge(df, df1, on = 'GID_1')
    
    for i in range(len(df)):

        df['area'].loc[i] = (df['geometry'].loc[i].area) * 12309
        df['pop_density'].loc[i] = ((df['population'].loc[i]) 
                                    / (df['area'].loc[i]))
        
    df2 = gpd.read_file(file_2)
    df2['length'] =  ''
    for i in range(len(df2)):

        line = LineString(df2['geometry'].loc[i])
        length_km = (line.length) * 111.32
        df2['length'].loc[i] = length_km
    
    df2 = df2[['GID_1', 'length']]

    df1 = pd.merge(df, df2, on = 'GID_1')
    total_length = df1['length'].sum()
    units = (len(df1))

    df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
        'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
        'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
        'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
        'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
        'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
        'emissions_kg_per_subscriber', 'strategy']] = ''
    
    lca_mfg = lca_manufacturing()
    lca_eot = lca_eolt()
    lca_tran = lca_trans()
    lca_ops = lca_operations()

    for idx, country in countries.iterrows():
            
        if not country['iso3'] == iso3:

            continue

        arpu = countries['arpu'].loc[idx]
        adoption_low = round(countries['adoption_low'].loc[idx], 0)
        df1['iso3'] = ''

        for i in range(len(df1)):
            
            df1['iso3'].loc[i] = iso3

            df1['tco'].loc[i] = cost_model(total_length, units)
            
            df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]) * 
                                            (adoption_low / 100))
            
            df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) 
                                        / units)
            ################# LCA MANUFACTURING PHASE ########################
            df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                * (total_length))
            df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * units)
            df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * units)
            df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * units)
            df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                * units)
            df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * units)
            df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                            + df1['aluminium_mfg_ghg'].loc[i] 
                                            + df1['steel_iron_mfg_ghg'].loc[i] 
                                            + df1['plastics_mfg_ghg'].loc[i] 
                                            + df1['other_metals_mfg_ghg'].loc[i] 
                                            + df1['concrete_mfg_ghg'].loc[i])
            
            ####################### LCA TRANSPORTATION PHASE ###################
            df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                * units)

            ####################### LCA OPERATIONS PHASE #######################
            df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * units) 
                                    + ((lca_ops['base_station_power_kwh'] * 
                                        units) 
                                    / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                    * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                        units) 
                                    / df1['users_area_sqkm'].loc[i]))) * 
                                    0.19338) 
            ####################### LCA END OF LIFE TREATMENT PHASE ############
            df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                * total_length)
            df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                units)
            df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                units)
            df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * units)
            df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                * units)
            df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * units)
            df1['total_eolt_ghg_kg'].loc[i] = (df1['optic_fiber_eolt_ghg'].loc[i] 
                                            + df1['aluminium_eolt_ghg'].loc[i] 
                                            + df1['steel_iron_eolt_ghg'].loc[i] 
                                            + df1['plastics_eolt_ghg'].loc[i] 
                                            + df1['other_metals_eolt_ghg'].loc[i] 
                                            + df1['concrete_eolt_ghg'].loc[i])
            
            df1['total_ghg_emissions_kg'].loc[i] = (df1['total_mfg_ghg_kg'].loc[i] 
                                            + df1['total_trans_ghg_kg'].loc[i] 
                                            + df1['total_ops_ghg_kg'].loc[i] 
                                            + df1['total_eolt_ghg_kg'].loc[i])
            df1['emissions_kg_per_subscriber'].loc[i] = (
                df1['total_ghg_emissions_kg'].loc[i] / 
                df1['users_area_sqkm'].loc[i]) / units
            
            df1['strategy'].loc[i] = 'regional'
    
    totat_ghg = df1[['iso3', 'GID_1', 'population', 'pop_density', 
                'users_area_sqkm', 'area', 'total_mfg_ghg_kg', 
                'total_trans_ghg_kg', 'total_ops_ghg_kg', 
                'total_eolt_ghg_kg', 'total_ghg_emissions_kg', 
                'emissions_kg_per_subscriber', 'strategy']]
    
    country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                'emissions_kg_per_subscriber', 'strategy']]
    
    ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()

    country_totat_ghg = pd.DataFrame({'iso3': 
                        [country_totat_ghg['iso3'].iloc[0]], 
                        'total_ghg_emissions_kg': [country_totat_ghg[
                        'total_ghg_emissions_kg'].iloc[0]], 
                        'emissions_kg_per_subscriber': [ghg_avg], 
                        'strategy': [country_totat_ghg['strategy'].iloc[0]]})

    df3 = df1[['iso3', 'GID_1', 'pop_density', 'users_area_sqkm', 
            'optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'strategy']]
    
    total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_1', 'pop_density', 
            'users_area_sqkm', 'total_mfg_ghg_kg', 'strategy'], value_vars = 
            ['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 
            'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 'other_metals_mfg_ghg', 
            'concrete_mfg_ghg',], var_name = 'emission_category', 
            value_name = 'lca_phase_ghg_kg')
    
    df4 = df1[['iso3', 'GID_1', 'pop_density', 'users_area_sqkm', 
            'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
            'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg', 
            'total_eolt_ghg_kg', 'strategy']]
    
    total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_1', 'pop_density',
        'users_area_sqkm', 'total_eolt_ghg_kg', 'strategy'], value_vars = 
        ['optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
        'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg',], 
        var_name = 'emission_category', value_name = 'lca_phase_ghg_kg')
    
    total_tco = df1[['iso3', 'GID_1', 'population', 'pop_density', 
                    'users_area_sqkm', 'tco', 'tco_per_user', 'strategy']]
    fileout = '{}_regional_emission_results.csv'.format(iso3)
    fileout1 = '{}_regional_mfg_emission_results.csv'.format(iso3)
    fileout2 = '{}_regional_eolt_emission_results.csv'.format(iso3)
    fileout3 = '{}_regional_tco_results.csv'.format(iso3)
    fileout4 = '{}_regional_emission.csv'.format(iso3)

    folder_out = os.path.join(DATA_RESULTS, iso3, 'emissions')
    folder_out1 = os.path.join(DATA_RESULTS, iso3, 'supply')
    folder_out2 = os.path.join(DATA_RESULTS, iso3, 'summary')
    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    path_out1 = os.path.join(folder_out, fileout1)
    path_out2 = os.path.join(folder_out, fileout2)
    path_out3 = os.path.join(folder_out1, fileout3)
    path_out4 = os.path.join(folder_out2, fileout4)

    totat_ghg.to_csv(path_out, index = False)
    total_mfg.to_csv(path_out1, index = False)
    total_eolt.to_csv(path_out2, index = False)
    total_tco.to_csv(path_out3, index = False)
    country_totat_ghg.to_csv(path_out4, index = False)
    
    
    return None