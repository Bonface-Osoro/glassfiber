import os
import configparser
import warnings
import pandas as pd
import geopandas as gpd
import tqdm
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')

path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'latin-1')

southern = ['AGO', 'ZMB', 'ZWE', 'NAM', 'BWA', 'ZAF', 'LSO', 
            'SWZ', 'MOZ', 'MWI']

central = ['CMR', 'CAF', 'TCD', 'COD', 'GNQ', 'GAB', 'STP']

eastern = ['BDI', 'COM', 'DJI', 'ERI', 'ETH', 'SWZ', 'MDG', 
           'KEN', 'MUS', 'SDN', 'SYC', 'SOM', 'SSD', 'UGA', 
           'TZA']

west = ['BEN', 'BFA', 'CPV', 'CIV', 'GMB', 'GHA', 'GIN', 
        'GNB', 'LBR', 'MLI', 'MRT', 'NER', 'NGA', 'SEN', 
        'SLE', 'TGO']

def csv_merger(csv_name, source_folder):
    """
    This funcion read and merge 
    multiple CSV files located 
    in different folders.

    Parameters
    ----------
    csv_name : string
        Name of the file to process. it can be
        '_customers.csv', '_ev_centers.csv' or
        '_optimized_ev_centers.csv'
    source_folder : string
        Name of the folder containing the files.
        It can be  
    """

    isos = os.listdir(DATA_RESULTS)

    merged_data = pd.DataFrame()
    for iso3 in isos:

        print('Merging {} csv files'. format(iso3))
        base_directory = os.path.join(DATA_RESULTS, iso3, source_folder) 

        for root, _, files in os.walk(base_directory):

            for file in files:

                if file.endswith('{}'.format(csv_name)):
                    
                    file_path = os.path.join(base_directory, '{}{}'.format(iso3, csv_name))
                    df = pd.read_csv(file_path)
                    df['region'] = ''

                    for i in range(len(df)):

                        if iso3 in southern:

                            df['region'].loc[i] = 'Southern'

                        elif iso3 in central:

                            df['region'].loc[i] = 'Central'

                        elif iso3 in eastern:

                            df['region'].loc[i] = 'Eastern'

                        else: 

                            df['region'].loc[i] = 'West'

                    merged_data = pd.concat([merged_data, df], ignore_index = True)
                        
                    fileout = 'SSA{}'.format(csv_name)
                    folder_out = os.path.join(DATA_RESULTS, '..', 'SSA')

                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    merged_data.to_csv(path_out, index = False)

    return None


def sum_costs(iso3, metric):
    """
    This function calculates 
    total and average 
    revenue per area and 
    the total cost of ownership 
    per user for each country.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    metric : string
        Attribute being quantified: i.e 
        `revenue_per_area`, `tco_per_user`.
    """

    DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
    path_in = os.path.join(DATA_RESULTS, iso3, 'supply', 
        '{}_supply_results.csv'.format(iso3))
    
    df = pd.read_csv(path_in)
    
    print('Summing {} data for {}'.format(metric, iso3))

    rev_per_area = df.groupby(['iso3', 'adoption_scenario', 
                   'geotype'])['revenue_per_area'].sum()
    
    average_rev = df.groupby(['iso3', 'adoption_scenario', 
                'geotype'])['revenue_per_area'].mean()

    tco_per_user = df.groupby(['iso3', 'adoption_scenario', 
                   'geotype'])['tco_per_user'].sum()
    
    average_tco = df.groupby(['iso3', 'adoption_scenario', 
                   'geotype'])['tco_per_user'].mean()
    
    average_area = df.groupby(['iso3', 'geotype'])['area'].sum()
    
    fileout_1 = '{}_rev_per_area_total.csv'.format(iso3)
    fileout_2 = '{}_tco_per_user_total.csv'.format(iso3)
    fileout_3 = '{}_rev_per_area_average.csv'.format(iso3)
    fileout_4 = '{}_tco_per_user_average.csv'.format(iso3)
    fileout_5 = '{}_geotype_total_area.csv'.format(iso3)

    folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout_1)
    path_out_2 = os.path.join(folder_out, fileout_2)
    path_out_3 = os.path.join(folder_out, fileout_3)
    path_out_4 = os.path.join(folder_out, fileout_4)
    path_out_5 = os.path.join(folder_out, fileout_5)

    rev_per_area.to_csv(path_out)
    tco_per_user.to_csv(path_out_2)
    average_rev.to_csv(path_out_3)
    average_tco.to_csv(path_out_4)
    average_area.to_csv(path_out_5)
    print('Summary statistics completed for {}'.format(iso3))
    
    return None


if __name__ == '__main__':
    for idx, country in countries.iterrows():
            
        if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
            
        #if not country['iso3'] == 'KEN':
            
            continue 

        #sum_costs(countries['iso3'].loc[idx], 'rev_per_area')
        #sum_costs(countries['iso3'].loc[idx], 'tco_per_user')

#csv_merger('_demand_results.csv', 'demand')
csv_merger('_supply_results.csv', 'supply')
#csv_merger('_rev_per_area_average.csv', 'summary')
#csv_merger('_rev_per_area_total.csv', 'summary')
#csv_merger('_tco_per_user_total.csv', 'summary')
#csv_merger('_tco_per_user_average.csv', 'summary')
csv_merger('_geotype_total_area.csv', 'summary')