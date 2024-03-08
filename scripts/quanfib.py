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
countries = pd.read_csv(path, encoding = 'utf-8-sig')

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

                    if csv_name == '_geotype_population.csv':

                        merged_data = merged_data.groupby(['geotype'])['population'].sum().reset_index()

                    if csv_name == '_geotype_total_area.csv':

                        merged_data = merged_data.groupby(['geotype']
                                    )['area'].sum().reset_index()

                    if csv_name == '_baseline_emission_results.csv':

                        merged_data = merged_data.groupby(['iso3', 'GID_2']
                        )['emissions_kg_per_subscriber'].mean().reset_index()

                    if csv_name == '_baseline_tco_results.csv':

                        merged_data = merged_data.groupby(['iso3', 'GID_2']
                                    )['tco_per_user'].mean().reset_index()       

                    fileout = 'SSA{}'.format(csv_name)
                    folder_out = os.path.join(DATA_RESULTS, '..', 'SSA')

                    if not os.path.exists(folder_out):

                        os.makedirs(folder_out)

                    path_out = os.path.join(folder_out, fileout)
                    merged_data.to_csv(path_out, index = False)

    return None


def summations(iso3, metric):
    """
    This function calculates 
    averages for each country.

    Parameters
    ----------
    iso3 : string
        Country ISO3 code
    metric : string
        Attribute being quantified: i.e 
        `revenue_per_area`, `tco_per_user`.
    """

    DATA_RESULTS = os.path.join(BASE_PATH, '..', 'results', 'final')
    if metric == 'demand_mbps_sqkm':

        path_in = os.path.join(DATA_RESULTS, iso3, 'demand', 
            '{}_demand_user.csv'.format(iso3))
        df = pd.read_csv(path_in)
        average_demand = df.groupby(['iso3', 'adoption_scenario', 
                   'geotype', 'monthly_traffic'])['demand_mbps_sqkm'].mean()
        fileout_6 = '{}_average_demand.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_6 = os.path.join(folder_out, fileout_6)
        average_demand.to_csv(path_out_6)

    elif metric == 'emissions_kg_per_subscriber':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        average_emissions = df.groupby(['iso3', 'adoption_scenario', 
                   'geotype', 'monthly_traffic'])['emissions_kg_per_subscriber'].mean()
        
        country_emissions = df.groupby(['iso3', 'adoption_scenario', 
                    'geotype'])['emissions_kg_per_subscriber'].sum()
        
        fileout_7 = '{}_average_emissions.csv'.format(iso3)
        fileout_8 = '{}_emission_subscriber_total.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')
        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_7 = os.path.join(folder_out, fileout_7)
        path_out_8 = os.path.join(folder_out, fileout_8)

        average_emissions.to_csv(path_out_7)
        country_emissions.to_csv(path_out_8)

    elif metric == 'total_eolt_ghg_kg':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        average_eolt = df.groupby(['iso3', 'adoption_scenario', 
                    'geotype', 'emission_category', 
                    'lca_phase_ghg_kg'])['total_eolt_ghg_kg'].mean()
        total_eolt = df.groupby(['iso3', 'adoption_scenario', 
                    'geotype', 'emission_category', 
                    'lca_phase_ghg_kg'])['total_eolt_ghg_kg'].sum()
        fileout_9 = '{}_average_eolt.csv'.format(iso3)
        fileout_sum_9 = '{}_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_9 = os.path.join(folder_out, fileout_9)
        path_out_sum_9 = os.path.join(folder_out, fileout_sum_9)
        average_eolt.to_csv(path_out_9)
        total_eolt.to_csv(path_out_sum_9)

    elif metric == 'total_mfg_ghg_kg':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        average_mfg = df.groupby(['iso3', 'adoption_scenario', 
                    'geotype', 'emission_category', 
                    'lca_phase_ghg_kg'])['total_mfg_ghg_kg'].mean()
        total_mfg = df.groupby(['iso3', 'adoption_scenario', 
                    'geotype', 'emission_category', 
                    'lca_phase_ghg_kg'])['total_mfg_ghg_kg'].sum()
        fileout_10 = '{}_average_mfg.csv'.format(iso3)
        fileout_sum_10 = '{}_total_mfg.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_10 = os.path.join(folder_out, fileout_10)
        path_out_sum_10 = os.path.join(folder_out, fileout_sum_10)
        average_mfg.to_csv(path_out_10)
        total_mfg.to_csv(path_out_sum_10)

    elif metric == '_baseline_mfg_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_baseline_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_baseline_mfg = df.groupby(['iso3', 'strategy', 
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_mfg_ghg_kg'].mean()
        fileout_sum_11 = '{}_baseline_total_mfg.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_10 = os.path.join(folder_out, fileout_sum_11)
        total_baseline_mfg.to_csv(path_out_sum_10)

    elif metric == '_baseline_eolt_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_baseline_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_baseline_eolt = df.groupby(['iso3', 'strategy', 
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_eolt_ghg_kg'].mean()
        fileout_sum_12 = '{}_baseline_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_11 = os.path.join(folder_out, fileout_sum_12)
        total_baseline_eolt.to_csv(path_out_sum_11)

    else:

        path_in = os.path.join(DATA_RESULTS, iso3, 'supply', 
            '{}_supply_results.csv'.format(iso3))
    
        df = pd.read_csv(path_in)
        df = df.fillna(1)
        
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
            
        #if not country['iso3'] == 'AGO':
            
            continue 
        try:
            #summations(countries['iso3'].loc[idx], 'rev_per_area')
            #summations(countries['iso3'].loc[idx], 'tco_per_user')
            #summations(countries['iso3'].loc[idx], 'demand_mbps_sqkm')
            #summations(countries['iso3'].loc[idx], 'emissions_kg_per_subscriber')
            #summations(countries['iso3'].loc[idx], 'total_mfg_ghg_kg')
            #summations(countries['iso3'].loc[idx], 'total_eolt_ghg_kg')
            #summations(countries['iso3'].loc[idx], '_baseline_mfg_emission')
            #summations(countries['iso3'].loc[idx], '_baseline_eolt_emission')
            pass
        except:

            pass

csv_merger('_demand_results.csv', 'demand')
csv_merger('_supply_results.csv', 'supply')
csv_merger('_rev_per_area_average.csv', 'summary')
csv_merger('_rev_per_area_total.csv', 'summary')
csv_merger('_tco_per_user_total.csv', 'summary')
csv_merger('_tco_per_user_average.csv', 'summary')
csv_merger('_geotype_total_area.csv', 'summary')
csv_merger('_geotype_population.csv', 'summary')
csv_merger('_demand_user.csv', 'demand')
csv_merger('_average_demand.csv', 'summary')
csv_merger('_emission_results.csv', 'emissions')
csv_merger('_emission_subscriber_average.csv', 'summary')
csv_merger('_emission_subscriber_total.csv', 'summary')
csv_merger('_baseline_emission_results.csv', 'emissions')
csv_merger('_baseline_tco_results.csv', 'supply')
csv_merger('_baseline_total_mfg.csv', 'summary')
csv_merger('_baseline_total_eolt.csv', 'summary')
