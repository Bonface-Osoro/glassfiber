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


if __name__ == '__main__':

    #csv_merger('_users_results.csv', 'demand')
    csv_merger('_supply_results.csv', 'supply')