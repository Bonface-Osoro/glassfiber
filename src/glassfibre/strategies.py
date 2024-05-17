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
    file = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
    
    
    try:

        file_2 = os.path.join(file, '{}_fiber_existing.csv'.format(iso3))

        df1 = pd.read_csv(file_2)
        df1[['tco', 'tco_per_user', 'users_area_sqkm']] = ''

        df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
            'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
            'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
            'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
            'emissions_kg_per_subscriber', 'total_ssc_usd', 'ssc_per_user']] = ''
        lca_mfg = lca_manufacturing()
        lca_eot = lca_eolt()
        lca_tran = lca_trans()
        lca_ops = lca_operations()

        for idx, country in countries.iterrows():
                
            if not country['iso3'] == iso3:

                continue

            adoption_low = round(countries['adoption_low'].loc[idx], 0)

            for i in range(len(df1)):

                df1['tco'].loc[i] = cost_model(df1['length_km'].loc[i], 
                                               df1['nodes'].loc[i])
                
                df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]) * 
                                                (adoption_low / 100))
                
                df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                            / (df1['users_area_sqkm'].loc[i])))

                ################# LCA MANUFACTURING PHASE ########################
                df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                    * df1['length_km'].loc[i])
                df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * 
                                                   df1['nodes'].loc[i])
                df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * 
                                                  df1['nodes'].loc[i])
                df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * 
                                                  df1['nodes'].loc[i])
                df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                                + df1['aluminium_mfg_ghg'].loc[i] 
                                                + df1['steel_iron_mfg_ghg'].loc[i] 
                                                + df1['plastics_mfg_ghg'].loc[i] 
                                                + df1['other_metals_mfg_ghg'].loc[i] 
                                                + df1['concrete_mfg_ghg'].loc[i])
                
                ####################### LCA TRANSPORTATION PHASE ###################
                df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                    * df1['nodes'].loc[i])

                ####################### LCA OPERATIONS PHASE #######################
                df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * 
                                                    df1['nodes'].loc[i]) 
                                        + ((lca_ops['base_station_power_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                        * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / df1['users_area_sqkm'].loc[i]))) * 
                                        0.19338) 
                ####################### LCA END OF LIFE TREATMENT PHASE ############
                df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                    * df1['length_km'].loc[i])
                df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * 
                                                   df1['nodes'].loc[i])
                df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * 
                                                   df1['nodes'].loc[i])
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
                    df1['users_area_sqkm'].loc[i]) 
                
                df1['strategy'].loc[i] = 'baseline'
                df1['algorithm'].loc[i] = 'none'

                df1['total_ssc_usd'].loc[i] = (
                    df1['total_ghg_emissions_kg'].loc[i] / 1000) * 185
                
                df1['ssc_per_user'].loc[i] = (df1['total_ssc_usd'].loc[i] / 
                                              df1['users_area_sqkm'].loc[i])
        
        df1.rename(columns = {'GID_0': 'iso3'}, inplace = True)
        totat_ghg = df1[['iso3', 'users_area_sqkm', 'total_mfg_ghg_kg', 
                         'total_trans_ghg_kg', 'total_ops_ghg_kg', 
                         'total_eolt_ghg_kg', 'total_ghg_emissions_kg', 
                         'emissions_kg_per_subscriber', 'total_ssc_usd', 
                         'ssc_per_user', 'strategy', 'algorithm']]
        
        country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()
        scc_avg = country_totat_ghg['ssc_per_user'].mean()

        country_totat_ghg = pd.DataFrame({'iso3': 
                            [country_totat_ghg['iso3'].iloc[0]], 
                            'total_ghg_emissions_kg': [country_totat_ghg[
                            'total_ghg_emissions_kg'].iloc[0]], 
                            'emissions_kg_per_subscriber': [ghg_avg], 
                            'total_ssc_usd': [country_totat_ghg[
                            'total_ssc_usd'].iloc[0]],
                            'ssc_per_user': [scc_avg], 
                            'strategy': [country_totat_ghg['strategy'].iloc[0]],
                            'algorithm': [country_totat_ghg['algorithm'].iloc[0]]})

        df3 = df1[['iso3','users_area_sqkm', 'optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg', 'total_mfg_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_mfg = pd.melt(df3, id_vars = ['iso3', 'users_area_sqkm', 
                'total_mfg_ghg_kg', 'strategy', 'algorithm'], value_vars = 
                ['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 
                'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 'other_metals_mfg_ghg', 
                'concrete_mfg_ghg',], var_name = 'emission_category', 
                value_name = 'lca_phase_ghg_kg')
        
        df4 = df1[['iso3', 'users_area_sqkm', 'optic_fiber_eolt_ghg', 
                'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
                'other_metals_eolt_ghg', 'concrete_eolt_ghg', 
                'total_eolt_ghg_kg', 'strategy', 'algorithm']]
        
        total_eolt = pd.melt(df4, id_vars = ['iso3', 'users_area_sqkm', 
            'total_eolt_ghg_kg', 'strategy', 'algorithm'], value_vars = 
            ['optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
            'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg',], 
            var_name = 'emission_category', value_name = 'lca_phase_ghg_kg')
        
        total_tco = df1[['iso3', 'users_area_sqkm', 'tco', 'tco_per_user',
                          'strategy', 'algorithm']]
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

    except:

        print('No Existing fiber data available')


    return None


def local_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions for local fiber nodes
    """
    try:

        print('Processing TCO and emissions for {}'.format(iso3))
        file = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
            
        if os.path.exists(file):

            file_2 = os.path.join(file, '{}_fiber_access.csv'.format(iso3))
            df1 = gpd.read_file(file_2)

        df1[['tco', 'tco_per_user', 'users_area_sqkm', 'nodes']] = ''

        df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
            'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
            'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
            'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
            'emissions_kg_per_subscriber', 'total_ssc_usd', 'ssc_per_user', 
            'strategy', 'algorithm']] = ''
        
        lca_mfg = lca_manufacturing()
        lca_eot = lca_eolt()
        lca_tran = lca_trans()
        lca_ops = lca_operations()

        for idx, country in countries.iterrows():
                
            if not country['iso3'] == iso3:

                continue

            arpu = countries['arpu'].loc[idx]
            adoption_low = round(countries['adoption_low'].loc[idx], 0)

            df1['length_km'] = df1['length_km'].astype(float)
            df1['population'] = df1['population'].astype(float)

            for i in range(len(df1)):
                
                df1['iso3'].loc[i] = iso3

                df1['nodes'].loc[i] = 1

                df1['tco'].loc[i] = cost_model(df1['length_km'].loc[i], 
                                            df1['nodes'].loc[i])
                
                df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]))
                
                df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                            / (df1['users_area_sqkm'].loc[i])))

                ################# LCA MANUFACTURING PHASE ########################
                df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                    * (df1['length_km'].loc[i]))
                df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * df1['nodes'].loc[i])
                df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * df1['nodes'].loc[i])
                df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * 1)
                df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                    * 1)
                df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * 
                                                df1['nodes'].loc[i])
                df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                                + df1['aluminium_mfg_ghg'].loc[i] 
                                                + df1['steel_iron_mfg_ghg'].loc[i] 
                                                + df1['plastics_mfg_ghg'].loc[i] 
                                                + df1['other_metals_mfg_ghg'].loc[i] 
                                                + df1['concrete_mfg_ghg'].loc[i])
                
                ####################### LCA TRANSPORTATION PHASE ###################
                df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                    * df1['nodes'].loc[i])

                ####################### LCA OPERATIONS PHASE #######################
                df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * 1) 
                                        + ((lca_ops['base_station_power_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                        * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / df1['users_area_sqkm'].loc[i]))) * 
                                        0.19338) 
                ####################### LCA END OF LIFE TREATMENT PHASE ############
                df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                    * df1['length_km'].loc[i])
                df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * 
                                                df1['nodes'].loc[i])
                df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * 
                                                df1['nodes'].loc[i])
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
                    df1['users_area_sqkm'].loc[i])
                
                df1['strategy'].loc[i] = 'access'
                df1['algorithm'].loc[i] = 'Dijkstras'

                df1['total_ssc_usd'].loc[i] = (
                    df1['total_ghg_emissions_kg'].loc[i] / 1000) * 185
                
                df1['ssc_per_user'].loc[i] = (df1['total_ssc_usd'].loc[i] / 
                                              df1['users_area_sqkm'].loc[i])

        totat_ghg = df1[['iso3', 'GID_2', 'users_area_sqkm', 'total_mfg_ghg_kg', 
                    'total_trans_ghg_kg', 'total_ops_ghg_kg', 'total_eolt_ghg_kg', 
                    'total_ghg_emissions_kg', 'emissions_kg_per_subscriber', 
                    'total_ssc_usd', 'ssc_per_user', 'strategy', 'algorithm']]
        
        country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()
        scc_avg = country_totat_ghg['ssc_per_user'].mean()

        country_totat_ghg = pd.DataFrame({'iso3': 
                            [country_totat_ghg['iso3'].iloc[0]], 
                            'total_ghg_emissions_kg': [country_totat_ghg[
                            'total_ghg_emissions_kg'].iloc[0]], 
                            'emissions_kg_per_subscriber': [ghg_avg], 
                            'total_ssc_usd': [country_totat_ghg[
                            'total_ssc_usd'].iloc[0]],
                            'ssc_per_user': [scc_avg], 
                            'strategy': [country_totat_ghg['strategy'].iloc[0]],
                            'algorithm': [country_totat_ghg['algorithm'].iloc[0]]})

        df3 = df1[['iso3', 'GID_2', 'users_area_sqkm', 'optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg', 'total_mfg_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_2', 'users_area_sqkm', 
                'total_mfg_ghg_kg', 'strategy', 'algorithm'], 
                value_vars = ['optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg',], var_name = 
                'emission_category', value_name = 'lca_phase_ghg_kg')
        
        df4 = df1[['iso3', 'GID_2', 'users_area_sqkm', 'optic_fiber_eolt_ghg', 
                'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
                'other_metals_eolt_ghg', 'concrete_eolt_ghg', 'total_eolt_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_2', 'users_area_sqkm', 
            'total_eolt_ghg_kg', 'strategy', 'algorithm'], 
            value_vars = ['optic_fiber_eolt_ghg', 
            'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
            'other_metals_eolt_ghg', 'concrete_eolt_ghg',], var_name = 
            'emission_category', value_name = 'lca_phase_ghg_kg')
        
        total_tco = df1[['iso3', 'GID_2', 'population', 'users_area_sqkm', 'tco', 
                        'tco_per_user', 'strategy', 'algorithm']]
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

    except:

        pass

    return None


def regional_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions for regionalfiber nodes
    """
    print('Processing regional TCO and emissions for {}'.format(iso3))
    
    file = os.path.join(DATA_RESULTS, iso3, 'fiber_design', 
                        '{}_fiber_regional.csv'.format(iso3))
    
    if os.path.exists(file):

        df1 = pd.read_csv(file)
        df1[['users_area_sqkm', 'tco', 'tco_per_user', 'nodes']] = ''

        df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
            'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
            'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
            'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
            'emissions_kg_per_subscriber', 'total_ssc_usd', 'ssc_per_user', 
            'algorithm']] = ''
        
        lca_mfg = lca_manufacturing()
        lca_eot = lca_eolt()
        lca_tran = lca_trans()
        lca_ops = lca_operations()

        for idx, country in countries.iterrows():
                
            if not country['iso3'] == iso3:

                continue

            arpu = countries['arpu'].loc[idx]
            adoption_low = round(countries['adoption_low'].loc[idx], 0)

            for i in range(len(df1)):
                
                df1['nodes'].loc[i] = 1

                df1['tco'].loc[i] = cost_model(df1['length_km'].loc[i], 1)
                
                df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]) * 
                                                (adoption_low / 100))
                
                df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                            / (df1['users_area_sqkm'].loc[i])))
                ################# LCA MANUFACTURING PHASE ########################
                df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                    * (df1['length_km'].loc[i]))
                df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * 
                                                   df1['nodes'].loc[i])
                df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * 
                                                  df1['nodes'].loc[i])
                df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * 
                                                  df1['nodes'].loc[i])
                df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                            + df1['aluminium_mfg_ghg'].loc[i] 
                                            + df1['steel_iron_mfg_ghg'].loc[i] 
                                            + df1['plastics_mfg_ghg'].loc[i] 
                                            + df1['other_metals_mfg_ghg'].loc[i] 
                                            + df1['concrete_mfg_ghg'].loc[i])
                
                ####################### LCA TRANSPORTATION PHASE ###################
                df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                    * df1['nodes'].loc[i])

                ####################### LCA OPERATIONS PHASE #######################
                df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * 
                                                    df1['nodes'].loc[i]) 
                                        + ((lca_ops['base_station_power_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                        * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / df1['users_area_sqkm'].loc[i]))) * 
                                        0.19338) 
                ####################### LCA END OF LIFE TREATMENT PHASE ############
                df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                    * df1['length_km'].loc[i])
                df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * 
                                                   df1['nodes'].loc[i])
                df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * 
                                                   df1['nodes'].loc[i])
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
                    df1['users_area_sqkm'].loc[i])
                
                df1['algorithm'].loc[i] = 'Dijkstras'

                df1['total_ssc_usd'].loc[i] = (
                    df1['total_ghg_emissions_kg'].loc[i] / 1000) * 185
                
                df1['ssc_per_user'].loc[i] = (df1['total_ssc_usd'].loc[i] / 
                                              df1['users_area_sqkm'].loc[i])
        
        totat_ghg = df1[['iso3', 'GID_1', 'population', 'users_area_sqkm',  
                    'total_mfg_ghg_kg', 'total_trans_ghg_kg', 'total_ops_ghg_kg', 
                    'total_eolt_ghg_kg', 'total_ghg_emissions_kg', 
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()
        scc_avg = country_totat_ghg['ssc_per_user'].mean()

        country_totat_ghg = pd.DataFrame({'iso3': 
                            [country_totat_ghg['iso3'].iloc[0]], 
                            'total_ghg_emissions_kg': [country_totat_ghg[
                            'total_ghg_emissions_kg'].iloc[0]], 
                            'emissions_kg_per_subscriber': [ghg_avg], 
                            'total_ssc_usd': [country_totat_ghg[
                            'total_ssc_usd'].iloc[0]],
                            'ssc_per_user': [scc_avg], 
                            'strategy': [country_totat_ghg['strategy'].iloc[0]],
                            'algorithm': [country_totat_ghg['algorithm'].iloc[0]]})

        df3 = df1[['iso3', 'GID_1', 'users_area_sqkm', 'optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg', 'total_mfg_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_1', 'users_area_sqkm', 
                'total_mfg_ghg_kg', 'strategy', 'algorithm'], value_vars = 
                ['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 
                'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 'other_metals_mfg_ghg', 
                'concrete_mfg_ghg',], var_name = 'emission_category', 
                value_name = 'lca_phase_ghg_kg')
        
        df4 = df1[['iso3', 'GID_1', 'users_area_sqkm', 'optic_fiber_eolt_ghg', 
                'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
                'other_metals_eolt_ghg', 'concrete_eolt_ghg', 
                'total_eolt_ghg_kg', 'strategy', 'algorithm']]
        
        total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_1', 'users_area_sqkm', 
            'total_eolt_ghg_kg', 'strategy', 'algorithm'], value_vars = 
            ['optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
            'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg',], 
            var_name = 'emission_category', value_name = 'lca_phase_ghg_kg')
        
        total_tco = df1[['iso3', 'GID_1', 'population', 'users_area_sqkm', 
                         'tco', 'tco_per_user', 'strategy', 'algorithm']]
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


def local_pcsf_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions for local PCSF fiber nodes
    """
    print('Processing TCO and emissions for {}'.format(iso3))
    file = os.path.join(DATA_RESULTS, iso3, 'fiber_design')

    try:

        if os.path.exists(file):

            file_2 = os.path.join(file, '{}_fiber_pcsf_access.csv'.format(iso3))
            df1 = gpd.read_file(file_2)

        df1[['tco', 'tco_per_user', 'users_area_sqkm', 'nodes']] = ''

        df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
            'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
            'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
            'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
            'emissions_kg_per_subscriber', 'total_ssc_usd', 'ssc_per_user']] = ''
        
        lca_mfg = lca_manufacturing()
        lca_eot = lca_eolt()
        lca_tran = lca_trans()
        lca_ops = lca_operations()

        for idx, country in countries.iterrows():
                
            if not country['iso3'] == iso3:

                continue

            arpu = countries['arpu'].loc[idx]
            adoption_low = round(countries['adoption_low'].loc[idx], 0)

            df1['length_km'] = df1['length_km'].astype(float)
            df1['population'] = df1['population'].astype(float)

            for i in range(len(df1)):
                
                df1['iso3'].loc[i] = iso3

                df1['nodes'].loc[i] = 1

                df1['tco'].loc[i] = cost_model(df1['length_km'].loc[i], 
                                            df1['nodes'].loc[i])
                
                df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]))
                
                df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                            / (df1['users_area_sqkm'].loc[i])))

                ################# LCA MANUFACTURING PHASE ########################
                df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                    * (df1['length_km'].loc[i]))
                df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * df1['nodes'].loc[i])
                df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * df1['nodes'].loc[i])
                df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * 1)
                df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                    * 1)
                df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * 
                                                df1['nodes'].loc[i])
                df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                                + df1['aluminium_mfg_ghg'].loc[i] 
                                                + df1['steel_iron_mfg_ghg'].loc[i] 
                                                + df1['plastics_mfg_ghg'].loc[i] 
                                                + df1['other_metals_mfg_ghg'].loc[i] 
                                                + df1['concrete_mfg_ghg'].loc[i])
                
                ####################### LCA TRANSPORTATION PHASE ###################
                df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                    * df1['nodes'].loc[i])

                ####################### LCA OPERATIONS PHASE #######################
                df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * 1) 
                                        + ((lca_ops['base_station_power_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                        * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / df1['users_area_sqkm'].loc[i]))) * 
                                        0.19338) 
                ####################### LCA END OF LIFE TREATMENT PHASE ############
                df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                    * df1['length_km'].loc[i])
                df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * 
                                                df1['nodes'].loc[i])
                df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * 
                                                df1['nodes'].loc[i])
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
                    df1['users_area_sqkm'].loc[i])
                
                df1['total_ssc_usd'].loc[i] = (
                    df1['total_ghg_emissions_kg'].loc[i] / 1000) * 185
                
                df1['ssc_per_user'].loc[i] = (df1['total_ssc_usd'].loc[i] / 
                                              df1['users_area_sqkm'].loc[i])

        totat_ghg = df1[['iso3', 'GID_2', 'users_area_sqkm', 'total_mfg_ghg_kg', 
                    'total_trans_ghg_kg', 'total_ops_ghg_kg', 'total_eolt_ghg_kg', 
                    'total_ghg_emissions_kg', 'emissions_kg_per_subscriber', 
                    'total_ssc_usd', 'ssc_per_user', 'strategy', 'algorithm']]
        
        country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()
        scc_avg = country_totat_ghg['ssc_per_user'].mean()

        country_totat_ghg = pd.DataFrame({'iso3': 
                            [country_totat_ghg['iso3'].iloc[0]], 
                            'total_ghg_emissions_kg': [country_totat_ghg[
                            'total_ghg_emissions_kg'].iloc[0]], 
                            'emissions_kg_per_subscriber': [ghg_avg], 
                            'total_ssc_usd': [country_totat_ghg[
                            'total_ssc_usd'].iloc[0]],
                            'ssc_per_user': [scc_avg], 
                            'strategy': [country_totat_ghg['strategy'].iloc[0]],
                            'algorithm': [country_totat_ghg['algorithm'].iloc[0]]})

        df3 = df1[['iso3', 'GID_2', 'users_area_sqkm', 'optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg', 'total_mfg_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_2', 'users_area_sqkm', 
                'total_mfg_ghg_kg', 'strategy', 'algorithm'], 
                value_vars = ['optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg',], var_name = 
                'emission_category', value_name = 'lca_phase_ghg_kg')
        
        df4 = df1[['iso3', 'GID_2', 'users_area_sqkm', 'optic_fiber_eolt_ghg', 
                'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
                'other_metals_eolt_ghg', 'concrete_eolt_ghg', 'total_eolt_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_2', 'users_area_sqkm', 
            'total_eolt_ghg_kg', 'strategy', 'algorithm'], 
            value_vars = ['optic_fiber_eolt_ghg', 
            'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
            'other_metals_eolt_ghg', 'concrete_eolt_ghg',], var_name = 
            'emission_category', value_name = 'lca_phase_ghg_kg')
        
        total_tco = df1[['iso3', 'GID_2', 'population', 'users_area_sqkm', 'tco', 
                        'tco_per_user', 'strategy', 'algorithm']]
        fileout = '{}_pcsf_local_emission_results.csv'.format(iso3)
        fileout1 = '{}_pcsf_local_mfg_emission_results.csv'.format(iso3)
        fileout2 = '{}_pcsf_local_eolt_emission_results.csv'.format(iso3)
        fileout3 = '{}_pcsf_local_tco_results.csv'.format(iso3)
        fileout4 = '{}_pcsf_country_local_emission.csv'.format(iso3)

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

    except:

        pass

    return None


def regional_pcsf_cost_emissions(iso3):   
    """
    This function calculates the TCO and emissions for regional PCSF fiber nodes
    """
    print('Processing PCSF regional TCO and emissions for {}'.format(iso3))
    
    file = os.path.join(DATA_RESULTS, iso3, 'fiber_design', 
                        '{}_fiber_pcsf_regional.csv'.format(iso3))
    
    if os.path.exists(file):

        df1 = pd.read_csv(file)
        df1[['users_area_sqkm', 'tco', 'tco_per_user', 'nodes']] = ''

        df1[['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 
            'plastics_mfg_ghg', 'other_metals_mfg_ghg', 'concrete_mfg_ghg', 
            'total_mfg_ghg_kg', 'optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 
            'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 'other_metals_eolt_ghg', 
            'concrete_eolt_ghg', 'total_eolt_ghg_kg', 'total_trans_ghg_kg', 
            'total_ops_ghg_kg', 'total_ghg_emissions_kg', 
            'emissions_kg_per_subscriber', 'total_ssc_usd', 'ssc_per_user']] = ''
        
        lca_mfg = lca_manufacturing()
        lca_eot = lca_eolt()
        lca_tran = lca_trans()
        lca_ops = lca_operations()

        for idx, country in countries.iterrows():
                
            if not country['iso3'] == iso3:

                continue

            arpu = countries['arpu'].loc[idx]
            adoption_low = round(countries['adoption_low'].loc[idx], 0)

            for i in range(len(df1)):
                
                df1['nodes'].loc[i] = 1

                df1['tco'].loc[i] = cost_model(df1['length_km'].loc[i], 1)
                
                df1['users_area_sqkm'].loc[i] = ((df1['population'].loc[i]) * 
                                                (adoption_low / 100))
                
                df1['tco_per_user'].loc[i] = (((df1['tco'].loc[i]) 
                                            / (df1['users_area_sqkm'].loc[i])))
                ################# LCA MANUFACTURING PHASE ########################
                df1['optic_fiber_mfg_ghg'].loc[i] = (lca_mfg['optic_fiber_ghg'] 
                                                    * (df1['length_km'].loc[i]))
                df1['aluminium_mfg_ghg'].loc[i] = (lca_mfg['aluminium_ghg'] * 
                                                   df1['nodes'].loc[i])
                df1['steel_iron_mfg_ghg'].loc[i] = (lca_mfg['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_mfg_ghg'].loc[i] = (lca_mfg['plastics_ghg'] * 
                                                  df1['nodes'].loc[i])
                df1['other_metals_mfg_ghg'].loc[i] = (lca_mfg['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_mfg_ghg'].loc[i] = (lca_mfg['concrete_ghg'] * 
                                                  df1['nodes'].loc[i])
                df1['total_mfg_ghg_kg'].loc[i] = (df1['optic_fiber_mfg_ghg'].loc[i] 
                                            + df1['aluminium_mfg_ghg'].loc[i] 
                                            + df1['steel_iron_mfg_ghg'].loc[i] 
                                            + df1['plastics_mfg_ghg'].loc[i] 
                                            + df1['other_metals_mfg_ghg'].loc[i] 
                                            + df1['concrete_mfg_ghg'].loc[i])
                
                ####################### LCA TRANSPORTATION PHASE ###################
                df1['total_trans_ghg_kg'].loc[i] = (lca_tran['optic_fiber_ghg'] 
                                                    * df1['nodes'].loc[i])

                ####################### LCA OPERATIONS PHASE #######################
                df1['total_ops_ghg_kg'].loc[i] = (((lca_ops['cpe_power'] * 
                                                    df1['nodes'].loc[i]) 
                                        + ((lca_ops['base_station_power_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / (df1['users_area_sqkm'].loc[i])) + (1.5 
                                        * ((lca_ops['terminal_unit_pwr_kwh'] * 
                                            df1['nodes'].loc[i]) 
                                        / df1['users_area_sqkm'].loc[i]))) * 
                                        0.19338) 
                ####################### LCA END OF LIFE TREATMENT PHASE ############
                df1['optic_fiber_eolt_ghg'].loc[i] = (lca_eot['optic_fiber_ghg'] 
                                                    * df1['length_km'].loc[i])
                df1['aluminium_eolt_ghg'].loc[i] = (lca_eot['aluminium_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['steel_iron_eolt_ghg'].loc[i] = (lca_eot['steel_iron_ghg'] * 
                                                    df1['nodes'].loc[i])
                df1['plastics_eolt_ghg'].loc[i] = (lca_eot['plastics_ghg'] * 
                                                   df1['nodes'].loc[i])
                df1['other_metals_eolt_ghg'].loc[i] = (lca_eot['other_metals_ghg'] 
                                                    * df1['nodes'].loc[i])
                df1['concrete_eolt_ghg'].loc[i] = (lca_eot['concrete_ghg'] * 
                                                   df1['nodes'].loc[i])
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
                    df1['users_area_sqkm'].loc[i])
        
                df1['total_ssc_usd'].loc[i] = (
                    df1['total_ghg_emissions_kg'].loc[i] / 1000) * 185
                
                df1['ssc_per_user'].loc[i] = (df1['total_ssc_usd'].loc[i] / 
                                              df1['users_area_sqkm'].loc[i])

        totat_ghg = df1[['iso3', 'GID_1', 'population', 'users_area_sqkm',  
                    'total_mfg_ghg_kg', 'total_trans_ghg_kg', 'total_ops_ghg_kg', 
                    'total_eolt_ghg_kg', 'total_ghg_emissions_kg', 
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        country_totat_ghg = totat_ghg[['iso3', 'total_ghg_emissions_kg',
                    'emissions_kg_per_subscriber', 'total_ssc_usd', 
                    'ssc_per_user', 'strategy', 'algorithm']]
        
        ghg_avg = country_totat_ghg['emissions_kg_per_subscriber'].mean()
        scc_avg = country_totat_ghg['ssc_per_user'].mean()

        country_totat_ghg = pd.DataFrame({'iso3': 
                            [country_totat_ghg['iso3'].iloc[0]], 
                            'total_ghg_emissions_kg': [country_totat_ghg[
                            'total_ghg_emissions_kg'].iloc[0]], 
                            'emissions_kg_per_subscriber': [ghg_avg], 
                            'total_ssc_usd': [country_totat_ghg[
                            'total_ssc_usd'].iloc[0]],
                            'ssc_per_user': [scc_avg], 
                            'strategy': [country_totat_ghg['strategy'].iloc[0]],
                            'algorithm': [country_totat_ghg['algorithm'].iloc[0]]})

        df3 = df1[['iso3', 'GID_1', 'users_area_sqkm', 'optic_fiber_mfg_ghg', 
                'aluminium_mfg_ghg', 'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 
                'other_metals_mfg_ghg', 'concrete_mfg_ghg', 'total_mfg_ghg_kg', 
                'strategy', 'algorithm']]
        
        total_mfg = pd.melt(df3, id_vars = ['iso3', 'GID_1', 'users_area_sqkm', 
                'total_mfg_ghg_kg', 'strategy', 'algorithm'], value_vars = 
                ['optic_fiber_mfg_ghg', 'aluminium_mfg_ghg', 
                'steel_iron_mfg_ghg', 'plastics_mfg_ghg', 'other_metals_mfg_ghg', 
                'concrete_mfg_ghg',], var_name = 'emission_category', 
                value_name = 'lca_phase_ghg_kg')
        
        df4 = df1[['iso3', 'GID_1', 'users_area_sqkm', 'optic_fiber_eolt_ghg', 
                'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 'plastics_eolt_ghg', 
                'other_metals_eolt_ghg', 'concrete_eolt_ghg', 
                'total_eolt_ghg_kg', 'strategy', 'algorithm']]
        
        total_eolt = pd.melt(df4, id_vars = ['iso3', 'GID_1', 'users_area_sqkm', 
            'total_eolt_ghg_kg', 'strategy', 'algorithm'], value_vars = 
            ['optic_fiber_eolt_ghg', 'aluminium_eolt_ghg', 'steel_iron_eolt_ghg', 
            'plastics_eolt_ghg', 'other_metals_eolt_ghg', 'concrete_eolt_ghg',], 
            var_name = 'emission_category', value_name = 'lca_phase_ghg_kg')
        
        total_tco = df1[['iso3', 'GID_1', 'population', 'users_area_sqkm', 
                         'tco', 'tco_per_user', 'strategy', 'algorithm']]
        fileout = '{}_pcsf_regional_emission_results.csv'.format(iso3)
        fileout1 = '{}_pcsf_regional_mfg_emission_results.csv'.format(iso3)
        fileout2 = '{}_pcsf_regional_eolt_emission_results.csv'.format(iso3)
        fileout3 = '{}_pcsf_regional_tco_results.csv'.format(iso3)
        fileout4 = '{}_pcsf_regional_emission.csv'.format(iso3)

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