import configparser
import os
import warnings
import pandas as pd
from glassfibre.preprocessing import ProcessCountry, ProcessRegions, ProcessPopulation
from glassfibre.generator import PointsGenerator, EdgeGenerator
from glassfibre.fiber_process import FiberProcess
from glassfibre.strategies import baseline_cost_emissions, local_cost_emissions
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


path = os.path.join(DATA_RAW, 'countries.csv')
pop_tif_loc = os.path.join(DATA_RAW, 'WorldPop', 'ppp_2020_1km_Aggregated.tif')

countries = pd.read_csv(path, encoding = 'utf-8-sig')

for idx, country in countries.iterrows():
        
    if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    #if not country['iso3'] == 'GAB':
        
        continue 

    country = ProcessCountry(path, countries['iso3'].loc[idx])
    #country.process_country_shapes()

    regions = ProcessRegions(countries['iso3'].loc[idx], countries['lowest'].loc[idx])
    #regions.process_regions()
    #regions.process_sub_region_boundaries()

    populations = ProcessPopulation(path, countries['iso3'].loc[idx], countries['lowest'].loc[idx], pop_tif_loc)
    #populations.process_national_population()
    #populations.process_population_tif()

    points_generator = PointsGenerator(countries['iso3'].loc[idx])
    #points_generator.generate_gid_points()
    #points_generator.generate_country_points()

    edges_generator = EdgeGenerator(countries['iso3'].loc[idx], countries['iso2'].loc[idx])
    #edges_generator.fit_regional_node_edges()
    #edges_generator.fit_country_node_edges()
    #edges_generator.process_existing_fiber()
    
    #fiber_processor = FiberProcess(countries['iso3'].loc[idx], countries['iso2'].loc[idx], path)
    '''fiber_processor.process_existing_fiber()
    fiber_processor.generate_agglomeration_lut()
    fiber_processor.find_nodes_on_existing_infrastructure()
    fiber_processor.find_regional_nodes()
    fiber_processor.prepare_edge_fitting()
    fiber_processor.fit_regional_edges()
    fiber_processor.generate_core_lut()
    fiber_processor.generate_backhaul_lut()'''
    
    baseline_cost_emissions(countries['iso3'].loc[idx])
    local_cost_emissions(countries['iso3'].loc[idx])