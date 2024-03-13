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

            nodes = gpd.overlay(shapes_df, gpd_region, how='intersection')

            stats = zonal_stats(shapes_df['geometry'], path, stats=['count', 'sum'])

            stats_df = pd.DataFrame(stats)

            nodes = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

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

        G.add_node(node_id, object=node)

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
        edges = gpd.GeoDataFrame.from_features(edges, crs='epsg:3857')

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
    

    def generate_agglomeration_lut(self):
        """
        Generate a lookup table of agglomerations.

        """
        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue   

            iso3 = country['iso3']
            regional_level = country['lowest']
            GID_level = 'GID_{}'.format(regional_level)

            folder = os.path.join(DATA_PROCESSED, iso3, 'agglomerations')
            if not os.path.exists(folder):
                os.makedirs(folder)
            path_output = os.path.join(folder, 'agglomerations.shp')

            if os.path.exists(path_output):
                return print('Agglomeration processing has already completed')

            print('Working on {} agglomeration lookup table'.format(iso3))

            filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
            folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
            path = os.path.join(folder, filename)
            regions = gpd.read_file(path, crs="epsg:4326")

            path_settlements = os.path.join(DATA_PROCESSED, iso3, 'population', 'national', 'ppp_2020_1km_Aggregated.tif')
            settlements = rasterio.open(path_settlements, 'r+')
            settlements.nodata = 255
            settlements.crs = {"init": "epsg:4326"}

            folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 'tifs')
            if not os.path.exists(folder_tifs):
                os.makedirs(folder_tifs)

            for idx, region in regions.iterrows():

                bbox = region['geometry'].envelope
                geo = gpd.GeoDataFrame()
                geo = gpd.GeoDataFrame({'geometry': bbox}, index=[idx])
                coords = [json.loads(geo.to_json())['features'][0]['geometry']]

                #chop on coords
                out_img, out_transform = mask(settlements, coords, crop=True)

                # Copy the metadata
                out_meta = settlements.meta.copy()

                out_meta.update({"driver": "GTiff",
                                "height": out_img.shape[1],
                                "width": out_img.shape[2],
                                "transform": out_transform,
                                "crs": 'epsg:4326'})

                path_output = os.path.join(folder_tifs, region[GID_level] + '.tif')

                with rasterio.open(path_output, "w", **out_meta) as dest:
                        dest.write(out_img)

            print('Completed settlement.tif regional segmentation')

            nodes, missing_nodes = find_nodes(country, regions)

            missing_nodes = get_missing_nodes(country, regions, missing_nodes, 10, 10)

            nodes = nodes + missing_nodes

            nodes = gpd.GeoDataFrame.from_features(nodes, crs='epsg:4326')

            bool_list = nodes.intersects(regions['geometry'].unary_union)
            nodes = pd.concat([nodes, bool_list], axis=1)
            nodes = nodes[nodes[0] == True].drop(columns=0)

            agglomerations = []

            print('Identifying agglomerations')
            for idx1, region in regions.iterrows():
                seen = set()
                for idx2, node in nodes.iterrows():
                    if node['geometry'].intersects(region['geometry']):
                        agglomerations.append({
                            'type': 'Feature',
                            'geometry': mapping(node['geometry']),
                            'properties': {
                                'id': idx1,
                                'GID_0': region['GID_0'],
                                'GID_1': region['GID_1'],
                                GID_level: region[GID_level],
                                'population': node['sum'],
                            }
                        })
                        seen.add(region[GID_level])
                if len(seen) == 0:
                    agglomerations.append({
                            'type': 'Feature',
                            'geometry': mapping(region['geometry'].centroid),
                            'properties': {
                                'id': 'regional_node',
                                'GID_0': region['GID_0'],
                                'GID_1': region['GID_1'],
                                GID_level: region[GID_level],
                                'population': 1,
                            }
                        })

            agglomerations = gpd.GeoDataFrame.from_features(
                    [
                        {
                            'geometry': item['geometry'],
                            'properties': {
                                'id': item['properties']['id'],
                                'GID_0':item['properties']['GID_0'],
                                'GID_1': item['properties']['GID_1'],
                                GID_level: item['properties'][GID_level],
                                'population': item['properties']['population'],
                            }
                        }
                        for item in agglomerations
                    ],
                    crs='epsg:4326'
                )

            folder = os.path.join(DATA_PROCESSED, iso3, 'agglomerations')
            path_output = os.path.join(folder, '{}_agglomerations' + '.shp').format(iso3)

            agglomerations.to_file(path_output)

            agglomerations['lon'] = agglomerations['geometry'].x
            agglomerations['lat'] = agglomerations['geometry'].y
            agglomerations = agglomerations[['GID_1', GID_level, 'lon', 'lat', 'population']]
            agglomerations.to_csv(os.path.join(folder, 'agglomerations.csv'), index = False)


        return print('Agglomerations layer complete')


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

            # shape_output = os.path.join(DATA_INTERMEDIATE, iso3, 'network', 'core_edges_buffered.shp')
            # existing_infra.to_file(shape_output, crs='epsg:4326')

            path = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', '{}_agglomerations.shp').format(iso3)
            agglomerations = gpd.read_file(path, crs='epsg:4326')

            bool_list = agglomerations.intersects(existing_infra.unary_union)

            agglomerations = pd.concat([agglomerations, bool_list], axis=1)

            agglomerations = agglomerations[agglomerations[0] == True].drop(columns=0)

            agglomerations['source'] = 'existing'

            agglomerations.to_file(path_output, crs='epsg:4326')


        return print('Found nodes on existing infrastructure')
    

    def find_regional_nodes(self):
        """

        """
        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue  

            iso3 = country['iso3']

            iso_exceptions = ['BFA', 'CAF']
            
            if iso3 in iso_exceptions:

                GID_level = 'GID_2'

            else:

                regional_level = country['lowest']    
                GID_level = 'GID_{}'.format(regional_level)

            folder = os.path.join(DATA_PROCESSED, iso3)
            input_path = os.path.join(folder, 'agglomerations', '{}_agglomerations.shp').format(iso3)
            existing_nodes_path = os.path.join(folder, 'network_existing', '{}_core_nodes_existing.shp').format(iso3)
            output_path = os.path.join(folder, 'network', '{}_core_nodes.shp').format(iso3)
            regional_output_path = os.path.join(folder, 'network', 'regional_nodes')

            regions = gpd.read_file(input_path, crs = "epsg:4326")
            unique_regions = regions[GID_level].unique()

            if os.path.exists(output_path):

                return print('Regional nodes layer already generated')

            folder = os.path.dirname(output_path)
            if not os.path.exists(folder):

                os.makedirs(folder)

            if not os.path.exists(regional_output_path):

                os.makedirs(regional_output_path)

            interim = []

            for unique_region in unique_regions:

                agglomerations = []

                for idx, region in regions.iterrows():

                    if unique_region == region[GID_level]:

                        agglomerations.append({
                            'type': 'Feature',
                            'geometry': region['geometry'],
                            'properties': {
                                GID_level: region[GID_level],
                                'population': region['population'],
                                'source': 'existing',
                            }
                        })

                regional_nodes = gpd.GeoDataFrame.from_features(agglomerations, crs='epsg:4326')
                path = os.path.join(regional_output_path, unique_region + '.shp')
                regional_nodes.to_file(path)

                agglomerations = sorted(agglomerations, key=lambda k: k['properties']['population'], reverse=True)

                interim.append(agglomerations[0])

            if os.path.exists(existing_nodes_path):

                output = []
                new_nodes = []
                seen = set()

                existing_nodes = gpd.read_file(existing_nodes_path, crs='epsg:4326')
                existing_nodes = existing_nodes.to_dict('records')

                for item in existing_nodes:

                    seen.add(item[GID_level])
                    output.append({
                        'type': 'Point',
                        'geometry': mapping(item['geometry']),
                        'properties': {
                            GID_level: item[GID_level],
                            'population': item['population'],
                            'source': 'existing',
                        }
                    })

                for item in interim:

                    if not item['properties'][GID_level] in seen:
                        new_node = {
                            'type': 'Point',
                            'geometry': mapping(item['geometry']),
                            'properties': {
                                GID_level: item['properties'][GID_level],
                                'population': item['properties']['population'],
                                'source': 'new',
                            }
                        }
                        output.append(new_node)
                        new_nodes.append(new_node)

                output = gpd.GeoDataFrame.from_features(output)
                output.to_file(output_path, crs='epsg:4326')#write core nodes

                if len(new_nodes) > 0:

                    new_nodes = gpd.GeoDataFrame.from_features(new_nodes)
                    path = os.path.join(DATA_PROCESSED, iso3, 'network', 'new_nodes.shp')
                    new_nodes.to_file(path, crs='epsg:4326')#write core nodes

            if not os.path.exists(output_path):

                output = gpd.GeoDataFrame.from_features(
                    [
                        {'geometry': item['geometry'], 'properties': item['properties']}
                        for item in interim
                    ],
                    crs='epsg:4326'
                )
                output['source'] = 'new'
                output.to_file(output_path)#write core nodes

            output = []

            for unique_region in unique_regions:

                path = os.path.join(regional_output_path, unique_region + '.shp')
                if os.path.exists(path):

                    regional_nodes = gpd.read_file(path, crs='epsg:4326')

                    for idx, regional_node in regional_nodes.iterrows():
                        
                        output.append({
                            'geometry': regional_node['geometry'],
                            'properties': {
                                'GID_2' : unique_region,
                                'value': regional_node['population'],
                                'source': 'new',
                            }
                        })
            output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
            path = os.path.join(folder, 'regional_nodes.shp')
            output.to_file(path)

        return print('Completed regional node estimation')
      

    def prepare_edge_fitting(self):

        """

        """
        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue  

            iso3 = country['iso3']
            folder = os.path.join(DATA_PROCESSED, country['iso3'])
            core_edges_path = os.path.join(folder, 'network_existing', '{}_core_edges_existing.shp').format(iso3)

            if not os.path.exists(core_edges_path):

                input_path = os.path.join(folder, 'network', '{}_core_nodes.shp').format(iso3)
                output_path = os.path.join(folder, 'network', '{}_core_edges.shp').format(iso3)
                fit_edges(input_path, output_path)

            else:

                core_nodes_path = os.path.join(folder, 'network_existing', '{}_core_nodes_existing.shp').format(iso3)
                fiber_exceptions = ['GAB', 'MDG']

                if country['iso3'] in fiber_exceptions:

                    core_nodes_path = os.path.join(DATA_RESULTS, iso3, 'country_points', '{}.shp').format(iso3)
                    existing_nodes = gpd.read_file(core_nodes_path, crs = 'epsg:4326')
                    
                else:

                    existing_nodes = gpd.read_file(core_nodes_path, crs = 'epsg:4326')
                
                path = os.path.join(folder, 'network', 'new_nodes.shp')

                output = []

                if os.path.exists(path):

                    new_nodes = gpd.read_file(path, crs='epsg:4326')

                    for idx, new_node in new_nodes.iterrows():

                        nearest = nearest_points(new_node.geometry, existing_nodes.unary_union)[1]

                        geom = LineString([
                                    (
                                        new_node['geometry'].coords[0][0],
                                        new_node['geometry'].coords[0][1]
                                    ),
                                    (
                                        nearest.coords[0][0],
                                        nearest.coords[0][1]
                                    ),
                                ])

                        output.append({
                            'type': 'LineString',
                            'geometry': mapping(geom),
                            'properties': {
                                'id': idx,
                                'source': 'new'
                            }
                        })

                existing_edges = gpd.read_file(core_edges_path, crs='epsg:4326')

                for idx, existing_edge in existing_edges.iterrows():
                    output.append({
                        'type': 'LineString',
                        'geometry': mapping(existing_edge['geometry']),
                        'properties': {
                            'id': idx,
                            'source': 'existing'
                        }
                    })

                output = gpd.GeoDataFrame.from_features(output)
                path = os.path.join(folder, 'network', '{}_core_edges.shp').format(iso3)
                output.to_file(path, crs='epsg:4326')


    def fit_regional_edges(self):
        """

        """
        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue  

            iso3 = country['iso3']
            regional_level = country['lowest']
            GID_level = 'GID_{}'.format(regional_level)

            folder = os.path.join(DATA_PROCESSED, iso3, 'network')
            path = os.path.join(folder, '{}_core_nodes.shp').format(iso3)

            nodes = gpd.read_file(path, crs = "epsg:4326")
            unique_regions = nodes[GID_level].unique()

            for unique_region in unique_regions:

                input_path = os.path.join(folder, 'regional_nodes', unique_region + '.shp')
                output_path = os.path.join(DATA_PROCESSED, country['iso3'], 'network', 'regional_edges', unique_region + '.shp')
                fit_edges(input_path, output_path)
            
            output = []

            for unique_region in unique_regions:

                path = os.path.join(DATA_PROCESSED, country['iso3'], 'network', 'regional_edges', unique_region + '.shp')
                if os.path.exists(path):
                    regional_edges = gpd.read_file(path, crs='epsg:4326')

                    for idx, regional_edge in regional_edges.iterrows():
                        output.append({
                            'geometry': regional_edge['geometry'],
                            'properties': {
                                'value': regional_edge['length'],
                                'source': 'new',
                            }
                        })
        try:
            output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
            path = os.path.join(folder, 'regional_edges.shp')
            output.to_file(path)

        except:
            pass

        return print('Regional edge fitting complete')
    

    def generate_core_lut(self):
        """
        Generate core lut.

        """
        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue  

            iso3 = country['iso3']
            level = country['lowest']
            regional_level = 'GID_{}'.format(level)

            filename = '{}_core_lut.csv'.format(iso3)
            folder = os.path.join(DATA_RESULTS, iso3, 'fiber_design')

            if not os.path.exists(folder):

                os.makedirs(folder)

            output_path = os.path.join(folder, filename)

            filename = 'regions_{}_{}.shp'.format(level, iso3)
            folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
            path = os.path.join(folder, filename)
            regions = gpd.read_file(path)
            regions.crs = 'epsg:4326'

            output = []

            path = os.path.join(DATA_PROCESSED, iso3, 'network', '{}_core_edges.shp').format(iso3)

            if os.path.exists(path):

                core_edges = gpd.read_file(path)
                core_edges.crs = 'epsg:4326'
                core_edges = gpd.GeoDataFrame(
                    {'geometry': core_edges['geometry'], 'source': core_edges['source']})

                existing_edges = core_edges.loc[core_edges['source'] == 'existing']
                existing_edges = gpd.clip(regions, existing_edges)
                existing_edges = existing_edges.to_crs('epsg:3857')
                existing_edges['length'] = existing_edges['geometry'].length

            else:

                path = os.path.join(DATA_PROCESSED, iso3, 'network', 'regional_edges.shp').format(iso3)
                core_edges = gpd.read_file(path)
                core_edges.crs = 'epsg:4326'
                core_edges = gpd.GeoDataFrame(
                    {'geometry': core_edges['geometry'], 'source': core_edges['source']})

                existing_edges = core_edges.loc[core_edges['source'] == 'existing']
                existing_edges = gpd.clip(regions, existing_edges)
                existing_edges = existing_edges.to_crs('epsg:3857')
                existing_edges['length'] = existing_edges['geometry'].length

            for idx, edge in existing_edges.iterrows():

                output.append({
                    'GID_id': edge[regional_level],
                    'asset': 'core_edge',
                    'value': edge['length'],
                    'source': 'existing',
                })

            new_edges = core_edges.loc[core_edges['source'] == 'new']
            new_edges = gpd.clip(regions, new_edges)
            new_edges = new_edges.to_crs('epsg:3857')
            new_edges['length'] = new_edges['geometry'].length

            for idx, edge in new_edges.iterrows():
                output.append({
                    'GID_id': edge[regional_level],
                    'asset': 'core_edge',
                    'value': edge['length'],
                    'source': 'new',
                })


            path = os.path.join(DATA_PROCESSED, iso3, 'network', 'regional_edges.shp')
            if os.path.exists(path):

                regional_edges = gpd.read_file(path, crs='epsg:4326')
                regional_edges = gpd.clip(regions, regional_edges)
                regional_edges = regional_edges.to_crs('epsg:3857')
                regional_edges['length'] = regional_edges['geometry'].length

                for idx, edge in regional_edges.iterrows():

                    output.append({
                        'GID_id': edge[regional_level],
                        'asset': 'regional_edge',
                        'value': edge['length'],
                        'source': 'new', #all regional edges are assumed to be new
                    })

            path = os.path.join(DATA_PROCESSED, iso3, 'network', '{}_core_nodes.shp').format(iso3)
            nodes = gpd.read_file(path, crs='epsg:4326')

            existing_nodes = nodes.loc[nodes['source'] == 'existing']
            f = lambda x:np.sum(existing_nodes.intersects(x))
            regions['nodes'] = regions['geometry'].apply(f)

            for idx, region in regions.iterrows():
                output.append({
                    'GID_id': region[regional_level],
                    'asset': 'core_node',
                    'value': region['nodes'],
                    'source': 'existing',
                })

            new_nodes = nodes.loc[nodes['source'] == 'new']
            f = lambda x:np.sum(new_nodes.intersects(x))
            regions['nodes'] = regions['geometry'].apply(f)

            for idx, region in regions.iterrows():

                output.append({
                    'GID_id': region[regional_level],
                    'asset': 'core_node',
                    'value': region['nodes'],
                    'source': 'new',
                })

            path = os.path.join(DATA_PROCESSED, iso3, 'network', 'regional_nodes.shp')
            regional_nodes = gpd.read_file(path, crs='epsg:4326')

            existing_nodes = regional_nodes.loc[regional_nodes['source'] == 'existing']
            f = lambda x:np.sum(existing_nodes.intersects(x))
            regions['regional_nodes'] = regions['geometry'].apply(f)

            for idx, region in regions.iterrows():

                output.append({
                    'GID_id': region[regional_level],
                    'asset': 'regional_node',
                    'value': region['regional_nodes'],
                    'source': 'existing',
                })

            new_nodes = regional_nodes.loc[regional_nodes['source'] == 'new']
            f = lambda x:np.sum(new_nodes.intersects(x))
            regions['regional_nodes'] = regions['geometry'].apply(f)

            for idx, region in regions.iterrows():

                output.append({
                    'GID_id': region[regional_level],
                    'asset': 'regional_node',
                    'value': region['regional_nodes'],
                    'source': 'new',
                })

            output = pd.DataFrame(output)
            output = output.drop_duplicates()
            output.to_csv(output_path, index=False)

        return print('Completed core lut')
    

    def generate_backhaul_lut(self):
        """
        Simulate backhaul distance given a 100km^2 area.
        Simulations show that for every 10x increase in node density,
        there is a 3.2x decrease in backhaul length.

        node_density_km2	average_distance_km
        0.000001	606.0	10	 3.2
        0.00001	189.0	10	 3.8
        0.0001	50.0	10	 3.1
        0.001	16.0	10	 3.2
        0.01	5.0	10	 3.2
        0.1	1.6	10	 3.2
        1	0.5

        """
        countries = pd.read_csv(self.csv_country, encoding = 'utf-8-sig')

        for idx, country in countries.iterrows():

            if not country['iso3'] == self.country_iso3: 

                continue  

            iso3 = country['iso3']
            filename = '{}_backhaul_lut.csv'.format(iso3)
            folder = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
            path = os.path.join(folder, filename)

            if os.path.exists(path):

                return print('Backhaul LUT already generated')

            output = []

            number_of_regional_nodes_range = [1, 10, 100, 1000, 10000]

            area_km2 = 1e6

            for number_of_regional_nodes in number_of_regional_nodes_range:

                sites = []

                for i in range(1, int(round(max(number_of_regional_nodes_range) + 1))):

                    x = random.uniform(0, round(math.sqrt(area_km2)))
                    y = random.uniform(0, round(math.sqrt(area_km2)))
                    sites.append({
                        'geometry': {
                            'type': 'Point',
                            'coordinates': (x, y)
                        },
                        'properties': {
                            'id': i
                        }
                    })

                regional_nodes = []

                for i in range(1, number_of_regional_nodes + 1):

                    x = random.uniform(0, round(math.sqrt(area_km2)))
                    y = random.uniform(0, round(math.sqrt(area_km2)))
                    regional_nodes.append({
                        'geometry': {
                            'type': 'Point',
                            'coordinates': (x, y)
                        },
                        'properties': {
                            'id': i
                        }
                    })

                distances = []

                idx = index.Index()

                for regional_node in regional_nodes:

                    idx.insert(
                        regional_node['properties']['id'],
                        shape(regional_node['geometry']).bounds,
                        regional_node)

                for site in sites:

                    geom1 = shape(site['geometry'])

                    nearest_regional_node = [i for i in idx.nearest((geom1.bounds))][0]

                    for regional_node in regional_nodes:

                        if regional_node['properties']['id'] == nearest_regional_node:

                            x1 = site['geometry']['coordinates'][0]
                            x2 = regional_node['geometry']['coordinates'][0]
                            y1 = site['geometry']['coordinates'][1]
                            y2 = regional_node['geometry']['coordinates'][1]

                            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                            distances.append(distance)

                output.append({
                    'node_density_km2': round(number_of_regional_nodes / area_km2, 8),
                    'average_distance_km': int(round(sum(distances) / len(distances))),
                })

            output = pd.DataFrame(output)
            output.to_csv(path, index=False)

        return print('Completed backhaul LUT processing') 
    
DATA_RAW = os.path.join(BASE_PATH, 'raw')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'utf-8-sig')

for idx, country in countries.iterrows():
        
    if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    #if not country['iso3'] == 'LSO':

        continue

    fiber_processor = FiberProcess(countries['iso3'].loc[idx], countries['iso2'].loc[idx], path)
    '''fiber_processor.process_existing_fiber()
    fiber_processor.generate_agglomeration_lut()
    fiber_processor.find_nodes_on_existing_infrastructure()
    fiber_processor.find_regional_nodes()
    fiber_processor.prepare_edge_fitting()
    fiber_processor.fit_regional_edges()
    fiber_processor.generate_core_lut()
    fiber_processor.generate_backhaul_lut()'''
    fiber_processor.generate_agglomeration_lut()


#file = os.path.join(DATA_PROCESSED, 'KEN', 'network_existing', 'KEN_core_edges_existing.shp')
#df = gpd.read_file(file, crs='epsg:4326')
#print(df.head(3))
