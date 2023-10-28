import configparser
import os
import warnings
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
import networkx as nx
from shapely.geometry import Polygon, MultiPolygon, mapping, shape, MultiLineString, LineString
from shapely.ops import transform, unary_union, nearest_points
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')

class PointsGenerator:

    """
    This class generates points for each polygon
    """

    def __init__(self, country_iso3):
        """
        A class constructor

        Arguments
        ---------
        country_iso3 : string
            Country iso3 to be processed.
        """
        self.country_iso3 = country_iso3

    def generate_gid_points(self):
        
        """
        This function generates geospatial sub-regional points for 
        every region.
        """
        regions = os.path.join(DATA_PROCESSED, self.country_iso3, 'regions')
        region_1 = os.path.join(regions, 'regions_1_{}.shp'.format(self.country_iso3))
        gdf1 = gpd.read_file(region_1)
        gdf1 = gdf1.to_dict('records')
        region_2 = os.path.join(regions, 'regions_2_{}.shp'.format(self.country_iso3)) 

        if os.path.exists(region_2):

            gdf2 = gpd.read_file(region_2)
            gdf2 = gdf2.to_dict('records')

            for myitem in tqdm(gdf1, desc = 'Generating geospatial points for {}'. format(self.country_iso3)):

                my_points = []

                for myitem2 in gdf2:

                    if myitem['GID_1'] == myitem2['GID_1']:

                        my_points.append({
                            'geometry': {
                                'type':'Point',
                                'coordinates': myitem2['geometry'].representative_point()   
                            },
                            'properties': {
                                'GID_2': myitem2['GID_2']
                            }
                        })
                
                mypoints = gpd.GeoDataFrame.from_features(my_points, crs='epsg:4326')

                folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'gid_points')
                fileout = '{}.shp'.format(myitem['GID_1'])

                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                
                mypoints.to_file(path_out, driver = 'ESRI Shapefile')

        else:

            regions = os.path.join(DATA_PROCESSED, self.country_iso3)
            region_2 = os.path.join(regions, 'national_outline.shp')  
            gdf2 = gpd.read_file(region_2) 
            
               
            gdf2 = gdf2.to_dict('records')

            for myitem in tqdm(gdf2, desc = 'Generating geospatial points for {}'. format(self.country_iso3)):

                my_points = []

                for myitem2 in gdf1:

                    if myitem['GID_0'] == myitem2['GID_0']:

                        my_points.append({
                            'geometry': {
                                'type':'Point',
                                'coordinates': myitem2['geometry'].representative_point()   
                            },
                            'properties': {
                                'GID_1': myitem2['GID_1']
                            }
                        })
                
                mypoints = gpd.GeoDataFrame.from_features(my_points, crs='epsg:4326')

                folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'gid_points')
                fileout = '{}.shp'.format(myitem2['GID_1'])

                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                
                mypoints.to_file(path_out, driver = 'ESRI Shapefile')


        return None


    def generate_country_points(self):
        
        """
        This function generates geospatial points for 
        every region.
        """
        regions = os.path.join(DATA_PROCESSED, self.country_iso3, 'regions')
        region_1 = os.path.join(regions, 'regions_1_{}.shp'.format(self.country_iso3))
        gdf1 = gpd.read_file(region_1)
        gdf1 = gdf1.to_dict('records')
        region_2 = os.path.join(DATA_PROCESSED, self.country_iso3, 'national_outline.shp')  
        gdf2 = gpd.read_file(region_2)  
        gdf2 = gdf2.to_dict('records')

        for myitem in tqdm(gdf2, desc = 'Generating geospatial country points for {}'. format(self.country_iso3)):

            my_points = []

            for myitem2 in gdf1:
                
                if myitem['GID_0'] == myitem2['GID_0']:

                    my_points.append({
                        'geometry': {
                            'type':'Point',
                            'coordinates': myitem2['geometry'].representative_point()   
                        },
                        'properties': {
                            'GID_1': myitem2['GID_1']
                        }
                    })
            
            mypoints = gpd.GeoDataFrame.from_features(my_points, crs = 'epsg:4326')

            folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'country_points')
            fileout = '{}.shp'.format(self.country_iso3)

            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, fileout)
            
            mypoints.to_file(path_out, driver = 'ESRI Shapefile')


        return None


class EdgeGenerator:

    """
    This class generates lines 
    connecting central coordinates 
    of sub-regions.
    """

    def __init__(self, country_iso3):
        """
        A class constructor

        Arguments
        ---------
        country_iso3 : string
            Country iso3 to be processed.
        """
        self.country_iso3 = country_iso3


    def fit_regional_node_edges(self):
        """
        This function fits edges 
        between geospatial points 
        using minimum spanning tree
        """
        input_path = os.path.join(DATA_RESULTS, self.country_iso3, 'gid_points')
        files = os.listdir(input_path)

        for file in tqdm(files, desc = 'Generating geospatial points for {}'. format(self.country_iso3)):
            
            if file.endswith('.shp'): 
                
                file_path = os.path.join(input_path, file)
                nodes = gpd.read_file(file_path, crs = 'epsg:4326')
                if len(nodes) == 1 and nodes.geometry.geom_type[0] == 'Point': #Ignore countries with single points

                    pass

                else:

                    nodes = nodes.to_crs('epsg:3857')

                    all_possible_edges = []
                    try:
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
                                            'GID_1': node2['GID_2'],
                                            'from': node1_id,
                                            'to':  node2_id,
                                            'length': line.length,
                                            'source': 'new',
                                        }
                                    })
                    except:
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
                                            'GID_1': node2['GID_1'],
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

                    edges = gpd.GeoDataFrame.from_features(edges, crs = 'epsg:3857')

                    if len(edges) > 0:

                        edges = edges.to_crs('epsg:4326')
                        fileout = str(file)
                        folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'gid_lines')
                        if not os.path.exists(folder_out):

                            os.makedirs(folder_out)

                        path_out = os.path.join(folder_out, fileout)

                        edges.to_file(path_out, driver = 'ESRI Shapefile')


        return
    

    def fit_country_node_edges(self):
        """
        This function fits edges 
        between geospatial points 
        using minimum spanning tree
        """
        input_path = os.path.join(DATA_RESULTS, self.country_iso3, 'country_points')
        files = os.listdir(input_path)

        for file in tqdm(files, desc = 'Generating geospatial country lines for {}'. format(self.country_iso3)):
            
            if file.endswith('.shp'): 
                
                file_path = os.path.join(input_path, file)
                nodes = gpd.read_file(file_path, crs = 'epsg:4326')
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
                                    'GID_1': node2['GID_1'],
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

                edges = gpd.GeoDataFrame.from_features(edges, crs = 'epsg:3857')

                if len(edges) > 0:

                    edges = edges.to_crs('epsg:4326')

                    fileout = '{}.shp'.format(self.country_iso3)
                    folder_out = os.path.join(DATA_RESULTS, self.country_iso3, 'country_lines')
                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)

                    edges.to_file(path_out, driver = 'ESRI Shapefile')
        
        
        return None