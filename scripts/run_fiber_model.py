"""
Simulation run script for mobile broadband.

Written by Bonface Osoro & Ed Oughton.

September 2024

"""
import configparser
import os
import math
import time
import pandas as pd
import glassfibre.fiber as fb
from tqdm import tqdm
pd.options.mode.chained_assignment = None 

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
RESULTS = os.path.join(BASE_PATH, '..', 'results', 'fiber')
SSA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'SSA')

def run_uq_processing_cost():
    """
    Run the UQ inputs through the fiber broadband model. 
    
    """
    path = os.path.join(RESULTS, 'uq_parameters_cost.csv') 
    ssa = os.path.join(SSA_RESULTS, 'SSA_decile_summary_stats.csv')

    if not os.path.exists(path):
        print('Cannot locate uq_parameters_cost.csv')

    df = pd.read_csv(path)
    df1 = pd.read_csv(ssa)
    df1 = df1.drop(columns = ['total_poor_unconnected'])
    df1 = df1.rename(columns = {'total_population': 'population'})
    df = pd.merge(df, df1, on = 'decile', how = 'inner')
    df = df.to_dict('records')

    results = []

    for item in tqdm(df, desc = "Processing uncertainty fiber cost results"):
        

        capex_cost_usd = fb.capex_cost(item['olt_usd'], item['civil_usd'], 
                        item['transportation_usd'], item['installation_usd'], 
                        item['rpu_usd'], item['odf_unit_usd'], 
                        item['mean_distance_km'], item['nodes'])
        
        opex_cost_usd = fb.opex_cost(item['rent_usd'], item['staff_usd'], 
                        item['power_usd'], item['regulatory_usd'], 
                        item['customer_usd'], item['other_costs_usd'], 
                        item['nodes'])
        
        total_cost_ownership = fb.total_cost_ownership(capex_cost_usd, 
                opex_cost_usd, item['discount_rate'], item['assessment_years'])
        
        per_user_tco = (total_cost_ownership / item['total_population'])

        total_ssa_tco_usd = per_user_tco * item['population']

        per_user_annualized_usd = (per_user_tco / item['assessment_years'])

        per_monthly_tco_usd = per_user_annualized_usd / 12
        
        
        results.append({
            'capex_cost_usd' : capex_cost_usd,
            'opex_cost_usd' : opex_cost_usd,
            'total_cost_ownership' : total_cost_ownership,
            'mean_connected' : item['total_population'],
            'per_user_tco' : per_user_tco,
            'total_ssa_tco_usd' : total_ssa_tco_usd,
            'per_user_annualized_usd' : per_user_annualized_usd,
            'per_monthly_tco_usd' : per_monthly_tco_usd,
            'algorithm' : item['algorithm'],
            'strategy' : item['strategy'],
            'decile' : item['decile']
        })

        df = pd.DataFrame.from_dict(results)
        df['technology'] = 'fiber'

        filename = 'SSA_fiber_cost_results.csv' 
        if not os.path.exists(SSA_RESULTS):

            os.makedirs(SSA_RESULTS)

        path_out = os.path.join(SSA_RESULTS, filename)
        df.to_csv(path_out, index = False)


    return


def run_uq_processing_emission():
    """
    Run the UQ inputs through the fiber broadband model.
    
    """
    path = os.path.join(RESULTS, 'uq_parameters_emission.csv') 
    ssa = os.path.join(SSA_RESULTS, 'SSA_decile_summary_stats.csv')

    if not os.path.exists(path):
        print('Cannot locate uq_parameters_emission.csv')

    df = pd.read_csv(path)
    df1 = pd.read_csv(ssa)
    df1 = df1.drop(columns = ['total_poor_unconnected'])
    df1 = df1.rename(columns = {'total_population': 'population'})
    df = pd.merge(df, df1, on = 'decile', how = 'inner')
    df = df.to_dict('records')

    results = []

    for item in tqdm(df, desc = "Processing uncertainty fiber results"):

        lca_mfg = fb.lca_manufacturing(item['fiber_cable_kg_per_km'], 
                    item['pcb_kg'], item['pvc_kg'], item['steel_kg'], 
                    item['router'], item['glass_kg_co2e'], item['pcb_kg_co2e'], 
                    item['steel_kg_co2e'], item['pvc_kg_co2e'], 
                    item['mean_distance_km'], item['nodes'])
        
        lca_trans = fb.lca_transportation(item['mean_distance_km'], 
                                          item['fuel_efficiency'], 
                                          item['diesel_factor_kgco2e'])

        lca_constr = fb.lca_construction(item['fuel_efficiency'], 
                                         item['hours_per_km'], 
                                         item['diesel_factor_kgco2e'], 
                                         item['nodes'])

        lca_ops = fb.lca_operations(item['fiber_point_pwr_kwh'], 
                                    item['electricity_kg_co2e'], item['nodes'])

        lca_eolts = fb.lca_eolt(item['fiber_cable_kg_per_km'], item['pcb_kg'], 
                    item['pvc_kg'], item['steel_kg'], item['router'], 
                    item['glass_eolt_kg_co2e'], item['plastics_factor_kgco2e'], 
                    item['metals_factor_kgco2e'], item['mean_distance_km'], 
                    item['nodes'])
        
        total_emissions_ghg_kg = (lca_mfg + lca_trans + lca_constr + lca_ops 
                                  + lca_eolts) 
        
        user_emissions_kg_per_user = (total_emissions_ghg_kg / 
                                      item['total_population'])
        
        total_emissions_ssa_kg = user_emissions_kg_per_user * item['population']
        
        annualized_per_user_emissions = (user_emissions_kg_per_user / 
                                         item['assessment_years'])
        
        social_carbon_cost = fb.social_carbon_cost(total_emissions_ghg_kg, 
                                            item['social_carbon_cost_usd'])
        
        per_user_scc_usd = (social_carbon_cost / item['total_population'])

        total_ssa_scc_usd = per_user_scc_usd * item['population']
        
        per_user_annualized_scc_usd = (per_user_scc_usd / 
                                       item['assessment_years'])
        
        results.append({
            'lca_mfg_kg' : lca_mfg,
            'lca_trans_kg' : lca_trans,
            'lca_constr_kg' : lca_constr,
            'lca_ops_kg' : lca_ops,
            'lca_eolts_kg' : lca_eolts,
            'total_emissions_ghg_kg' : total_emissions_ghg_kg,
            'total_emissions_ssa_kg' : total_emissions_ssa_kg,
            'total_population' : item['total_population'],
            'social_carbon_cost_usd' : social_carbon_cost,
            'user_emissions_kg_per_user' : user_emissions_kg_per_user,
            'annualized_per_user_emissions' : annualized_per_user_emissions,
            'per_user_scc_usd' : per_user_scc_usd,
            'total_ssa_scc_usd' : total_ssa_scc_usd, 
            'per_user_annualized_scc_usd' : per_user_annualized_scc_usd,
            'decile' : item['decile'],
            'strategy' : item['strategy'],
            'algorithm' : item['algorithm']
        })

        df = pd.DataFrame.from_dict(results)
        df['technology'] = 'fiber'

        filename = 'SSA_fiber_emission_results.csv'
        if not os.path.exists(SSA_RESULTS):

            os.makedirs(SSA_RESULTS)

        path_out = os.path.join(SSA_RESULTS, filename)
        df.to_csv(path_out, index = False)


    return None


if __name__ == '__main__':

    print('Running fiber broadband cost model')
    run_uq_processing_cost()

    print('Running fiber broadband emissions model')
    run_uq_processing_emission()