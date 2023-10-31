import os
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
from pylab import * #is this needed

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_PROCESS = os.path.join(BASE_PATH, '..', 'results', 'processed')
USER_COSTS = os.path.join(BASE_PATH, '..', 'results', 'user_costs')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')


def get_regional_shapes():
    """
    Load regional shapes.

    """
    output = []

    for item in os.listdir(DATA_PROCESS):

        filename_gid2 = 'regions_2_{}.shp'.format(item)
        path_gid2 = os.path.join(DATA_PROCESS, item, 'regions', filename_gid2)

        filename_gid1 = 'regions_1_{}.shp'.format(item)
        path_gid1 = os.path.join(DATA_PROCESS, item, 'regions', filename_gid1)

        if os.path.exists(path_gid2):
            data = gpd.read_file(path_gid2)
            data['GID_id'] = data['GID_2']
            data = data.to_dict('records')

        elif os.path.exists(path_gid1):
            data = gpd.read_file(path_gid1)
            data['GID_id'] = data['GID_1']
            data = data.to_dict('records')

        else:

            print('No shapefiles for {}'.format(item))
            continue

        for datum in data:
            output.append({
                'geometry': datum['geometry'],
                'properties': {
                    'GID_1': datum['GID_id'],
                },
            })

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
    

    return output


def plot_regions_by_geotype():
    """
    Plot regions by geotype.

    """
    regions = get_regional_shapes()
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 
                 'SSA', 'SSA_demand_results.csv')
    
    data = pd.read_csv(DATA_AFRICA)
    n = len(regions)
    data['pop_density'] = round(data['pop_density'])
    data = data[['GID_1', 'pop_density']]
    regions = regions[['GID_1', 'geometry']]#[:1000]
    regions = regions.copy()

    regions = regions.merge(data, left_on = 'GID_1', right_on = 'GID_1')
    regions.reset_index(drop = True, inplace = True)

    metric = 'pop_density'
    bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 1116]
    labels = [
        '<20 $\mathregular{km^2}$',
        '20-43 $\mathregular{km^2}$',
        '43-69 $\mathregular{km^2}$',
        '69-109 $\mathregular{km^2}$',
        '109-171 $\mathregular{km^2}$',
        '171-257 $\mathregular{km^2}$',
        '257-367 $\mathregular{km^2}$',
        '367-541 $\mathregular{km^2}$',
        '541-1104 $\mathregular{km^2}$',
        '>1104 $\mathregular{km^2}$']

    regions['bin'] = pd.cut(
        regions[metric],
        bins = bins,
        labels = labels)

    sns.set(font_scale = 0.9)
    fig, ax = plt.subplots(1, 1, figsize = (10, 10))

    base = regions.plot(column = 'bin', ax = ax, 
        cmap = 'YlGnBu', linewidth = 0.2,
        legend=True, edgecolor = 'grey')

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

    name = 'Population Density Deciles for Sub-National Regions (n={})'.format(n)
    ax.set_title(name, fontsize = 14)

    fig.tight_layout()
    path = os.path.join(VIS, 'region_by_pop_density.png')
    fig.savefig(path)

    plt.close(fig)


def plot_revenue_per_area():
    """
    Plot regions by geotype.

    """
    regions = get_regional_shapes()
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 
                 'SSA', 'SSA_demand_results.csv')
    
    data = pd.read_csv(DATA_AFRICA)
    n = len(regions)
    data['revenue_per_area'] = round(data['revenue_per_area'])
    data = data[['GID_1', 'revenue_per_area']]
    regions = regions[['GID_1', 'geometry']]#[:1000]
    regions = regions.copy()

    regions = regions.merge(data, left_on = 'GID_1', right_on = 'GID_1')
    regions.reset_index(drop = True, inplace = True)

    metric = 'revenue_per_area'
    bins = [-1, 15, 25, 50, 75, 120, 180, 275, 375, 750, 1500, 2000, 3000, 10000]
    labels = ['<15 $US', '15-25 $US', '25-50 $US', '50-75 $US', '75-120 $US',
              '120-180 $US', '180-275 $US', '275-375 $US', '375-750 $US',
              '750-1500 $US', '1500-2000 $US', '2000-3000 $US', '>3000 $US']

    regions['bin'] = pd.cut(
        regions[metric],
        bins = bins,
        labels = labels)

    sns.set(font_scale = 0.9)
    fig, ax = plt.subplots(1, 1, figsize = (10, 10))

    base = regions.plot(column = 'bin', ax = ax, 
        cmap = 'YlGnBu', linewidth = 0.2,
        legend=True, edgecolor = 'grey')

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

    name = 'Revenue per Area for Sub-National Regions (n={})'.format(n)
    ax.set_title(name, fontsize = 14)

    fig.tight_layout()
    path = os.path.join(VIS, 'region_by_revenue_per_area.png')
    fig.savefig(path)

    plt.close(fig)


def plot_tco_per_user():
    """
    Plot tco per user by subregions.

    """
    regions = get_regional_shapes()
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 
                 'SSA', 'SSA_supply_results.csv')
    
    data = pd.read_csv(DATA_AFRICA)
    n = len(regions)
    data['tco_per_user'] = round(data['tco_per_user'])
    data = data[['GID_1', 'tco_per_user']]
    regions = regions[['GID_1', 'geometry']]#[:1000]
    regions = regions.copy()

    regions = regions.merge(data, left_on = 'GID_1', right_on = 'GID_1')
    regions.reset_index(drop = True, inplace = True)

    metric = 'tco_per_user'
    bins = [-1, 1000, 3400, 70000, 150000, 200000, 300000, 400000, 500000, 550000, 650000, 750000, 800000, 430000000]
    labels = ['<15 $US', '15-25 $US', '25-50 $US', '50-75 $US', '75-120 $US',
              '120-180 $US', '180-275 $US', '275-375 $US', '375-750 $US',
              '750-1500 $US', '1500-2000 $US', '2000-3000 $US', '>3000 $US']

    regions['bin'] = pd.cut(
        regions[metric],
        bins = bins,
        labels = labels)

    sns.set(font_scale = 0.9)
    fig, ax = plt.subplots(1, 1, figsize = (10, 10))

    base = regions.plot(column = 'bin', ax = ax, 
        cmap = 'YlGnBu', linewidth = 0.2,
        legend=True, edgecolor = 'grey')

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

    name = 'TCO per User for Sub-National Regions (n={})'.format(n)
    ax.set_title(name, fontsize = 14)

    fig.tight_layout()
    path = os.path.join(VIS, 'region_by_tco_per_user.png')
    fig.savefig(path)

    plt.close(fig)

#plot_revenue_per_area()
plot_tco_per_user()
#plot_regions_by_geotype()