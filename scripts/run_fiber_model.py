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
from inputs import maritime, electricity_costs
pd.options.mode.chained_assignment = None 

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
RESULTS = os.path.join(BASE_PATH, '..', 'results', 'fiber')
SSA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'SSA')
VALID = os.path.join(BASE_PATH, '..', '..', 'geosafi-consav', 'results', 'SSA')


def generate_ssa_costs():
    """
    This function generates the data on the maritime distance of shipping 
    components by sea from the port of China to the port of the SSA country. It 
    also reads and stores the cost of electricity in US$ per kWh in each SSA 
    country.

    Returns
    -------
    df : dataframe
        Dataframe containing the mean maritime distance of the SSA country deciles.
    """
    ssa = os.path.join(SSA_RESULTS, 'SSA_subregional_population_deciles.csv')
    df = pd.read_csv(ssa)
    df[['maritime_km', 'cost_kWh']] = ''

    for i in range(len(df)):

        df.loc[i, 'maritime_km'] = fb.maritime_distance(df.loc[i, 'iso3'], 
                                                        maritime)
        
        df.loc[i, 'cost_kWh'] = fb.electricity_cost(df.loc[i, 'iso3'], 
                                                    electricity_costs)

    df = df.groupby(['decile']).agg(maritime_km = ('maritime_km', 'mean'),
                                    cost_kWh = ('cost_kWh', 'mean')
                                    ).reset_index()
    

    return df


def run_uq_processing_cost():
    """
    Run the UQ inputs through the fiber broadband model. 
    
    """
    path = os.path.join(RESULTS, 'uq_parameters_cost.csv') 
    ssa = os.path.join(SSA_RESULTS, 'SSA_decile_summary_stats.csv')
    gni_data = os.path.join(VALID, 'SSA_decile_summary_stats.csv')

    if not os.path.exists(path):
        print('Cannot locate uq_parameters_cost.csv')

    df = pd.read_csv(path)
    df1 = pd.read_csv(ssa)
    gni = pd.read_csv(gni_data)
    gni = gni[['decile', 'cost_per_1GB_usd', 'monthly_income_usd', 
               'cost_per_month_usd', 'adoption_rate_perc', 'arpu_usd']]

    df1 = df1.drop(columns = ['total_poor_unconnected'])
    df1 = df1.rename(columns = {'total_population': 'population'})
    df = pd.merge(df, df1, on = 'decile', how = 'inner')
    df = pd.merge(df, gni, on = 'decile')
    electricity_cost = generate_ssa_costs()
    df = pd.merge(df, electricity_cost, on = 'decile', how = 'inner')
    df = df.to_dict('records')

    results = []

    for item in tqdm(df, desc = "Processing uncertainty fiber cost results"):
        

        capex_cost_usd = fb.capex_cost(item['olt_usd'], item['installation_usd'], 
                        item['otc_usd'], item['wan_unit_usd'], 
                        item['wdm_usd'], item['mean_distance_km'], item['nodes'])
        
        opex_cost_usd = fb.opex_cost(item['staff_usd'], 
                        item['cost_kWh'], item['regulatory_usd'], 
                        item['customer_usd'], item['other_costs_usd'], 
                        item['nodes'], item['assessment_years'], 
                        item['node_power_kWh_per_km_gbps'], 
                        item['fiber_speed_gbps'], item['mean_distance_km'])
        
        total_cost_ownership = fb.total_cost_ownership(capex_cost_usd, 
                opex_cost_usd, item['discount_rate'], item['assessment_years'])
        
        per_user_tco = ((total_cost_ownership / (item['total_population'] 
        * (item['adoption_rate_perc'] / 100))))

        total_ssa_tco_usd = (((per_user_tco * item['population'])) 
        * (item['adoption_rate_perc'] / 100))

        per_user_annualized_usd = (per_user_tco / item['assessment_years'])

        per_monthly_tco_usd = per_user_annualized_usd / 12

        percent_gni = per_monthly_tco_usd / item['monthly_income_usd'] * 100
        
        results.append({
            'capex_cost_usd' : capex_cost_usd,
            'opex_cost_usd' : opex_cost_usd,
            'total_cost_ownership' : total_cost_ownership,
            'mean_connected' : item['total_population'],
            'per_user_tco' : per_user_tco,
            'total_ssa_tco_usd' : total_ssa_tco_usd,
            'per_user_annualized_usd' : per_user_annualized_usd,
            'per_monthly_tco_usd' : per_monthly_tco_usd,
            'monthly_income_usd' : item['monthly_income_usd'],
            'cost_per_1GB_usd' : item['cost_per_1GB_usd'],
            'cost_per_month_usd' : item['cost_per_month_usd'],
            'adoption_rate_perc' : item['adoption_rate_perc'],
            'arpu_usd' : item['arpu_usd'],
            'percent_gni' : percent_gni,
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
    maritime_distance_results = generate_ssa_costs()
    df = pd.merge(df, maritime_distance_results, on = 'decile', how = 'inner')
 
    df = df.to_dict('records')

    results = []

    for item in tqdm(df, desc = "Processing uncertainty fiber results"):

        lca_mfg = fb.lca_manufacturing(item['fiber_cable_kg_per_km'], 
                    item['pcb_kg'], item['pvc_kg'], item['steel_kg'], 
                    item['concrete_kg'], item['glass_kg_co2e'], 
                    item['pcb_kg_co2e'], item['steel_kg_co2e'], 
                    item['concrete_kg_co2e'], item['pvc_kg_co2e'], 
                    item['mean_distance_km'], item['nodes'])
        
        lca_trans = fb.lca_transportation(item['mean_distance_km'], 
                                          item['truck_fuel_efficiency'], 
                                          item['diesel_factor_kgco2e'],
                                          item['maritime_km'],
                                          item['container_ship_kgco2e'])

        lca_constr = fb.lca_construction(item['mean_distance_km'], 
                                         item['trench_percent'],
                                         item['hours_per_km'],
                                         item['fuel_efficiency'], 
                                         item['diesel_factor_kgco2e'])

        lca_ops = fb.lca_operations(item['node_power_kWh_per_km_gbps'], 
                                    item['fiber_speed_gbps'],
                                    item['cost_kWh'],
                                    item['assessment_years'],
                                    item['electricity_kg_co2e'], 
                                    item['mean_distance_km'])

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
    #run_uq_processing_cost()

    print('Running fiber broadband emissions model')
    run_uq_processing_emission()