"""
A PoC for the healthsite.io data
"""
import configparser
import os
import logging
import sys
import warnings

import pandas as pd
import geopandas as gpd

from glassfibre.processor import Processor
from glassfibre.solver import PCSTSolver

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, 'SLE_data')

fiber_path = os.path.join(DATA_PROCESSED, 'settlement nodes', 'SLE.1.1_1.shp')
street_path = os.path.join(DATA_PROCESSED, 'street', 'SLE.1.1_1.shp')

def main():

    logging.basicConfig(filename = 'log.log',level = logging.DEBUG)
    fiber_sites = gpd.read_file(fiber_path)
    fiber_sites = fiber_sites[['iso3', 'GID_0', 'GID_2', 'population', 'lon', 
                               'lat', 'geometry']]
    #fiber_sites['geometry'] = fiber_sites.apply(lambda x: x.geometry.centroid, axis = 1)

    streets = gpd.read_file(street_path)
    
    logging.info(f"Running on {fiber_sites}")
    pr = Processor("Senegal")
    logging.info("Snapping addresses to streets")
    pr.snap_points_to_line(streets, fiber_sites)
    logging.info("Converting GIS to graph")
    pr.geom_to_graph()
    logging.info("Writing intermediate files")
    pr.store_intermediate()

    logging.info("Create solver")
    sl = PCSTSolver(pr.edges, pr.look_up, pr.demand_nodes)
    logging.info("Running solve")
    sl.solve()

    pr.graph_to_geom(sl.s_edges)

    pr.solution.to_crs("epsg:4326").to_file(f"solution.shp")

if __name__ == "__main__":

    logging.basicConfig(level = logging.INFO)
    main()
