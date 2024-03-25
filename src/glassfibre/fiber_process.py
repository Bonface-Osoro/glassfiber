import configparser
import os
import warnings
import random
import math
import json
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
import networkx as nx
from rtree import index
from rasterio.mask import mask
from rasterstats import zonal_stats
from shapely.geometry import Polygon, MultiPolygon, mapping, shape, MultiLineString, LineString, Point
from shapely.ops import transform, unary_union, nearest_points
import fiona
import fiona.crs
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')


def find_nodes(country, regions):
    """
    Find key nodes.

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    threshold = country['pop_density_km2']
    settlement_size = country['settlement_size']

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 'tifs')

    interim = []
    missing_nodes = set()

    print('Working on gathering data from regional rasters')
    for idx, region in regions.iterrows():

        path = os.path.join(folder_tifs, region[GID_level] + '.tif')
        try:

            with rasterio.open(path) as src:
                data = src.read()
                data[data < threshold] = 0
                data[data >= threshold] = 1
                polygons = rasterio.features.shapes(data, transform=src.transform)
                shapes_df = gpd.GeoDataFrame.from_features(
                    [
                        {'geometry': poly, 'properties':{'value':value}}
                        for poly, value in polygons
                        if value > 0
                    ],
                    crs='epsg:4326'
                )

            geojson_region = [
                {
                    'geometry': region['geometry'],
                    'properties': {
                        GID_level: region[GID_level]
                    }
                }
            ]

            gpd_region = gpd.GeoDataFrame.from_features(
                    [
                        {'geometry': poly['geometry'],
                        'properties':{
                            GID_level: poly['properties'][GID_level]
                            }}
                        for poly in geojson_region
                    ], crs='epsg:4326'
                )

            if len(shapes_df) == 0:
                continue

            nodes = gpd.overlay(shapes_df, gpd_region, how = 'intersection')

            stats = zonal_stats(shapes_df['geometry'], path, stats =[ 'count', 
                                                                     'sum'])

            stats_df = pd.DataFrame(stats)

            nodes = pd.concat([shapes_df, stats_df], axis=1).drop(columns = 
                                                                  'value')

            nodes_subset = nodes[nodes['sum'] >= settlement_size]

            if len(nodes_subset) == 0:
                missing_nodes.add(region[GID_level])

            for idx, item in nodes_subset.iterrows():
                interim.append({
                        'geometry': item['geometry'].centroid,
                        'properties': {
                            GID_level: region[GID_level],
                            'count': item['count'],
                            'sum': item['sum']
                        }
                })

        except:
        
            pass


    return interim, missing_nodes


def get_missing_nodes(country, regions, missing_nodes, threshold, settlement_size):
    """
    Find any missing nodes

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 'tifs')

    interim = []

    for idx, region in regions.iterrows():

        if not region[GID_level] in list(missing_nodes):
            continue

        path = os.path.join(folder_tifs, region[GID_level] + '.tif')

        with rasterio.open(path) as src:
            data = src.read()
            data[data < threshold] = 0
            data[data >= threshold] = 1
            polygons = rasterio.features.shapes(data, transform=src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons
                    if value > 0
                ],
                crs='epsg:4326'
            )

        geojson_region = [
            {
                'geometry': region['geometry'],
                'properties': {
                    GID_level: region[GID_level]
                }
            }
        ]

        gpd_region = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly['geometry'],
                    'properties':{
                        GID_level: poly['properties'][GID_level]
                        }}
                    for poly in geojson_region
                ], crs='epsg:4326'
            )

        nodes = gpd.overlay(shapes_df, gpd_region, how = 'intersection')

        stats = zonal_stats(shapes_df['geometry'], path, stats = ['count', 'sum'])

        stats_df = pd.DataFrame(stats)

        nodes = pd.concat([shapes_df, stats_df], axis = 1).drop(columns = 'value')

        max_sum = nodes['sum'].max()

        nodes = nodes[nodes['sum'] > max_sum - 1]

        for idx, item in nodes.iterrows():
            interim.append({
                    'geometry': item['geometry'].centroid,
                    'properties': {
                        GID_level: region[GID_level],
                        'count': item['count'],
                        'sum': item['sum']
                    }
            })

    return interim


def fit_edges(input_path, output_path):
    """
    Fit edges to nodes using a minimum spanning tree.

    Parameters
    ----------
    path : string
        Path to nodes shapefile.

    """
    folder = os.path.dirname(output_path)
    if not os.path.exists(folder):

        os.makedirs(folder)

    nodes = gpd.read_file(input_path, crs='epsg:4326')
    nodes = nodes.to_crs('epsg:3857')

    all_possible_edges = []

    for node1_id, node1 in nodes.iterrows():

        for node2_id, node2 in nodes.iterrows():

            if node1_id != node2_id:

                geom1 = shape(node1['geometry'])
                geom2 = shape(node2['geometry'])
                line = LineString([geom1, geom2])
                all_possible_edges.append({
                    'type': 'Feature',
                    'geometry': mapping(line),
                    'properties':{
                        # 'network_layer': 'core',
                        'from': node1_id,
                        'to':  node2_id,
                        'length': line.length,
                        'source': 'new',
                    }
                })
    if len(all_possible_edges) == 0:

        return

    G = nx.Graph()

    for node_id, node in enumerate(nodes):

        G.add_node(node_id, object = node)

    for edge in all_possible_edges:

        G.add_edge(edge['properties']['from'], edge['properties']['to'],
            object=edge, weight=edge['properties']['length'])

    tree = nx.minimum_spanning_edges(G)

    edges = []

    for branch in tree:

        link = branch[2]['object']
        if link['properties']['length'] > 0:

            edges.append(link)

    try:
        edges = gpd.GeoDataFrame.from_features(edges, crs = 'epsg:3857')

        if len(edges) > 0:

            edges = edges.to_crs('epsg:4326')
            edges.to_file(output_path)

    except:

        pass

    return
    

class FiberProcess:

    """
    This class generates lines 
    connecting central coordinates 
    of sub-regions.
    """

    def __init__(self, country_iso3, country_iso2, csv_country):
        """
        A class constructor

        Arguments
        ---------
        country_iso3 : string
            Country iso3 to be processed.
        country_iso2 : string
            Country iso2 to be processed 
            (specific for fiber data).
        csv_country : string
            Name of the country metadata file.
        """
        self.country_iso3 = country_iso3
        self.country_iso2 = country_iso2
        self.csv_country = csv_country


    def process_existing_fiber(self):
        """
        Load and process existing fiber data.

        """
        iso3 = self.country_iso3
        iso2 = self.country_iso2.lower()

        folder = os.path.join(DATA_PROCESSED, iso3, 'network_existing')

        if not os.path.exists(folder):

            os.makedirs(folder)

        filename = '{}_core_edges_existing.shp'.format(iso3)
        path_output = os.path.join(folder, filename)

        if os.path.exists(path_output):

            return print('Existing fiber already processed')

        else:

            path = os.path.join(DATA_RAW, 'existing_fiber', 'SSA_existing_fiber.shp')

            shape = fiona.open(path)

            data = []

            for item in shape:

                if item['properties']['iso2'] == iso2:

                    if item['geometry']['type'] == 'LineString':

                        if int(item['properties']['live']) == 1:

                            data.append({
                                'type': 'Feature',
                                'geometry': {
                                    'type': 'LineString',
                                    'coordinates': item['geometry']['coordinates'],
                                },
                                'properties': {
                                    'operators': item['properties']['operator'],
                                    'source': 'existing'
                                }
                            })

                    if item['geometry']['type'] == 'MultiLineString':

                        if int(item['properties']['live']) == 1:
                            
                            geom = MultiLineString(item['geometry']['coordinates'])

                            for line in geom.geoms:

                                data.append({
                                    'type': 'Feature',
                                    'geometry': mapping(line),
                                    'properties': {
                                        'operators': item['properties']['operator'],
                                        'source': 'existing'
                                    }
                                })


            if len(data) == 0:

                return print('No existing infrastructure')

            data = gpd.GeoDataFrame.from_features(data)
            data.to_file(path_output, crs='epsg:4326')

        return print('Existing fiber processed')


    def find_nodes_on_existing_infrastructure(self):
        """
        Find those agglomerations which are within a buffered zone of
        existing fiber links.

        """

        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue   

            iso3 = country['iso3']

            folder = os.path.join(DATA_PROCESSED, iso3, 'network_existing')
            filename = '{}_core_nodes_existing.shp'.format(iso3)
            path_output = os.path.join(folder, filename)

            if os.path.exists(path_output):

                return print('Already found nodes on existing infrastructure')
            
            else:

                if not os.path.dirname(path_output):

                    os.makedirs(os.path.dirname(path_output))

            path = os.path.join(folder, '{}_core_edges_existing.shp').format(iso3)

            if not os.path.exists(path):

                return print('No existing infrastructure')

            existing_infra = gpd.read_file(path, crs='epsg:4326')

            existing_infra = existing_infra.to_crs(epsg=3857)
            existing_infra['geometry'] = existing_infra['geometry'].buffer(5000)
            existing_infra = existing_infra.to_crs(epsg=4326)

            path = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 'agglomerations.shp').format(iso3)
            agglomerations = gpd.read_file(path, crs='epsg:4326')

            bool_list = agglomerations.intersects(existing_infra.unary_union)

            agglomerations = pd.concat([agglomerations, bool_list], axis=1)

            agglomerations = agglomerations[agglomerations[0] == True].drop(columns=0)

            agglomerations['source'] = 'existing'

            agglomerations.to_file(path_output, crs='epsg:4326')


        return print('Found nodes on existing infrastructure')