import configparser
import os
import warnings
import pandas as pd
from glassfibre.preprocessing import (ProcessCountry, ProcessRegions, 
                                      ProcessPopulation)

from glassfibre.fiber_process import FiberProcess
from glassfibre.netPlanning import(process_regional_settlement_tifs, 
    process_access_settlement_tifs, generate_access_settlement_lut, 
    generate_regional_settlement_lut, generate_agglomeration_lut,
    find_largest_regional_settlement, get_settlement_routing_paths,
    create_regions_to_model, create_routing_buffer_zone, create_region_nodes,
    fit_regional_node_edges, combine_access_nodes, combine_access_edges,
    combine_pcsf_access_edges, combine_pcsf_regional_nodes,
    generate_access_csv, combine_regional_nodes, combine_regional_edges,
    generate_regional_csv, generate_existing_fiber_csv, 
    generate_pcsf_regional_csv, generate_pcsf_access_csv)
from glassfibre.street_data import(generate_region_nodes, 
                                   generate_sub_region_nodes)

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
        
    if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    #if not country['iso3'] == 'RWA':
        
        continue 
   
    country = ProcessCountry(path, countries['iso3'].loc[idx])
    #country.process_country_shapes()

    regions = ProcessRegions(countries['iso3'].loc[idx], 
                             countries['lowest'].loc[idx])
    #regions.process_regions()
    #regions.process_sub_region_boundaries()

    populations = ProcessPopulation(path, countries['iso3'].loc[idx], 
                                    countries['lowest'].loc[idx], pop_tif_loc)
    #opulations.process_national_population()
    #populations.process_population_tif()
    
    fiber_processor = FiberProcess(countries['iso3'].loc[idx], 
                                   countries['iso2'].loc[idx], path)
    '''fiber_processor.process_existing_fiber()
    fiber_processor.find_nodes_on_existing_infrastructure()
    
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

    #download_street_data(countries['iso3'].loc[idx])
    #combine_street_csv(countries['iso3'].loc[idx])
    #generate_street_shapefile(countries['iso3'].loc[idx])
    #process_region_street(countries['iso3'].loc[idx])
    #process_subregion_street(countries['iso3'].loc[idx])

    #generate_region_nodes(countries['iso3'].loc[idx])
    #generate_sub_region_nodes(countries['iso3'].loc[idx])

    #combine_pcsf_access_edges(countries['iso3'].loc[idx])
    #combine_pcsf_regional_nodes(countries['iso3'].loc[idx])

    #generate_pcsf_regional_csv(countries['iso3'].loc[idx])
    #generate_pcsf_access_csv(countries['iso3'].loc[idx])