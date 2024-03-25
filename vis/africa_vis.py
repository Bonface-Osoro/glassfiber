import os
import configparser
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
from pylab import *
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_PROCESS = os.path.join(BASE_PATH, '..', 'results', 'processed')
USER_COSTS = os.path.join(BASE_PATH, '..', 'results', 'user_costs')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')
DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 'SSA')

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
    Plot population density 
    by regions.

    """
    print('Plotting population density by regions')
    regions = get_regional_shapes()
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 
                 'SSA', 'SSA_demand_results.csv')
    
    data = pd.read_csv(DATA_AFRICA)
    n = int((len(data)) / 4)
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
        legend=True, edgecolor = None)

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
    Plot revenue per area 
    by regions.

    """
    print('Plotting revenue per area by regions')
    regions = get_regional_shapes()
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 
                 'SSA', 'SSA_demand_results.csv')
    
    data = pd.read_csv(DATA_AFRICA)
    n = int((len(data)) / 4)
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
        legend=True, edgecolor = None)

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
    print('Plotting TCO per user by regions')
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
    bins = ([-1, 1000, 3400, 70000, 150000, 200000, 300000, 400000, 
             500000, 550000, 650000, 750000, 800000, 430000000])
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
        legend=True, edgecolor = None)

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

    name = 'TCO per User for Sub-National Regions (n={})'.format(n)
    ax.set_title(name, fontsize = 14)

    fig.tight_layout()
    path = os.path.join(VIS, 'region_by_tco_per_user.png')
    fig.savefig(path)

    plt.close(fig)


def plot_demand_area(monthly_traffic):
    """
    Plot demand per area by regions.

    """
    print('Plotting demand per area for {} GB monthly traffic by regions'.format(monthly_traffic))
    regions = get_regional_shapes()
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 
                 'SSA', 'SSA_demand_user.csv')
    
    data = pd.read_csv(DATA_AFRICA)
    data = data[data['monthly_traffic'] == monthly_traffic]
    data['demand_mbps_sqkm'] = round(data['demand_mbps_sqkm'])
    data = data[['GID_1', 'demand_mbps_sqkm']]
    regions = regions[['GID_1', 'geometry']]#[:1000]
    regions = regions.copy()

    regions = regions.merge(data, left_on = 'GID_1', right_on = 'GID_1')
    regions.reset_index(drop = True, inplace = True)

    metric = 'demand_mbps_sqkm'
    bins = [-1, 0.001, 0.01, 0.05, 0.5, 1, 5, 10, 20, 30, 100, 200]
    labels = ['<0.001 $\mathregular{Mbps/km^2}$', 
              '0.001 - 0.01 $\mathregular{Mbps/km^2}$', 
              '0.01 - 0.05 $\mathregular{Mbps/km^2}$', 
              '0.05 - 0.5 $\mathregular{Mbps/km^2}$', 
              '0.5 - 1 $\mathregular{Mbps/km^2}$',
              '1 - 5 $\mathregular{Mbps/km^2}$', 
              '5 - 10 $\mathregular{Mbps/km^2}$', 
              '10 - 20 $\mathregular{Mbps/km^2}$', 
              '20 - 30 $\mathregular{Mbps/km^2}$',
              '30 - 100 $\mathregular{Mbps/km^2}$',
              '>200 $\mathregular{Mbps/km^2}$']

    regions['bin'] = pd.cut(
        regions[metric],
        bins = bins,
        labels = labels)

    sns.set(font_scale = 0.9)
    fig, ax = plt.subplots(1, 1, figsize = (10, 10))

    base = regions.plot(column = 'bin', ax = ax, 
        cmap = 'YlGnBu', linewidth = 0.2,
        legend=True, edgecolor = None)

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

    name = "Demand per Area for Sub-National Regions ({} GB/Month)".format(monthly_traffic)
    ax.set_title(name, fontsize = 14)

    fig.tight_layout()
    path = os.path.join(VIS, 'demand_{}_per_area.png'.format(monthly_traffic))
    fig.savefig(path)

    plt.close(fig)

def plot_regions_by_emissions():
    """
    Plot emissions per user 
    by regions.
    """
    print('Plotting emissions per user by regions')
    
    regions = get_regional_shapes()
    
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 'SSA', 'SSA_emission_results.csv')
    data = pd.read_csv(DATA_AFRICA)
    n = int(len(data) / 4)
    data['emissions_kg_per_subscriber'] = round(data['emissions_kg_per_subscriber']/1e6)
    data = data[['GID_1', 'emissions_kg_per_subscriber', 'adoption_scenario']]
    
    value_mapping = {'low': 'Low', 'baseline': 'Baseline', 'high': 'High'}
    data['adoption_scenario'] = data['adoption_scenario'].replace(value_mapping)
    
    regions = regions[['GID_1', 'geometry']]
    regions = regions.merge(data, left_on = 'GID_1', right_on = 'GID_1')
    regions.reset_index(drop = True, inplace = True)

    metric = 'emissions_kg_per_subscriber'
    bins = [-1, 1000, 5000, 10000, 25000, 50000, 100000, 150000, 200000, 500000, 1000000]
    labels = [
        '<1k$',
        '5 - 10k',
        '10 - 25k',
        '25 - 50k',
        '50 - 100k',
        '100 - 250k',
        '250 - 500k',
        '500k - 1 mn',
        '1 - 3 mn',
        '>3 mn']

    regions['bin'] = pd.cut(
        regions[metric],
        bins = bins,
        labels = labels)
    
    sns.set(font_scale = 0.9)
    
    # Create subplots for each category in the "poverty_range" column
    fig, axes = plt.subplots(1, 3, figsize = (12, 10), sharex = True, sharey = True)

    for i, adoption in enumerate(data['adoption_scenario'].unique()):

        subset_regions = regions[regions['adoption_scenario'] == adoption]
        if i < len(axes):

            ax = axes[i]

            base = subset_regions.plot(column = 'bin', ax = ax,
                                    cmap = 'YlGnBu', linewidth = 0.2,
                                    legend = True, edgecolor = None)

            handles, labels = ax.get_legend_handles_labels()

            ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

            name = f'{adoption} (n={n})'
            ax.set_title(name, fontsize = 14)

        else:

            print(f"Warning: Not enough axes for adoption {adoption}")

    fig.subplots_adjust(wspace = 0)
    fig.tight_layout(rect = [0, 0, 1, 1])

    path = os.path.join(VIS, 'emission_per_user_map.png')
    fig.savefig(path)
    plt.close(fig)


def plot_emission_subscriber():
    """
    Plot emissions per user 
    by regions.
    """
    print('Plotting emissions per user by regions')
    
    regions = get_regional_shapes()
    
    DATA_AFRICA = os.path.join(BASE_PATH, '..', 'results', 'SSA', 'SSA_emission_results.csv')
    data = pd.read_csv(DATA_AFRICA)
    n = int(len(data) / 4)
    data['emissions_kg_per_subscriber'] = round(data['emissions_kg_per_subscriber']/1e3)
    data = data[['GID_1', 'emissions_kg_per_subscriber', 'adoption_scenario']]
    
    value_mapping = {'low': 'Low', 'baseline': 'Baseline', 'high': 'High'}
    data['adoption_scenario'] = data['adoption_scenario'].replace(value_mapping)
    
    regions = regions[['GID_1', 'geometry']]
    regions = regions.merge(data, left_on = 'GID_1', right_on = 'GID_1')
    regions.reset_index(drop = True, inplace = True)

    metric = 'emissions_kg_per_subscriber'
    bins = [-1, 1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 60000000]
    labels = [
        '<0.5k$',
        '0.5 - 1k',
        '1 - 2.5k',
        '2.5 - 5k',
        '5 - 10k',
        '10 - 25k',
        '25 - 50k',
        '50k - 100k',
        '100 - 300k',
        '>300k']

    regions['bin'] = pd.cut(
        regions[metric],
        bins = bins,
        labels = labels)
    
    sns.set(font_scale = 0.9)
    fig, ax = plt.subplots(1, 1, figsize = (10, 10))

    base = regions.plot(column = 'bin', ax = ax, 
        cmap = 'YlGnBu', linewidth = 0.2,
        legend=True, edgecolor = None)

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs = regions.crs, source = ctx.providers.CartoDB.Voyager)

    name = "Emission per User (kt $\mathregular{ CO_2}$ eq.) by Sub-National Regions"
    ax.set_title(name, fontsize = 14)

    fig.tight_layout()
    path = os.path.join(VIS, 'per_user_emissions_map.png')
    fig.savefig(path)

    plt.close(fig)


'''if __name__ == '__main__':

    plot_regions_by_geotype()
    plot_revenue_per_area()
    plot_tco_per_user()
    #plot_emission_subscriber()
    plot_regions_by_emissions()
    traffics = [10, 20, 30, 40]
    for traffic in traffics:

        plot_demand_area(traffic)'''