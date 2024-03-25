import configparser
import os
import warnings
import pandas as pd
from glassfibre.preprocessing import (ProcessCountry, ProcessRegions, 
                                      ProcessPopulation)

from glassfibre.fiber_process import FiberProcess
from glassfibre.strategies import (baseline_cost_emissions, local_cost_emissions, 
                                   regional_cost_emissions)
from glassfibre.netPlanning import(process_regional_settlement_tifs, 
    process_access_settlement_tifs, generate_access_settlement_lut, 
    generate_regional_settlement_lut, generate_agglomeration_lut,
    find_largest_regional_settlement, get_settlement_routing_paths,
    create_regions_to_model, create_routing_buffer_zone, create_region_nodes,
    fit_regional_node_edges, combine_access_nodes, combine_access_edges,
    generate_access_csv, combine_regional_nodes, combine_regional_edges,
    generate_regional_csv, generate_existing_fiber_csv)

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')


path = os.path.join(DATA_RAW, 'countries.csv')
pop_tif_loc = os.path.join(DATA_RAW, 'WorldPop', 'ppp_2020_1km_Aggregated.tif')

countries = pd.read_csv(path, encoding = 'utf-8-sig')

for idx, country in countries.iterrows():
        
    #if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    if not country['iso3'] == 'COD':
        
        continue 
   
    #country = ProcessCountry(path, countries['iso3'].loc[idx])
    #country.process_country_shapes()

    regions = ProcessRegions(countries['iso3'].loc[idx], 
                             countries['lowest'].loc[idx])
    #regions.process_regions()
    #regions.process_sub_region_boundaries()

    populations = ProcessPopulation(path, countries['iso3'].loc[idx], 
                                    countries['lowest'].loc[idx], pop_tif_loc)
    #populations.process_national_population()
    #populations.process_population_tif()
    
    fiber_processor = FiberProcess(countries['iso3'].loc[idx], 
                                   countries['iso2'].loc[idx], path)
    #fiber_processor.process_existing_fiber()
    #fiber_processor.find_nodes_on_existing_infrastructure()
    
    '''baseline_cost_emissions(countries['iso3'].loc[idx])
    local_cost_emissions(countries['iso3'].loc[idx])
    regional_cost_emissions(countries['iso3'].loc[idx])

    process_regional_settlement_tifs(country)
    process_access_settlement_tifs(country)
    generate_access_settlement_lut(country)
    generate_regional_settlement_lut(country)

    generate_agglomeration_lut(country)
    find_largest_regional_settlement(country)
    get_settlement_routing_paths(country)
    create_regions_to_model(country)
    create_routing_buffer_zone(country)'''

    #create_region_nodes(countries['iso3'].loc[idx])
    #fit_regional_node_edges(countries['iso3'].loc[idx])
   
    #combine_access_nodes(countries['iso3'].loc[idx])
    #combine_access_edges(countries['iso3'].loc[idx])
    #generate_access_csv(countries['iso3'].loc[idx])

    #combine_regional_nodes(countries['iso3'].loc[idx])
    #combine_regional_edges(countries['iso3'].loc[idx])
    #generate_regional_csv(countries['iso3'].loc[idx])

    #generate_existing_fiber_csv(countries['iso3'].loc[idx])
    print(country[2])