import configparser
import os
import warnings
import random
import math
import json
import rasterio
import fiona
import fiona.crs

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx

from tqdm import tqdm
from rtree import index
from rasterio.mask import mask
from rasterstats import zonal_stats
from shapely.ops import transform, unary_union, nearest_points
from shapely.geometry import (Polygon, MultiPolygon, mapping, shape, 
                              MultiLineString, LineString, Point)


pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESSED = os.path.join(BASE_PATH, '..', 'results', 'processed')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'utf-8-sig')


def process_regional_settlement_tifs(country):
    """
    This function generates settlement rasters for regions.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """

    iso3 = country['iso3']
    GID_level = 'GID_1'
    main_settlement_size = country['main_settlement_size']

    folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
    if not os.path.exists(folder):

        os.makedirs(folder)

    path_output = os.path.join(folder, 'regional_settlements.shp')
    filename = 'regions_1_{}.shp'.format(iso3)
    folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs = "epsg:4326")#[:20]
    regions = regions.loc[regions.is_valid]

    path_settlements = os.path.join(DATA_PROCESSED, iso3, 'population', 
                       'national', 'ppp_2020_1km_Aggregated.tif')
    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 0
    settlements.crs = {"init": "epsg:4326"}

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'settlements', 'reg_tifs')
    if not os.path.exists(folder_tifs):

        os.makedirs(folder_tifs)

    for idx, region in regions.iterrows():

        path_output = os.path.join(folder_tifs, region[GID_level] + '.tif')

        bbox = region['geometry'].envelope

        geo = gpd.GeoDataFrame()
        geo = gpd.GeoDataFrame({'geometry': bbox}, index = [idx], crs = 
                               'epsg:4326')
        coords = [json.loads(geo.to_json())['features'][0]['geometry']]
        out_img, out_transform = mask(settlements, coords, crop = True)
        out_meta = settlements.meta.copy()

        out_meta.update({'driver': 'GTiff',
                        'height': out_img.shape[1],
                        'width': out_img.shape[2],
                        'transform': out_transform})
       
        with rasterio.open(path_output, 'w', **out_meta) as dest:
                dest.write(out_img) 

    return None


def process_access_settlement_tifs(country):
    """
    This function generates settlement rasters for access (gid 2 levels)

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.
    """

    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
    if not os.path.exists(folder):

        os.makedirs(folder)

    path_output = os.path.join(folder, 'access_settlements.shp')
    filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
    folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs = "epsg:4326")#[:20]
    regions = regions.loc[regions.is_valid]

    path_settlements = os.path.join(DATA_PROCESSED, iso3, 'population', 
                       'national', 'ppp_2020_1km_Aggregated.tif')
    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 0
    settlements.crs = {"init": "epsg:4326"}

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'settlements', 'tifs')
    if not os.path.exists(folder_tifs):

        os.makedirs(folder_tifs)

    for idx, region in regions.iterrows():

        path_output = os.path.join(folder_tifs, region[GID_level] + '.tif')

        bbox = region['geometry'].envelope

        geo = gpd.GeoDataFrame()
        geo = gpd.GeoDataFrame({'geometry': bbox}, index = [idx], crs = 
                               'epsg:4326')
        coords = [json.loads(geo.to_json())['features'][0]['geometry']]
        out_img, out_transform = mask(settlements, coords, crop = True)
        out_meta = settlements.meta.copy()

        out_meta.update({'driver': 'GTiff',
                        'height': out_img.shape[1],
                        'width': out_img.shape[2],
                        'transform': out_transform})
       
        with rasterio.open(path_output, 'w', **out_meta) as dest:
                dest.write(out_img) 

    return None


def generate_regional_settlement_lut(country):
    """
    Generate a lookup table of all settlements over the defined
    settlement thresholds for the country being modeled.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """
    iso3 = country['iso3']
    GID_level = 'GID_1'
    main_settlement_size = country['main_settlement_size']

    folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
    if not os.path.exists(folder):

        os.makedirs(folder)

    path_output = os.path.join(folder, 'regional_settlements.shp')

    filename = 'regions_1_{}.shp'.format(iso3)
    folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs = "epsg:4326")#[:20]
    regions = regions.loc[regions.is_valid]

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'settlements', 'reg_tifs')
    if not os.path.exists(folder_tifs):

        os.makedirs(folder_tifs)

    print('Working on gathering data from {} regional rasters'.format(iso3))
    for idx, region in regions.iterrows():

        nodes = find_regional_nodes(country, regions)
        nodes = gpd.GeoDataFrame.from_features(nodes, crs = 'epsg:4326')
        bool_list = nodes.intersects(regions['geometry'].unary_union)
        nodes = pd.concat([nodes, bool_list], axis = 1)
        nodes = nodes[nodes[0] == True].drop(columns = 0)
        
        settlements = []
        for idx1, region in regions.iterrows():

            seen = set()
            for idx2, node in nodes.iterrows():

                if node['geometry'].intersects(region['geometry']):

                    if node['sum'] > 0:

                        settlements.append({
                            'type': 'Feature',
                            'geometry': mapping(node['geometry']),
                            'properties': {
                                'id': idx1,
                                'GID_0': region['GID_0'],
                                GID_level: region[GID_level],
                                'population': node['sum'],
                                'type': node['type'],
                            }
                        })
                        seen.add(region[GID_level])

        settlements = gpd.GeoDataFrame.from_features(
                [
                    {
                        'geometry': item['geometry'],
                        'properties': {
                            'iso3': iso3,
                            'id': item['properties']['id'],
                            'GID_0':item['properties']['GID_0'],
                            GID_level: item['properties'][GID_level],
                            'population': item['properties']['population'],
                            'type': item['properties']['type'],
                        }
                    }
                    for item in settlements
                ],
                crs='epsg:4326'
            )
        settlements['lon'] = round(settlements['geometry'].x, 5)
        settlements['lat'] = round(settlements['geometry'].y, 5)
        settlements = settlements.drop_duplicates(subset=['lon', 'lat'])

        folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
        path_output = os.path.join(folder, 'regional_settlements' + '.shp')
        settlements.to_file(path_output)

        folder = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure')
        if not os.path.exists(folder):
            
            os.makedirs(folder)

        path_output = os.path.join(folder, 'regional_nodes' + '.shp')
        main_nodes = settlements.loc[settlements['population'] >= 
                                     main_settlement_size]
        main_nodes.to_file(path_output)
        settlements = settlements[['iso3', 'lon', 'lat', GID_level, 'population'
                                   , 'type']]
        settlements.to_csv(os.path.join(folder, 'regional_settlements.csv'), index = 
                           False)
    
    return None


def generate_access_settlement_lut(country):
    """
    Generate a lookup table of all settlements over the defined
    settlement thresholds for the country being modeled.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)
    main_settlement_size = country['main_settlement_size']

    folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
    if not os.path.exists(folder):

        os.makedirs(folder)

    path_output = os.path.join(folder, 'access_settlements.shp')

    filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
    folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs = "epsg:4326")#[:20]
    regions = regions.loc[regions.is_valid]

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'settlements', 'tifs')
    if not os.path.exists(folder_tifs):

        os.makedirs(folder_tifs)

    print('Working on gathering data from {} sub-regional rasters'.format(iso3))
    for idx, region in regions.iterrows():

        nodes = find_access_nodes(country, regions)
        nodes = gpd.GeoDataFrame.from_features(nodes, crs = 'epsg:4326')
        bool_list = nodes.intersects(regions['geometry'].unary_union)
        nodes = pd.concat([nodes, bool_list], axis = 1)
        nodes = nodes[nodes[0] == True].drop(columns = 0)
        
        settlements = []
        for idx1, region in regions.iterrows():

            seen = set()
            for idx2, node in nodes.iterrows():

                if node['geometry'].intersects(region['geometry']):

                    if node['sum'] > 0:

                        settlements.append({
                            'type': 'Feature',
                            'geometry': mapping(node['geometry']),
                            'properties': {
                                'id': idx1,
                                'GID_0': region['GID_0'],
                                GID_level: region[GID_level],
                                'population': node['sum'],
                                'type': node['type'],
                            }
                        })
                        seen.add(region[GID_level])

        settlements = gpd.GeoDataFrame.from_features(
                [
                    {
                        'geometry': item['geometry'],
                        'properties': {
                            'iso3': iso3,
                            'id': item['properties']['id'],
                            'GID_0':item['properties']['GID_0'],
                            GID_level: item['properties'][GID_level],
                            'population': item['properties']['population'],
                            'type': item['properties']['type'],
                        }
                    }
                    for item in settlements
                ],
                crs='epsg:4326'
            )
        settlements['lon'] = round(settlements['geometry'].x, 5)
        settlements['lat'] = round(settlements['geometry'].y, 5)
        settlements = settlements.drop_duplicates(subset=['lon', 'lat'])

        folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
        path_output = os.path.join(folder, 'access_settlements' + '.shp')
        settlements.to_file(path_output)

        folder = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure')
        if not os.path.exists(folder):
            
            os.makedirs(folder)

        path_output = os.path.join(folder, 'access_nodes' + '.shp')
        main_nodes = settlements.loc[settlements['population'] >= 
                                     main_settlement_size]
        main_nodes.to_file(path_output)
        settlements = settlements[['iso3', 'lon', 'lat', GID_level, 'population'
                                   , 'type']]
        settlements.to_csv(os.path.join(folder, 'access_settlements.csv'), index = 
                           False)
    
    return None


def find_regional_nodes(country, regions):
    """
    Find key nodes in each region.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.
    regions : dataframe
        Pandas df containing all regions for modeling.

    Returns
    -------
    interim : list of dicts

    """
    iso3 = country['iso3']
    GID_level = 'GID_1'

    threshold = country['pop_density_km2']
    settlement_size = country['settlement_size']

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'settlements', 'reg_tifs')
    interim = []
    for idx, region in regions.iterrows():
        
        path = os.path.join(folder_tifs, region[GID_level] + '.tif')
        with rasterio.open(path) as src: # convert raster to pandas geodataframe

            data = src.read()
            data[data < threshold] = 0
            data[data >= threshold] = 1
            polygons = rasterio.features.shapes(data, transform = src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [{'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons if value > 0])

        if len(shapes_df) == 0: #if you put the crs in the preceeding function
                                #there is an error for an empty df
            continue            

        shapes_df = shapes_df.set_crs('epsg:4326')

        geojson_region = [
            {'geometry': region['geometry'],
            'properties': {GID_level: region[GID_level]}}]
        
        gpd_region = gpd.GeoDataFrame.from_features(
                [{'geometry': poly['geometry'],
                    'properties':{GID_level: poly['properties'][GID_level]}}
                    for poly in geojson_region])
        
        if len(gpd_region) == 0: 

            continue      

        gpd_region = gpd_region.set_crs('epsg:4326')
        nodes = gpd.overlay(shapes_df, gpd_region, how = 'intersection')
        
        results = []
        for idx, node in nodes.iterrows():

            pop = zonal_stats(node['geometry'], path, nodata = 0,
                              stats = ['sum'])
            
            if not pop[0]['sum'] == None and pop[0]['sum'] > settlement_size:

                results.append({'geometry': node['geometry'], 
                                'properties': {'{}'.format(GID_level): 
                                               node[GID_level], 
                                               'sum': pop[0]['sum']},})
                
        nodes = gpd.GeoDataFrame.from_features([{
                'geometry': item['geometry'],
                'properties': {
                        '{}'.format(GID_level): item['properties'][GID_level],
                        'sum': item['properties']['sum'],},}
                for item in results])
        
        nodes = nodes.drop_duplicates()
        if len(nodes) == 0: 

            continue    

        nodes = nodes.set_crs('epsg:4326')
        nodes.loc[(nodes['sum'] >= 20000), 'type'] = '>20k'
        nodes.loc[(nodes['sum'] <= 10000) | (nodes['sum'] < 20000), 
                  'type'] = '10-20k'
        nodes.loc[(nodes['sum'] <= 5000) | (nodes['sum'] < 10000), 
                  'type'] = '5-10k'
        nodes.loc[(nodes['sum'] <= 1000) | (nodes['sum'] < 5000), 
                  'type'] = '1-5k'
        nodes.loc[(nodes['sum'] <= 500) | (nodes['sum'] < 1000), 
                  'type'] = '0.5-1k'
        nodes.loc[(nodes['sum'] <= 250) | (nodes['sum'] < 500), 
                  'type'] = '0.25-0.5k'
        nodes.loc[(nodes['sum'] <= 250), 'type'] = '<0.25k'

        nodes = nodes.dropna()

        for idx, item in nodes.iterrows():
            if item['sum'] > 0:
                interim.append({
                        'geometry': item['geometry'].centroid,
                        'properties': {
                            GID_level: region[GID_level],
                            'sum': item['sum'],
                            'type': item['type'],
                        },
                })

    
    return interim


def find_access_nodes(country, regions):
    """
    Find key nodes in each region.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.
    regions : dataframe
        Pandas df containing all regions for modeling.

    Returns
    -------
    interim : list of dicts

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    threshold = country['pop_density_km2']
    settlement_size = country['settlement_size']

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'settlements', 'tifs')
    interim = []
    for idx, region in regions.iterrows():
        
        path = os.path.join(folder_tifs, region[GID_level] + '.tif')
        with rasterio.open(path) as src: # convert raster to pandas geodataframe

            data = src.read()
            data[data < threshold] = 0
            data[data >= threshold] = 1
            polygons = rasterio.features.shapes(data, transform = src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [{'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons if value > 0])

        if len(shapes_df) == 0: #if you put the crs in the preceeding function
                                #there is an error for an empty df
            continue            

        shapes_df = shapes_df.set_crs('epsg:4326')

        geojson_region = [
            {'geometry': region['geometry'],
            'properties': {GID_level: region[GID_level]}}]
        
        gpd_region = gpd.GeoDataFrame.from_features(
                [{'geometry': poly['geometry'],
                    'properties':{GID_level: poly['properties'][GID_level]}}
                    for poly in geojson_region])
        
        if len(gpd_region) == 0: 

            continue      

        gpd_region = gpd_region.set_crs('epsg:4326')
        nodes = gpd.overlay(shapes_df, gpd_region, how = 'intersection')
        
        results = []
        for idx, node in nodes.iterrows():

            pop = zonal_stats(node['geometry'], path, nodata = 0,
                              stats = ['sum'])
            
            if not pop[0]['sum'] == None and pop[0]['sum'] > settlement_size:

                results.append({'geometry': node['geometry'], 
                                'properties': {'{}'.format(GID_level): 
                                               node[GID_level], 
                                               'sum': pop[0]['sum']},})
                
        nodes = gpd.GeoDataFrame.from_features([{
                'geometry': item['geometry'],
                'properties': {
                        '{}'.format(GID_level): item['properties'][GID_level],
                        'sum': item['properties']['sum'],},}
                for item in results])
        
        nodes = nodes.drop_duplicates()
        if len(nodes) == 0: 

            continue    

        nodes = nodes.set_crs('epsg:4326')
        nodes.loc[(nodes['sum'] >= 20000), 'type'] = '>20k'
        nodes.loc[(nodes['sum'] <= 10000) | (nodes['sum'] < 20000), 
                  'type'] = '10-20k'
        nodes.loc[(nodes['sum'] <= 5000) | (nodes['sum'] < 10000), 
                  'type'] = '5-10k'
        nodes.loc[(nodes['sum'] <= 1000) | (nodes['sum'] < 5000), 
                  'type'] = '1-5k'
        nodes.loc[(nodes['sum'] <= 500) | (nodes['sum'] < 1000), 
                  'type'] = '0.5-1k'
        nodes.loc[(nodes['sum'] <= 250) | (nodes['sum'] < 500), 
                  'type'] = '0.25-0.5k'
        nodes.loc[(nodes['sum'] <= 250), 'type'] = '<0.25k'

        nodes = nodes.dropna()

        for idx, item in nodes.iterrows():
            if item['sum'] > 0:
                interim.append({
                        'geometry': item['geometry'].centroid,
                        'properties': {
                            GID_level: region[GID_level],
                            'sum': item['sum'],
                            'type': item['type'],
                        },
                })

    
    return interim


def generate_agglomeration_lut(country):
    """
    Generate a lookup table of agglomerations.
    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    core_node_level = 'GID_{}'.format(country['gid_region'])
    regional_node_level = 'GID_{}'.format(country['lowest'])

    folder = os.path.join(DATA_PROCESSED, iso3, 'agglomerations')
    if not os.path.exists(folder):

        os.makedirs(folder)

    path_output = os.path.join(folder, 'agglomerations.shp')
    if os.path.exists(path_output):

        return print('Agglomeration processing has {} already completed'.format(
            iso3))
    
    print('Working on {} agglomeration lookup table'.format(iso3))
    filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
    folder = os.path.join(DATA_PROCESSED, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs = 'epsg:4326')

    path_settlements = os.path.join(DATA_PROCESSED, iso3, 'population', 
                                    'national', 'ppp_2020_1km_Aggregated.tif')
    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {'init': 'epsg:4326'}
    
    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 'tifs')
    if not os.path.exists(folder_tifs):

        os.makedirs(folder_tifs)

    for idx, region in regions.iterrows():

        path_output = os.path.join(folder_tifs, region[GID_level] + '.tif')

        if os.path.exists(path_output):

            continue

        geo = gpd.GeoDataFrame(geometry = gpd.GeoSeries(region['geometry']))
        coords = [json.loads(geo.to_json())['features'][0]['geometry']]
        out_img, out_transform = mask(settlements, coords, crop = True)
        out_meta = settlements.meta.copy()

        out_meta.update({'driver': 'GTiff',
                        'height': out_img.shape[1],
                        'width': out_img.shape[2],
                        'transform': out_transform,
                        'crs': 'epsg:4326'})
        
        with rasterio.open(path_output, 'w', **out_meta) as dest:
                
                dest.write(out_img)

    print('Completed settlement.tif regional segmentation')

    nodes, missing_nodes = find_settlement_nodes(country, regions)
    nodes = gpd.GeoDataFrame.from_features(nodes, crs = 'epsg:4326')
    bool_list = nodes.intersects(regions['geometry'].unary_union)
    nodes = pd.concat([nodes, bool_list], axis = 1)
    nodes = nodes[nodes[0] == True].drop(columns = 0)
    
    agglomerations = []
    print('Identifying agglomerations')
    for idx1, region in regions.iterrows():

        seen_coords = set()
        for idx2, node in nodes.iterrows():

            if node['geometry'].intersects(region['geometry']):

                x = float(str(node['geometry'].x)[:12])
                y = float(str(node['geometry'].y)[:12])
                coord = '{}_{}'.format(x ,y)

                if coord in seen_coords:

                    continue    

                agglomerations.append({
                    'type': 'Feature',
                    'geometry': mapping(node['geometry']),
                    'properties': {
                        'id': idx1,
                        'GID_0': region['GID_0'],
                        'GID_1': region['GID_1'],
                        GID_level: region[GID_level],
                        core_node_level: region[core_node_level],
                        regional_node_level: region[regional_node_level],
                        'population': node['sum'],}})
                
                seen_coords.add(coord)
        
        if len(seen_coords) == 0:
            
            pop_tif = os.path.join(folder_tifs, region[GID_level] + '.tif')

            with rasterio.open(pop_tif) as src:
                
                data = src.read()
                polygons = rasterio.features.shapes(data, transform = 
                                                    src.transform)
                shapes_df = gpd.GeoDataFrame.from_features(
                    [
                        {'geometry': poly, 'properties':{'value':value}}
                        for poly, value in polygons],crs = 'epsg:4326')
                
                shapes_df = shapes_df.nlargest(1, columns = ['value'])

                shapes_df['geometry'] = shapes_df['geometry'].to_crs('epsg:3857')
                shapes_df['geometry'] = shapes_df['geometry'].centroid
                shapes_df['geometry'] = shapes_df['geometry'].to_crs('epsg:4326')
                geom = shapes_df['geometry'].values[0]

                x = float(str(node['geometry'].x)[:12])
                y = float(str(node['geometry'].y)[:12])
                coord = '{}_{}'.format(x ,y)

                if coord in seen_coords:

                    continue 

                agglomerations.append({
                        'type': 'Feature',
                        'geometry': mapping(geom),
                        'properties': {
                            'id': 'regional_node',
                            'GID_0': region['GID_0'],
                            'GID_1': region['GID_1'],
                            GID_level: region[GID_level],
                            core_node_level: region[core_node_level],
                            regional_node_level: region[regional_node_level],
                            'population': shapes_df['value'].values[0],}})
    
    agglomerations = gpd.GeoDataFrame.from_features(
            [
                {
                    'geometry': item['geometry'],
                    'properties': {
                        'id': item['properties']['id'],
                        'GID_0':item['properties']['GID_0'],
                        'GID_1':item['properties']['GID_1'],
                        GID_level: item['properties'][GID_level],
                        core_node_level: item['properties'][core_node_level],
                        regional_node_level: item['properties'][regional_node_level],
                        'population': item['properties']['population'],
                    }}
                for item in agglomerations
            ],crs = 'epsg:4326')             
    agglomerations = agglomerations.drop_duplicates(subset = ['geometry']
                                                    ).reset_index()
    
    folder = os.path.join(DATA_PROCESSED, iso3, 'agglomerations')
    path_output = os.path.join(folder, 'agglomerations' + '.shp')
    agglomerations.to_file(path_output)

    agglomerations['lon'] = agglomerations['geometry'].x
    agglomerations['lat'] = agglomerations['geometry'].y
    agglomerations = agglomerations[['GID_1', GID_level, 'lon', 'lat', 
                                     'population']]
    agglomerations = agglomerations.drop_duplicates(subset = ['lon', 'lat']
                                                    ).reset_index()
    agglomerations.to_csv(os.path.join(folder, 'agglomerations.csv'), index = 
                          False)

    return print('Agglomerations layer complete for {}'.format(iso3))


def find_settlement_nodes(country, regions):
    """
    Find key nodes.
    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    core_node_level = 'GID_{}'.format(country['gid_region'])
    regional_node_level = 'GID_{}'.format(country['lowest'])

    threshold = country['pop_density_km2']
    settlement_size = country['settlement_size']

    folder_tifs = os.path.join(DATA_PROCESSED, iso3, 'agglomerations', 'tifs')
    interim = []
    missing_nodes = set()

    print('Working on gathering data from regional rasters') 
    for idx, region in regions.iterrows():
        
        path = os.path.join(folder_tifs, region[GID_level] + '.tif')

        with rasterio.open(path) as src:

            data = src.read()
            data[data < threshold] = 0
            data[data >= threshold] = 1
            polygons = rasterio.features.shapes(data, transform = src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [{'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons
                    if value > 0])
        
        if len(shapes_df) == 0:

            continue

        shapes_df = shapes_df.set_crs('epsg:4326')
        geojson_region = [
            {'geometry': region['geometry'],
                'properties': {
                    GID_level: region[GID_level],
                    core_node_level: region[core_node_level],
                    regional_node_level: region[regional_node_level],}}]   
        
        gpd_region = gpd.GeoDataFrame.from_features(
                [{'geometry': poly['geometry'],
                    'properties':{
                        GID_level: poly['properties'][GID_level],
                        core_node_level: region[core_node_level],
                        regional_node_level: region[regional_node_level],
                        }}
                    for poly in geojson_region
                ], crs = 'epsg:4326')   
        
        if len(shapes_df) == 0:

            continue

        nodes = gpd.overlay(shapes_df, gpd_region, how = 'intersection')
        stats = zonal_stats(shapes_df['geometry'], path, stats = ['count', 
                                                                  'sum'])
        stats_df = pd.DataFrame(stats)

        nodes = pd.concat([shapes_df, stats_df], axis = 1).drop(columns = 
                                                                'value')
        nodes_subset = nodes[nodes['sum'] >= settlement_size]

        if len(nodes_subset) == 0:

            missing_nodes.add(region[GID_level])

        for idx, item in nodes_subset.iterrows():

            interim.append({
                    'geometry': item['geometry'].centroid,
                    'properties': {
                        GID_level: region[GID_level],
                        core_node_level: region[core_node_level],
                        regional_node_level: region[regional_node_level],
                        'count': item['count'],
                        'sum': item['sum']}})
        
    return interim, missing_nodes


def find_largest_regional_settlement(country):
    """
    Find the largest settlement in each region as the main regional
    routing node.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure')
    path_output = os.path.join(folder, 'largest_regional_settlements.shp')

    folder = os.path.join(DATA_PROCESSED, iso3, 'settlements')
    path_input = os.path.join(folder, 'access_settlements' + '.shp')
    nodes = gpd.read_file(path_input, crs = 'epsg:4326')
    
    nodes = nodes.loc[nodes.reset_index().groupby([GID_level])['population'
                                                               ].idxmax()]
    nodes.to_file(path_output, crs = 'epsg:4326')

    return None


def get_settlement_routing_paths(country):
    """
    Create settlement routing paths and export as linestrings.

    This is based on the largest regional settlement being routed
    to the nearest major settlement, which may or may not be within
    its own region. Any settlements routing to a major settlement from
    a different region will later be combined into a single region
    for modeling purposes.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)
    main_settlement_size = country['main_settlement_size']

    folder = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure')
    path_output = os.path.join(folder, 'settlement_routing.shp')

    folder = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure')
    path_input = os.path.join(folder, 'largest_regional_settlements.shp')
    regional_nodes = gpd.read_file(path_input, crs = 'epsg:4326')

    folder = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure')
    path_input = os.path.join(folder, 'regional_nodes.shp')
    main_nodes = gpd.read_file(path_input, crs = 'epsg:4326')

    paths = []

    for idx, regional_node in regional_nodes.iterrows():
       
        if regional_node['population'] < main_settlement_size:
            
            continue
        
        nearest = nearest_points(regional_node.geometry, main_nodes.unary_union
                                 )[1]
        geom = LineString([
                    (
                        regional_node['geometry'].coords[0][0],
                        regional_node['geometry'].coords[0][1]
                    ),
                    (
                        nearest.coords[0][0],
                        nearest.coords[0][1]
                    ),
                ])
        paths.append({
            'type': 'LineString',
            'geometry': mapping(geom),
            'properties': {
                'id': idx,
                'source': regional_node[GID_level],}})

    paths = gpd.GeoDataFrame.from_features(
        [{
            'geometry': item['geometry'],
            'properties': item['properties'],
            }
            for item in paths
        ],
        crs = 'epsg:4326'
    )
    
    paths['geometry'] = paths['geometry'].to_crs('epsg:3857').buffer(0.01)
    paths['geometry'] = paths['geometry'].to_crs('epsg:4326')
    paths['distance'] = paths['geometry'].length
    geoms = paths.geometry.unary_union
    paths = gpd.GeoDataFrame(geometry = [geoms])
    #paths = gpd.GeoDataFrame({'geometry': [geoms], 'distance': [paths['distance'].sum()]})
    paths = paths.explode().reset_index(drop = True) 
    paths.to_file(path_output, crs = 'epsg:4326') 
    
    return None


def create_regions_to_model(country):
    """
    Any settlements routing to a major settlement from a different
    region are combined into a single region for modeling purposes.

    To combine multiple regions, a union is formed. This is achieved
    by intersecting regions with the settlement routing linestrings.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """
    iso3 = country['iso3']
    GID_level = 'GID_{}'.format(country['lowest'])

    filename = 'regions_{}_{}.shp'.format(country['lowest'], iso3)
    path = os.path.join(DATA_PROCESSED, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs = 'epsg:4326')
    regions = regions.drop_duplicates()
    regions = regions.loc[regions.is_valid]

    filename = 'settlement_routing.shp'
    path = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure', 
                        filename)
    settlement_routing = gpd.read_file(path, crs = 'epsg:4326')
    seen = set()

    output = []
    for idx, regions_to_model in settlement_routing.iterrows():

        regions_to_model = gpd.GeoDataFrame(
            {'geometry': unary_union(regions_to_model['geometry'])},
            crs = 'epsg:4326', index = [0])
        
        regions_to_model = regions[regions.geometry.map(
            lambda x: x.intersects(regions_to_model.geometry.any()))]
        
        if len(regions_to_model) == 0:
            
            print('no matching')
            continue
        
        unique_list = regions_to_model[GID_level].unique()
        unique_names = regions_to_model['NAME_1'].unique()
        unique_regions = str(unique_list).replace('[', '').replace(']', ''
                         ).replace(' ', '-')
        unique_names = str(unique_names).replace('[', '').replace(']', ''
                         ).replace(' ', '-')
        
        regions_to_model = regions_to_model.copy()
        regions_to_model['modeled_regions'] = unique_regions
        regions_to_model['unique_names'] = unique_names
        regions_to_model = regions_to_model.dissolve(by = ['modeled_regions'])
        
        output.append({
            'geometry': regions_to_model['geometry'][0],
            'properties': {
                'regions': unique_regions,
                'names': unique_names,}})
        
        for item in unique_list:

            seen.add(item)

    for idx, region in regions.iterrows():

        if not region[GID_level] in list(seen):

            output.append({
                'geometry': region['geometry'],
                'properties': {
                    'regions': region[GID_level],
                    'names': region['NAME_1'],}})
  
            seen.add(region[GID_level])

    output = gpd.GeoDataFrame.from_features(output)
    filename = 'modeling_regions.shp'
    folder = os.path.join(DATA_PROCESSED, iso3, 'modeling_regions')
    if not os.path.exists(folder):

        os.makedirs(folder)

    output.to_file(os.path.join(folder, filename), crs = 'epsg:4326')


    return None


def create_routing_buffer_zone(country):
    """
    A routing buffer is required to reduce the size of the problem.

    To create the routing zone, a minimum spanning tree is fitted
    between the desired settlements, with a buffer and union consequently
    being added.

    Parameters
    ----------
    country : dict
        Contains all country-specific information for modeling.

    """
    iso3 = country['iso3']
    regional_level = country['lowest']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones')
    folder_nodes = os.path.join(folder, 'nodes')
    folder_edges = os.path.join(folder, 'edges')

    if not os.path.exists(folder_nodes):

        os.makedirs(folder_nodes)

    if not os.path.exists(folder_edges):

        os.makedirs(folder_edges)

    filename = 'access_settlements.shp'
    path = os.path.join(DATA_PROCESSED, iso3, 'settlements', filename)
    settlements = gpd.read_file(path, crs = 'epsg:4326')

    filename = 'modeling_regions.shp'
    path = os.path.join(DATA_PROCESSED, iso3, 'modeling_regions', filename)
    modeling_regions = gpd.read_file(path, crs = 'epsg:4326')

    for idx, region in modeling_regions.iterrows():

        modeling_region = gpd.GeoDataFrame.from_features([{
            'geometry': mapping(region['geometry']),
            'properties': {
                'regions': region['regions']
            }
        }], crs = 'epsg:4326')

        nodes = gpd.overlay(settlements, modeling_region, how = 'intersection')
        main_node = (nodes[nodes['population'] == nodes['population'].max()])

        if not len(main_node) > 0:

            continue

        #export nodes
        path_nodes = os.path.join(folder_nodes, main_node.iloc[0][GID_level] + 
                                  '.shp')
        nodes.to_file(path_nodes, crs = 'epsg:4326')

        #export edges
        path_edges = os.path.join(folder_edges, main_node.iloc[0][GID_level] + 
                                  '.shp')
        fit_edges(path_nodes, path_edges, modeling_region)
        folder_regions = os.path.join(DATA_PROCESSED, iso3, 'modeling_regions')
        path = os.path.join(folder_regions, main_node.iloc[0][GID_level] + '.shp')
        modeling_region.to_file(path, crs = 'epsg:4326')


    return None


def fit_edges(input_path, output_path, modeling_region):
    """
    Fit edges to nodes using a minimum spanning tree.

    Parameters
    ----------
    input_path : string
        Path to the node shapefiles.
    output_path : string
        Path for writing the network edge shapefiles.
    modeling_region : geojson
        The modeling region being assessed.

    """
    folder = os.path.dirname(output_path)
    if not os.path.exists(folder):

        os.makedirs(folder)

    nodes = gpd.read_file(input_path, crs = 'epsg:4326')
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
                        'from': node1_id,
                        'to':  node2_id,
                        'length': line.length,
                        'regions': modeling_region['regions'].iloc()[0],}})
                
    if len(all_possible_edges) == 0:

        return
    G = nx.Graph()

    for node_id, node in enumerate(nodes):

        G.add_node(node_id, object = node)

    for edge in all_possible_edges:

        G.add_edge(edge['properties']['from'], edge['properties']['to'],
            object = edge, weight = edge['properties']['length'])
        
    tree = nx.minimum_spanning_edges(G)
    edges = []

    for branch in tree:

        link = branch[2]['object']
        if link['properties']['length'] > 0:

            edges.append(link)

    edges = gpd.GeoDataFrame.from_features(edges, crs = 'epsg:3857')

    if len(edges) > 0:

        edges = edges.to_crs('epsg:4326')
        edges.to_file(output_path)

    return


def create_region_nodes(iso3):
    """
    This function creates individual region nodes to route fiber.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Creating individual regional nodes for {}'.format(iso3))
    file_in = os.path.join(DATA_PROCESSED, iso3, 'network_routing_structure', 
                               'regional_nodes.shp')
    gdf = gpd.read_file(file_in) 
    grouped_gdf = gdf.groupby('GID_1')

    for gid, group_df in grouped_gdf:

        geometries = []
        populations = []
        types = []

        for index, row in group_df.iterrows():
            
            point = Point(row['lon'], row['lat'])
            geometries.append(point)

            populations.append(row['population'])
            types.append(row['type'])

        group_gdf = gpd.GeoDataFrame(geometry = geometries, crs = gdf.crs)

        group_gdf['population'] = populations
        group_gdf['type'] = types
        group_gdf[['iso3', 'GID_1']] = ''
        for i in range(len(group_gdf)):

            group_gdf['GID_1'].loc[i] = gid
            group_gdf['iso3'].loc[i] = iso3

        group_gdf = group_gdf[['iso3', 'GID_1', 'population', 'type', 'geometry'
                               ]]
        filename = f'{gid}.shp'    
        folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                'regions', 'nodes')
        
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, filename)
        group_gdf.to_file(path_out, index = False)


    return None


def fit_regional_node_edges(iso3):
    """
    This function fits edges between geospatial points using minimum spanning 
    tree

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Fitting {} regional edges'.format(iso3))
    input_path = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                  'regions', 'nodes')
    files = os.listdir(input_path)
    for file in files:
        
        if file.endswith('.shp'): 

            file_path = os.path.join(input_path, file)
            nodes = gpd.read_file(file_path, crs = 'epsg:4326')
            if len(nodes) == 1 and nodes.geometry.geom_type[0] == 'Point':

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

                folder_out = os.path.join(DATA_PROCESSED, iso3, 
                            'buffer_routing_zones', 'regions', 'edges')
                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                edges.to_file(path_out, driver = 'ESRI Shapefile')


    return None


def combine_access_nodes(iso3):
    """
    This function combines the shapefiles into a single shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Combining access node shapefiles for {}'.format(iso3))
    shapefile_dir = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                 'nodes')
    shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(
        shapefile_dir) if f.endswith('.shp')]
    gdf_combined = gpd.GeoDataFrame(pd.concat([gpd.read_file(shp) for shp in 
                                            shapefiles], ignore_index = True))

    folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                               'combined')
    fileout = '{}_combined_access_nodes.shp'.format(iso3)
    if not os.path.exists(folder_out):
        
        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    gdf_combined.to_file(path_out, index = False)


    return None 


def combine_access_edges(iso3):
    """
    This function combines the shapefiles into a single shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Combining access edges shapefiles for {}'.format(iso3))
    merged_shapefile = gpd.GeoDataFrame()
    shapefile_dir = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                 'edges')
    for file_name in os.listdir(shapefile_dir):

        if file_name.endswith('.shp'):

            file_path = os.path.join(shapefile_dir, file_name)
            shapefile = gpd.read_file(file_path)
            shapefile[['GID_2', 'strategy']] = ''
            base_name, extension = os.path.splitext(file_name)

            for i in range(len(shapefile)):

                shapefile['GID_2'].loc[i] = base_name  
                shapefile['strategy'].loc[i] = 'access'

            merged_shapefile = pd.concat([merged_shapefile, shapefile], 
                                         ignore_index = True) 
          
    folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                               'combined')
    fileout = '{}_combined_access_edges.shp'.format(iso3)
    if not os.path.exists(folder_out):
        
        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    merged_shapefile.to_file(path_out, index = False)

    return None


def generate_access_csv(iso3):
    """
    This function generates a csv file for access level.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating fiber access csv file for {}'.format(iso3))
    folder_in = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                               'combined')
    node_path = os.path.join(folder_in, '{}_combined_access_nodes.shp'.format(
        iso3))
    edge_path = os.path.join(folder_in, '{}_combined_access_edges.shp'.format(
        iso3))
    
    gdf = gpd.read_file(node_path)
    gdf = gdf.drop(columns = ['regions', 'id', 'GID_0', 'geometry'])

    gdf1 = gpd.read_file(edge_path)
    
    if iso3 == 'GMB':

        pass

    else:
        gdf1 = gdf1.drop(columns = ['regions', 'geometry', 'to', 'from']
                        ).reset_index()
        gdf1 = gdf1.groupby(['GID_2', 'strategy'])['length'].sum().reset_index()

        try:

            merged_df = pd.merge(gdf, gdf1, on = 'GID_2', how = 'inner')

        except:

            gdf.rename(columns = {'GID_1': 'GID_2'}, inplace = True)
            merged_df = pd.merge(gdf, gdf1, on = 'GID_2', how = 'inner')

        merged_df['length_km'] = ''
        for i in range(len(merged_df)):

            merged_df['length_km'].loc[i] = merged_df['length'].loc[i] / 1000
        
        merged_df['algorithm'] = 'Dijkstras'
        merged_df = merged_df.drop(columns = ['length']).reset_index()

        fileout = '{}_fiber_access.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_df.to_csv(path_out, index = False)


    return None


def combine_regional_nodes(iso3):
    """
    This function combines the regional node shapefiles into a single shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Combining regional node shapefiles for {}'.format(iso3))
    shapefile_dir = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                'regions', 'nodes')
    shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(
        shapefile_dir) if f.endswith('.shp')]
    gdf_combined = gpd.GeoDataFrame(pd.concat([gpd.read_file(shp) for shp in 
                                            shapefiles], ignore_index = True))
    
    folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                            'combined')
    fileout = '{}_combined_regional_nodes.shp'.format(iso3)
    if not os.path.exists(folder_out):
        
        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    gdf_combined.to_file(path_out, index = False)


    return None 


def combine_regional_edges(iso3):
    """
    This function combines the regional shapefile nodes into a single shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Combining regional edges shapefiles for {}'.format(iso3))
    merged_shapefile = gpd.GeoDataFrame()
    shapefile_dir = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                 'regions', 'edges')
    try:
        for file_name in os.listdir(shapefile_dir):

            if file_name.endswith('.shp'):

                file_path = os.path.join(shapefile_dir, file_name)
                shapefile = gpd.read_file(file_path)
                shapefile[['GID_2', 'strategy']] = ''
                base_name, extension = os.path.splitext(file_name)

                for i in range(len(shapefile)):

                    shapefile['GID_2'].loc[i] = base_name  
                    shapefile['strategy'].loc[i] = 'regional'

                merged_shapefile = pd.concat([merged_shapefile, shapefile], 
                                            ignore_index = True) 
            
        folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                'combined')
        fileout = '{}_combined_regional_edges.shp'.format(iso3)
        if not os.path.exists(folder_out):
            
            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_shapefile.to_file(path_out, index = False)
    except:

        print('Regional edges already fitted')

    return None

def generate_regional_csv(iso3):
    """
    This function generates a csv file for regional level.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating regional fiber csv file for {}'.format(iso3))
    folder_in = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                               'combined')
    node_path = os.path.join(folder_in, '{}_combined_regional_nodes.shp'.format(
        iso3))
    edge_path = os.path.join(folder_in, '{}_combined_regional_edges.shp'.format(
        iso3))
    
    gdf = gpd.read_file(node_path)
    gdf = gdf.drop(columns = ['geometry'])

    try:

        gdf1 = gpd.read_file(edge_path)
        gdf1 = gdf1.drop(columns = ['geometry', 'to', 'from']
                        ).reset_index()
        gdf1 = gdf1.groupby(['GID_1', 'strategy'])['length'].sum().reset_index()

        try:

            merged_df = pd.merge(gdf, gdf1, on = 'GID_1', how = 'inner')

        except:

            gdf.rename(columns = {'GID_1': 'GID_1'}, inplace = True)
            merged_df = pd.merge(gdf, gdf1, on = 'GID_1', how = 'inner')

        merged_df['length_km'] = ''
        for i in range(len(merged_df)):

            merged_df['length_km'].loc[i] = merged_df['length'].loc[i] / 1000
        
        merged_df['algorithm'] = 'Dijkstras'
        merged_df = merged_df.drop(columns = ['length']).reset_index()

        fileout = '{}_fiber_regional.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_df.to_csv(path_out, index = False)
    except:

        print('No regional fiber data available')

    return None



def generate_existing_fiber_csv(iso3):
    """
    This function generates a csv file for existing fiber.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating regional fiber csv file for {}'.format(iso3))
    folder_in = os.path.join(DATA_PROCESSED, iso3, 'network_existing')
    node_path = os.path.join(folder_in, '{}_core_nodes_existing.shp'.format(
        iso3))
    edge_path = os.path.join(folder_in, '{}_core_edges_existing.shp'.format(
        iso3))
    
    if os.path.exists(edge_path):

        gdf = gpd.read_file(node_path)
        gdf = gdf.drop(columns = ['geometry'])

        gdf1 = gpd.read_file(edge_path)
        gdf1[['iso3', 'length_km', 'nodes', 'strategy']] = ''
        #111.32km is equaivalent to 1 decimal degree. The distance calculated 
        #from EPSG:4326 coordinate system is always in decimal degrees
        for i in range(len(gdf1)):

            gdf1['iso3'].loc[i] = iso3
            gdf1['nodes'].loc[i] = len(gdf1)
            gdf1['length_km'].loc[i] = (gdf1['geometry'].loc[i]).length * 111.32
            gdf1['strategy'].loc[i] = 'existing'

        gdf1 = gdf1.drop(columns = ['geometry', 'operators', 'source']
                        ).reset_index()
        gdf1 = gdf1.groupby(['iso3', 'strategy', 'nodes'])['length_km'].sum().reset_index()
        
        gdf.rename(columns = {'GID_0': 'iso3'}, inplace = True)
        merged_df = pd.merge(gdf, gdf1, on = 'iso3', how = 'inner').reset_index()

        merged_df = merged_df[['iso3', 'length_km', 'nodes', 'strategy', 
                               'population']]
        merged_df = merged_df.groupby(['iso3', 'length_km', 'nodes', 'strategy']
                                      )['population'].sum().reset_index()
        
        merged_df['algorithm'] = 'none'
        fileout = '{}_fiber_existing.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_df.to_csv(path_out, index = False)

    else:

        print('No existing fiber data found for {}'.format(iso3))

    return None


def combine_pcsf_access_edges(iso3):
    """
    This function combines the shapefiles obtained from running
    PCSF algorthm into a single shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    try: 
        print('Combining PCSF access edges shapefiles for {}'.format(iso3))
        merged_shapefile = gpd.GeoDataFrame()
        shapefile_dir = os.path.join(DATA_RESULTS, iso3, 'pcsf_solutions', 
                                    'regions_soln')
        for file_name in os.listdir(shapefile_dir):

            if file_name.endswith('.shp'):

                file_path = os.path.join(shapefile_dir, file_name)
                shapefile = gpd.read_file(file_path)
                shapefile[['GID_2', 'strategy', 'algorithm']] = ''
                base_name = '_'.join(file_name.split('_')[:-1])

                for i in range(len(shapefile)):

                    shapefile['GID_2'].loc[i] = base_name  
                    shapefile['strategy'].loc[i] = 'access'
                    shapefile['algorithm'].loc[i] = 'pcsf'

                merged_shapefile = pd.concat([merged_shapefile, shapefile], 
                                            ignore_index = True) 
            
        folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                                'combined')
        fileout = '{}_combined_pcsf_access_edges.shp'.format(iso3)
        if not os.path.exists(folder_out):
            
            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_shapefile.to_file(path_out, index = False)

    except:

        pass

    return None


def combine_pcsf_regional_nodes(iso3):
    """
    This function combines the regional node shapefiles obtained from running
    PCSF algorthm into a single shapefile.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Combining PCSF regional node shapefiles for {}'.format(iso3))
    shapefile_dir = os.path.join(DATA_PROCESSED, iso3, 'pcsf_region_nodes')

    shapefiles = [os.path.join(shapefile_dir, files) for files in os.listdir(
        shapefile_dir) if files.endswith('updated.shp')]
    gdf_combined = gpd.GeoDataFrame(pd.concat([gpd.read_file(shp) for shp in 
                                            shapefiles], ignore_index = True))
    
    folder_out = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                            'combined')
    fileout = '{}_combined_pcsf_regional_nodes.shp'.format(iso3)
    if not os.path.exists(folder_out):
        
        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    gdf_combined.to_file(path_out, index = False)


    return None 


def generate_pcsf_regional_csv(iso3):
    """
    This function generates a csv file for connected population at regional 
    level using PCSF.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating PCSF regional fiber csv file for {}'.format(iso3))
    folder_in = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                               'combined')
    node_path = os.path.join(folder_in, '{}_combined_pcsf_regional_nodes.shp'.format(
        iso3))
    edge_path = os.path.join(folder_in, '{}_combined_pcsf_access_edges.shp'.format(
        iso3))
    
    gdf = gpd.read_file(node_path)
    gdf = gdf.drop(columns = ['geometry'])

    try:

        gdf1 = gpd.read_file(edge_path)
        gdf1 = gdf1.drop(columns = ['id', 'start', 'strategy', 'end', 'type']
                        ).reset_index()
        gdf1.rename(columns = {'GID_2': 'GID_1'}, 
                                inplace = True)
        gdf1['length'] = gdf1.geometry.length
        gdf1['strategy'] = 'regional'
        gdf1 = gdf1.groupby(['GID_1', 'strategy', 'algorithm']
                            )['length'].sum().reset_index()

        try:

            merged_df = pd.merge(gdf, gdf1, on = 'GID_1', how = 'inner')

        except:

            gdf.rename(columns = {'GID_1': 'GID_1'}, inplace = True)
            merged_df = pd.merge(gdf, gdf1, on = 'GID_1', how = 'inner')

        merged_df['length_km'] = ''
        for i in range(len(merged_df)):

            merged_df['length_km'].loc[i] = merged_df['length'].loc[i] * 110.567
        
        merged_df = merged_df.drop(columns = ['length']).reset_index()

        fileout = '{}_fiber_pcsf_regional.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_df.to_csv(path_out, index = False)

    except:

        print('No regional fiber data available')

    return None


def generate_pcsf_access_csv(iso3):
    """
    This function generates a csv file for connected population at access 
    level using PCSF.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    """
    print('Generating PCSF access fiber csv file for {}'.format(iso3))
    folder_in = os.path.join(DATA_PROCESSED, iso3, 'buffer_routing_zones', 
                               'combined')
    node_path = os.path.join(folder_in, '{}_combined_pcsf_subregional_nodes.shp'.format(
        iso3))
    edge_path = os.path.join(folder_in, '{}_combined_pcsf_access_edges.shp'.format(
        iso3))
    
    gdf = gpd.read_file(node_path)
    gdf = gdf.drop(columns = ['geometry'])

    try:

        gdf1 = gpd.read_file(edge_path)
        gdf1 = gdf1.drop(columns = ['id', 'start', 'strategy', 'end', 'type']
                        ).reset_index()
        gdf1.rename(columns = {'GID_2': 'GID_1'}, 
                                inplace = True)

        gdf1['length'] = gdf1.geometry.length
        gdf1['strategy'] = 'access'
        gdf1 = gdf1.groupby(['GID_1','strategy', 'algorithm']
                            )['length'].sum().reset_index()
        

        try:

            merged_df = pd.merge(gdf, gdf1, on = 'GID_2', how = 'inner')

        except:

            gdf.rename(columns = {'GID_1': 'GID_1'}, inplace = True)
            merged_df = pd.merge(gdf, gdf1, on = 'GID_1', how = 'inner')

        merged_df['length_km'] = ''
        for i in range(len(merged_df)):

            merged_df['length_km'].loc[i] = merged_df['length'].loc[i] * 110.567
        
        merged_df = merged_df.drop(columns = ['length']).reset_index()
        merged_df = merged_df[['iso3', 'GID_1', 'GID_2', 'population', 
                              'length_km', 'strategy', 'algorithm']]

        fileout = '{}_fiber_pcsf_access.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'fiber_design')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out = os.path.join(folder_out, fileout)
        merged_df.to_csv(path_out, index = False)

    except:

        print('No access fiber data available')

    return None


'''for idx, country in countries.iterrows():
        
    #if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
        
    if not country['iso3'] == 'BWA':

        continue

    generate_pcsf_access_csv(countries['iso3'].loc[idx])'''