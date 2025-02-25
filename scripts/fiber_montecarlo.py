"""
Preprocess all Uncertainty Quantification (UQ) inputs. 

Written by Bonface Osoro & Ed Oughton.

October 2024

"""
import configparser
import os
import random
import numpy as np
import pandas as pd
from inputs import parameters
from geosafi_consav.mobile import generate_log_normal_dist_value
pd.options.mode.chained_assignment = None 

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results')
DATA_SSA = os.path.join(BASE_PATH, '..', 'results', 'SSA')

deciles = ['Decile 1', 'Decile 2', 'Decile 3', 'Decile 4', 'Decile 5',
           'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 'Decile 10']


def multinetwork_fiber_costs(i, fiber_params):
    """
    This function generates random values within the given parameter ranges. 

    Parameters
    ----------
    i : int.
        number of iterations
    fiber_params : dict
        Dictionary containing fiber engineering details

    Return
    ------
        output : list
            List containing cost outputs

    """
    output = []

    for decile in deciles:

        olt_usd = random.randint(fiber_params['olt_low_usd'], 
                                fiber_params['olt_high_usd'])
        
        otc_usd = random.randint(fiber_params['otc_low_usd'], 
                                fiber_params['otc_high_usd'])
        
        wan_unit_usd = random.randint(fiber_params['wan_unit_low_usd'], 
                                fiber_params['wan_unit_high_usd'])

        installation_usd = random.randint(fiber_params['installation_low_usd'], 
                                fiber_params['installation_high_usd'])
        
        wdm_usd = random.randint(fiber_params['wdm_low_usd'], 
                                fiber_params['wdm_high_usd'])
        
        other_usd = random.randint(fiber_params['other_low_usd'], 
                                fiber_params['other_high_usd'])
        
        staff_usd = random.randint(fiber_params['staff_low_usd'], 
                                fiber_params['staff_high_usd'])
        
        power_usd = random.randint(fiber_params['power_low_usd'], 
                                fiber_params['power_high_usd'])
        
        regulatory_usd = random.randint(fiber_params['regulatory_low_usd'], 
                                fiber_params['regulatory_high_usd'])
        
        customer_usd = random.randint(fiber_params['customer_low_usd'], 
                                fiber_params['customer_high_usd'])
        
        other_costs_usd = random.randint(fiber_params['other_low_costs_usd'], 
                                fiber_params['other_high_costs_usd'])

        fiber_speed_gbps = random.randint(fiber_params['min_fiber_speed_gbps'], 
            fiber_params['max_fiber_speed_gbps'])
        
        node_pwr_low_kWh_per_km_gbps = random.uniform(
            fiber_params['node_pwr_low_kWh_per_km_gbps'], 
            fiber_params['node_pwr_high_kWh_per_km_gbps'])
        
        output.append({
            'olt_usd' : olt_usd,
            'otc_usd' : otc_usd,
            'wan_unit_usd' : wan_unit_usd,
            'installation_usd' : installation_usd,
            'wdm_usd' : wdm_usd,
            'other_usd' : other_usd,
            'staff_usd' : staff_usd,
            'power_usd' : power_usd,
            'regulatory_usd' : regulatory_usd,
            'customer_usd' : customer_usd,
            'fiber_speed_gbps' : fiber_speed_gbps,
            'node_power_kWh_per_km_gbps' : node_pwr_low_kWh_per_km_gbps,
            'other_costs_usd' : other_costs_usd,
            'assessment_years' : fiber_params['assessment_period_year'],
            'discount_rate' : fiber_params['discount_rate_percent'],
            'decile' : decile
        })


    return output


def uq_inputs_costs(parameters):
    """
    Generate all UQ cost inputs in preparation for running through the 
    mobile broadband model. 

    Parameters
    ----------
    parameters : dict
        dictionary of dictionary containing mobile cost values.

    """
    iterations = []

    for key, fiber_params in parameters.items():

        for i in range(0, fiber_params['iterations']):

            if key in ['regional']:
                
                data = multinetwork_fiber_costs(i, fiber_params)

            iterations = iterations + data

    df = pd.DataFrame.from_dict(iterations)

    # Import user data
    pop_path = os.path.join(DATA_SSA, 'population_connected_fiber.csv') 
    df1 = pd.read_csv(pop_path)

    filename = 'uq_parameters_cost.csv'
    folder_out = os.path.join(DATA_RESULTS, 'fiber')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)
    
    merged_df = pd.merge(df, df1, on = 'decile')
    path_out = os.path.join(folder_out, filename)
    merged_df.to_csv(path_out, index = False)


    return None


def multinetwork_fiber_emissions(i, fiber_params):
    """
    This function generates random values within the given emission ranges. 

    Parameters
    ----------
    i : int.
        number of iterations
    mobile_params : dict
        Dictionary containing fiber emission details

    Return
    ------
        output : list
            List containing emission outputs

    """
    output = []

    for decile in deciles:

        fiber_cable_kg_per_km = random.randint(
            fiber_params['fiber_cable_low_kg_per_km'], 
            fiber_params['fiber_cable_high_kg_per_km'])

        pcb_kg = random.uniform(fiber_params['pcb_low_kg'], 
            fiber_params['pcb_high_kg'])
        
        concrete_kg = random.uniform(fiber_params['machine_concrete_low_kg'], 
            fiber_params['machine_concrete_high_kg'])
        
        pvc_kg = random.randint(fiber_params['pvc_low_kg'], 
            fiber_params['pvc_high_kg'])
        
        steel_kg = random.randint(fiber_params['steel_low_kg'], 
            fiber_params['steel_high_kg'])
        
        router = random.randint(fiber_params['low_router'], 
            fiber_params['high_router'])

        fuel_efficiency = random.uniform(fiber_params['fuel_efficiency_low'], 
            fiber_params['fuel_efficiency_high'])
        
        hours_per_km = random.randint(fiber_params['hours_low_per_km'], 
            fiber_params['hours_high_per_km'])
        
        fiber_speed_gbps = random.randint(fiber_params['min_fiber_speed_gbps'], 
            fiber_params['max_fiber_speed_gbps'])
        
        node_power_kWh_per_km_gbps = random.uniform(
            fiber_params['node_pwr_low_kWh_per_km_gbps'], 
            fiber_params['node_pwr_high_kWh_per_km_gbps'])
        
        truck_fuel_efficiency = random.uniform(
            fiber_params['truck_fuel_efficiency_low'], 
            fiber_params['truck_fuel_efficiency_high'])
        
        trench_percent = random.uniform(
            fiber_params['trench_low_percent'], 
            fiber_params['trench_high_percent'])
        
        output.append({
            'fiber_cable_kg_per_km' : fiber_cable_kg_per_km,
            'pcb_kg' : pcb_kg,
            'pvc_kg' : pvc_kg,
            'steel_kg' : steel_kg,
            'concrete_kg' : concrete_kg,
            'router' : router,
            'glass_kg_co2e' : fiber_params['glass_kg_co2e'],
            'pcb_kg_co2e' : fiber_params['pcb_kg_co2e'],
            'steel_kg_co2e' : fiber_params['steel_kg_co2e'],
            'concrete_kg_co2e' : fiber_params['concrete_kg_co2e'],
            'pvc_kg_co2e' : fiber_params['pvc_kg_co2e'],
            'router_kg_co2e' : fiber_params['olnu_kg_co2e'],
            'electricity_kg_co2e' : fiber_params['electricity_kg_co2e'],
            'glass_eolt_kg_co2e' : fiber_params['glass_eolt_kg_co2e'],
            'plastics_factor_kgco2e' : fiber_params['plastics_factor_kgco2'],
            'metals_factor_kgco2e' : fiber_params['metals_factor_kgco2'],
            'diesel_factor_kgco2e' : fiber_params['diesel_factor_kgco2e'],
            'container_ship_kgco2e' : fiber_params['container_ship_kgco2e'],
            'fuel_efficiency' : fuel_efficiency,
            'truck_fuel_efficiency' : truck_fuel_efficiency,
            'trench_percent' : trench_percent,
            'hours_per_km' : hours_per_km,
            'fiber_speed_gbps' : fiber_speed_gbps,
            'node_power_kWh_per_km_gbps' : node_power_kWh_per_km_gbps,
            'assessment_years' : fiber_params['assessment_period_year'],
            'social_carbon_cost_usd' : fiber_params['social_carbon_cost_usd'],
            'decile' : decile,
        })


    return output


def uq_inputs_emissions(parameters):
    """
    Generate all UQ emission inputs in preparation for running through the 
    fiber broadband model. 

    Parameters
    ----------
    parameters : dict
        dictionary of dictionary containing fiber emission values.

    """
    iterations = []

    for key, fiber_params in parameters.items():

        for i in range(0, fiber_params['iterations']):

            if key in ['regional']:
                
                data = multinetwork_fiber_emissions(i, fiber_params)

            iterations = iterations + data

    df = pd.DataFrame.from_dict(iterations)
    pop_path = os.path.join(DATA_SSA, 'population_connected_fiber.csv') 
    df1 = pd.read_csv(pop_path)

    filename = 'uq_parameters_emission.csv'
    folder_out = os.path.join(DATA_RESULTS, 'fiber')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    merged_df = pd.merge(df, df1, on = 'decile')
    path_out = os.path.join(folder_out, filename)
    merged_df.to_csv(path_out, index = False)


    return None


if __name__ == '__main__':

    print('Setting seed for consistent results')
    random.seed(10)

    print('Running uq_cost_inputs_generator()')
    #uq_inputs_costs(parameters)

    print('Running uq_inputs_emissions_generator()')
    uq_inputs_emissions(parameters)