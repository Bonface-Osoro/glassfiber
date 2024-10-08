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
DATA_SSA = os.path.join(BASE_PATH, '..', 'results', 'SSA')

path = os.path.join(DATA_RAW, 'countries.csv')
countries = pd.read_csv(path, encoding = 'utf-8-sig')

southern = ['AGO', 'ZMB', 'ZWE', 'NAM', 'BWA', 'ZAF', 'LSO', 
            'SWZ', 'MOZ', 'MWI']

central = ['CMR', 'CAF', 'TCD', 'COD', 'GNQ', 'GAB', 'STP', 'COG']

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
                    merged_data = pd.concat([merged_data, df], ignore_index = True)

                    if csv_name == '_geotype_population.csv':

                        merged_data = merged_data.groupby(['geotype'])['population'].sum().reset_index()

                    if csv_name == '_geotype_total_area.csv':

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['geotype']
                                    )['area'].sum().reset_index()

                    if csv_name == '_baseline_emission_results.csv':

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['iso3', 'GID_2']
                        )['emissions_kg_per_subscriber'].mean().reset_index()

                    if csv_name == '_country_baseline_emission.csv':  

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['iso3', 'strategy', 
                            'algorithm']).agg({'total_ghg_emissions_kg': 'sum', 
                            'emissions_kg_per_subscriber': 'sum',
                            'total_ssc_usd': 'sum',
                            'ssc_per_user': 'sum'}).reset_index()
                        
                    if csv_name == '_country_local_emission.csv': 

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['iso3', 'strategy', 
                            'algorithm']).agg({'total_ghg_emissions_kg': 'sum', 
                            'emissions_kg_per_subscriber': 'sum',
                            'total_ssc_usd': 'sum',
                            'ssc_per_user': 'sum'}).reset_index()
                        
                    if csv_name == '_baseline_tco_results.csv':  

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['iso3', 'strategy', 
                            'algorithm'] ).agg({'tco': 'mean', 
                            'tco_per_user': 'mean'}).reset_index()
                        
                    if csv_name == '_local_tco_results.csv':  

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['iso3', 'GID_2', 
                                    'strategy', 'algorithm']).agg({'tco': 'mean', 
                                    'tco_per_user': 'mean'}).reset_index()  

                    if csv_name == '_regional_emission.csv': 

                        df = pd.read_csv(file_path) 
                        merged_data = pd.concat([merged_data, df], ignore_index = True)
                        merged_data = merged_data.groupby(['iso3', 'strategy', 
                                    'algorithm']).agg({'total_ghg_emissions_kg': 'mean', 
                                    'emissions_kg_per_subscriber': 'mean',
                                    'total_ssc_usd': 'mean',
                                    'ssc_per_user': 'mean'}).reset_index()   
                      
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

    elif metric == '_total_eolt_ghg_kg':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        average_eolt = df.groupby(['iso3', 'adoption_scenario', 
                    'emission_category', 'lca_phase_ghg_kg'])[
                        'total_eolt_ghg_kg'].mean()
        total_eolt = df.groupby(['iso3', 'emission_category', 
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

    elif metric == '_total_mfg_ghg_kg':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        print(df.head(3))
        average_mfg = df.groupby(['iso3', 'adoption_scenario', 
                    'emission_category', 'lca_phase_ghg_kg'])[
                        'total_mfg_ghg_kg'].mean()
        total_mfg = df.groupby(['iso3', 'adoption_scenario', 'emission_category', 
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
        total_baseline_mfg = df.groupby(['iso3', 'strategy', 'algorithm',
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
        total_baseline_eolt = df.groupby(['iso3', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_eolt_ghg_kg'].mean()
        fileout_sum_12 = '{}_baseline_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_11 = os.path.join(folder_out, fileout_sum_12)
        total_baseline_eolt.to_csv(path_out_sum_11)

    elif metric == '_local_mfg_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_local_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_mfg = df.groupby(['iso3', 'GID_2', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_mfg_ghg_kg'].mean()
        fileout_sum_13 = '{}_local_total_mfg.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_12 = os.path.join(folder_out, fileout_sum_13)
        total_local_mfg.to_csv(path_out_sum_12)

    elif metric == '_local_eolt_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_local_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_eolt = df.groupby(['iso3', 'GID_2', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_eolt_ghg_kg'].mean()
        fileout_sum_14 = '{}_local_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_13 = os.path.join(folder_out, fileout_sum_14)
        total_local_eolt.to_csv(path_out_sum_13)
   
    elif metric == '_regional_mfg_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_regional_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_eolt = df.groupby(['iso3', 'GID_1', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_mfg_ghg_kg'].mean()
        fileout_sum_14 = '{}_regional_total_mfg.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_13 = os.path.join(folder_out, fileout_sum_14)
        total_local_eolt.to_csv(path_out_sum_13)
    
    elif metric == '_regional_eolt_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_regional_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_eolt = df.groupby(['iso3', 'GID_1', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_eolt_ghg_kg'].mean()
        fileout_sum_14 = '{}_regional_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_13 = os.path.join(folder_out, fileout_sum_14)
        total_local_eolt.to_csv(path_out_sum_13)


    elif metric == '_pcsf_local_mfg_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_pcsf_local_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_mfg = df.groupby(['iso3', 'GID_2', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_mfg_ghg_kg'].mean()
        fileout_sum_15 = '{}_pcsf_local_total_mfg.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_14 = os.path.join(folder_out, fileout_sum_15)
        total_local_mfg.to_csv(path_out_sum_14)

    elif metric == '_pcsf_local_eolt_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_pcsf_local_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_eolt = df.groupby(['iso3', 'GID_2', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_eolt_ghg_kg'].mean()
        fileout_sum_16 = '{}_pcsf_local_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_15 = os.path.join(folder_out, fileout_sum_16)
        total_local_eolt.to_csv(path_out_sum_15)

    elif metric == '_pcsf_regional_mfg_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_pcsf_regional_mfg_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_eolt = df.groupby(['iso3', 'GID_1', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_mfg_ghg_kg'].mean()
        fileout_sum_17 = '{}_pcsf_regional_total_mfg.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_16 = os.path.join(folder_out, fileout_sum_17)
        total_local_eolt.to_csv(path_out_sum_16)

    elif metric == '_pcsf_regional_eolt_emission':

        path_in = os.path.join(DATA_RESULTS, iso3, 'emissions', 
            '{}_pcsf_regional_eolt_emission_results.csv'.format(iso3))
        df = pd.read_csv(path_in)
        total_local_eolt = df.groupby(['iso3', 'GID_1', 'strategy', 'algorithm',
                    'emission_category', 'lca_phase_ghg_kg']
                    )['total_eolt_ghg_kg'].mean()
        fileout_sum_18 = '{}_pcsf_regional_total_eolt.csv'.format(iso3)
        folder_out = os.path.join(DATA_RESULTS, iso3, 'summary')

        if not os.path.exists(folder_out):

            os.makedirs(folder_out)

        path_out_sum_17 = os.path.join(folder_out, fileout_sum_18)
        total_local_eolt.to_csv(path_out_sum_17)


    else:

        pass
        
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


def ssa_csv_merger(csv_name):
    """
    This funcion read and merge multiple CSV files located in different folders.

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
    DATA_SSA = os.path.join(BASE_PATH, '..', 'results', 'SSA')

    merged_data = pd.DataFrame()

    print('Merging {} files'. format(csv_name))
    base_directory = os.path.join(DATA_SSA) 

    for root, _, files in os.walk(base_directory):

        for file in files:

            if file.endswith('{}'.format(csv_name)):
                
                file_path = os.path.join(base_directory, file)
                df = pd.read_csv(file_path)
                merged_data = pd.concat([merged_data, df], ignore_index = True)

                if csv_name == '_emission.csv':  

                    merged_data = merged_data.groupby(['iso3', 'strategy', 
                        'algorithm']).agg({'total_ghg_emissions_kg': 'sum', 
                        'emissions_kg_per_subscriber': 'sum'}).reset_index()
                    
                    merged_data = merged_data[['iso3', 
                        'emissions_kg_per_subscriber', 'total_ghg_emissions_kg', 
                        'strategy', 'algorithm']]
                    
                if csv_name == '_tco_results.csv':  

                    merged_data = merged_data.groupby(['iso3', 'strategy',
                        'algorithm']).agg({'tco': 'mean','tco_per_user': 'mean'}
                        ).reset_index()
                    
                    merged_data = merged_data[['iso3', 'tco', 'tco_per_user', 
                        'strategy', 'algorithm']]
                    
                if csv_name == '_local_emission_results.csv':  

                    merged_data = merged_data.groupby(['iso3', 'strategy', 'GID_2',
                        'algorithm']).agg({'total_ghg_emissions_kg': 'mean',
                        'emissions_kg_per_subscriber': 'mean'}
                        ).reset_index()
                    
                    merged_data = merged_data[['iso3', 'GID_2', 
                        'total_ghg_emissions_kg', 'emissions_kg_per_subscriber', 
                        'strategy', 'algorithm']]
                    
                             
                merged_data['algorithm'] = merged_data['algorithm'].fillna(
                    'Dijkstras')
                
                fileout = 'SSA{}'.format(csv_name)
                folder_out = os.path.join(DATA_SSA)

                if not os.path.exists(folder_out):

                    os.makedirs(folder_out)

                path_out = os.path.join(folder_out, fileout)
                merged_data.to_csv(path_out, index = False)

    return None


def ssa_hireachy_emissions(csv_name):
    """
    This funcion read and merge multiple CSV files located  in different folders.

    Parameters
    ----------
    csv_name : string
        Name of the file to process. It can be '_local_emission_results.csv'
    """

    isos = os.listdir(DATA_RESULTS)

    merged_data = pd.DataFrame()
    for iso3 in isos:

        print('Merging {} csv files'. format(iso3))
        base_directory = os.path.join(DATA_RESULTS, iso3, 'emissions') 

        for root, _, files in os.walk(base_directory):

            for file in files:

                try:
                
                    if file.endswith('{}'.format(csv_name)):

                        file_path = os.path.join(base_directory, '{}{}'.format(iso3, csv_name))

                        if csv_name == '_local_emission_results.csv':  

                            df = pd.read_csv(file_path)
                            merged_data = pd.concat([merged_data, df], ignore_index = True)

                        if csv_name == '_pcsf_local_emission_results.csv':  

                            df = pd.read_csv(file_path)
                            merged_data = pd.concat([merged_data, df], ignore_index = True)

                        if csv_name == '_regional_emission_results.csv':  

                            df = pd.read_csv(file_path)
                            merged_data = pd.concat([merged_data, df], ignore_index = True)

                        if csv_name == '_pcsf_regional_emission_results.csv':  

                            df = pd.read_csv(file_path)
                            merged_data = pd.concat([merged_data, df], ignore_index = True)

                        fileout = 'SSA{}'.format(csv_name)
                        folder_out = os.path.join(DATA_RESULTS, '..', 'SSA', 
                                                'fiber_levels')

                        if not os.path.exists(folder_out):

                            os.makedirs(folder_out)

                        path_out = os.path.join(folder_out, fileout)
                        merged_data.to_csv(path_out, index = False)

                except:

                    pass


if __name__ == '__main__':
    
    for idx, country in countries.iterrows():
            
        if not country['region'] == 'Sub-Saharan Africa' or country['Exclude'] == 1:
            
        #if not country['iso3'] == 'GMB':
            
            continue 

        try:

            '''summations(countries['iso3'].loc[idx], '_baseline_mfg_emission')
            summations(countries['iso3'].loc[idx], '_baseline_eolt_emission')

            ### Prim's algorithm ####
            summations(countries['iso3'].loc[idx], '_local_mfg_emission')
            summations(countries['iso3'].loc[idx], '_local_eolt_emission')
            summations(countries['iso3'].loc[idx], '_regional_mfg_emission')
            summations(countries['iso3'].loc[idx], '_regional_eolt_emission')

            ### PCSF algorithm ####
            summations(countries['iso3'].loc[idx], '_pcsf_local_mfg_emission')
            summations(countries['iso3'].loc[idx], '_pcsf_local_eolt_emission')
            summations(countries['iso3'].loc[idx], '_pcsf_regional_mfg_emission')
            summations(countries['iso3'].loc[idx], '_pcsf_regional_eolt_emission')'''

            pass

        except:

            pass

'''csv_merger('_demand_results.csv', 'demand')
csv_merger('_geotype_total_area.csv', 'summary')
csv_merger('_geotype_population.csv', 'summary')
csv_merger('_demand_user.csv', 'demand')
csv_merger('_average_demand.csv', 'summary')'''

########## TOTAL BASELINE AND LOCAL EMISSIONS ##########
'''csv_merger('_country_baseline_emission.csv', 'summary')

### Prim's algorithm ####
csv_merger('_country_local_emission.csv', 'summary')
csv_merger('_regional_emission.csv', 'summary')

### PCSF algorithm ####
csv_merger('_pcsf_country_local_emission.csv', 'summary')
csv_merger('_pcsf_regional_emission.csv', 'summary')

#ssa_csv_merger('_emission.csv')

###### TOTAL TCO AND PER USER TCO EMISSIONS ######
csv_merger('_baseline_tco_results.csv', 'supply')

### Prim's algorithm ####
csv_merger('_local_tco_results.csv', 'supply')
csv_merger('_regional_tco_results.csv', 'supply')

### PCSF algorithm ####
csv_merger('_pcsf_local_tco_results.csv', 'supply')
csv_merger('_pcsf_regional_tco_results.csv', 'supply')

ssa_csv_merger('_tco_results.csv')
ssa_csv_merger('_tco_results.csv')'''

############ TOTAL EMISSION TYPES ##############
#run after running summations
'''csv_merger('_baseline_total_mfg.csv', 'summary')
csv_merger('_baseline_total_eolt.csv', 'summary')

### Prim's algorithm ####
csv_merger('_local_total_mfg.csv', 'summary')
csv_merger('_local_total_eolt.csv', 'summary')
csv_merger('_regional_total_mfg.csv', 'summary')
csv_merger('_regional_total_eolt.csv', 'summary')

### PCSF algorithm ####
csv_merger('_pcsf_local_total_mfg.csv', 'summary')
csv_merger('_pcsf_local_total_eolt.csv', 'summary')
csv_merger('_pcsf_regional_total_mfg.csv', 'summary')
csv_merger('_pcsf_regional_total_eolt.csv', 'summary')

ssa_csv_merger('_total_mfg.csv')
ssa_csv_merger('_total_eolt.csv')

#### Results for decile plots ####
ssa_hireachy_emissions('_local_emission_results.csv')
ssa_hireachy_emissions('_pcsf_local_emission_results.csv')
ssa_hireachy_emissions('_regional_emission_results.csv')
ssa_hireachy_emissions('_pcsf_regional_emission_results.csv')
csv_merger('_demand_user.csv', 'demand')
csv_merger('_average_demand.csv', 'summary')'''


def process_fiber_metrics():
    """
    This is summarizes the population and distance covered by fiber cable at 
    access and regional network for both Prim's and PCST algorithms.

    """
    isos = os.listdir(DATA_RESULTS)

    merged_access = pd.DataFrame()
    merged_regional = pd.DataFrame()
    sub_dec = os.path.join(DATA_SSA, 'SSA_subregional_population_deciles.csv')
    reg_dec = os.path.join(DATA_SSA, 'SSA_regional_population_deciles.csv')
    dec = pd.read_csv(sub_dec)
    dec = dec[['GID_2', 'decile']]
    dec1 = pd.read_csv(reg_dec)
    dec1 = dec1[['GID_1', 'decile']]

    for iso3 in isos:

        print('Merging {} csv files'. format(iso3))
        path_in = os.path.join(DATA_RESULTS, iso3, 'fiber_design')

        access_mst = os.path.join(path_in, '{}_fiber_access.csv'.format(iso3))
        access_pcst = os.path.join(path_in, 
                                   '{}_fiber_pcsf_access.csv'.format(iso3))

        regional_mst = os.path.join(path_in, 
                                    '{}_fiber_regional.csv'.format(iso3))
        regional_pcst = os.path.join(path_in, 
                                     '{}_fiber_pcsf_regional.csv'.format(iso3))

        try:
        
            df = pd.read_csv(access_mst)
            df1 = pd.read_csv(access_pcst)
            df2 = pd.read_csv(regional_mst)
            df3 = pd.read_csv(regional_pcst)

            df = df.groupby(['GID_2', 'strategy', 'algorithm']).agg(
                total_population = ('population', 'sum'),
                mean_distance_km = ('length_km', 'mean'), nodes = 
                ('iso3', 'count')).reset_index()

            df1 = df1.groupby(['GID_2', 'strategy', 'algorithm']).agg(
                total_population = ('population', 'sum'),
                mean_distance_km = ('length_km', 'mean'), nodes = 
                ('iso3', 'count')).reset_index()

            df2 = df2.groupby(['GID_1', 'strategy', 'algorithm']).agg(
                total_population = ('population', 'sum'),
                mean_distance_km = ('length_km', 'mean'), nodes = 
                ('iso3', 'count')).reset_index()

            df3 = df3.groupby(['GID_1', 'strategy', 'algorithm']).agg(
                total_population = ('population', 'sum'),
                mean_distance_km = ('length_km', 'mean'), nodes = 
                ('iso3', 'count')).reset_index()

            access_df = pd.concat([df, df1], ignore_index = True)
            merged_access = pd.concat([merged_access, access_df], 
                                      ignore_index = True)
            regional_df = pd.concat([df2, df3], ignore_index = True)
            merged_regional = pd.concat([merged_regional, regional_df], 
                                        ignore_index = True)

            fileout = 'SSA_fiber_access.csv'
            fileout_1 = 'SSA_fiber_regional.csv'
            folder_out = os.path.join(DATA_RESULTS, '..', 'SSA', 
                                        'fiber_levels')

            if not os.path.exists(folder_out):

                os.makedirs(folder_out)

            path_out = os.path.join(folder_out, fileout)
            path_out_2 = os.path.join(folder_out, fileout_1)
            merged_access = pd.merge(merged_access, dec, on = 'GID_2', 
                                     how = 'inner')
            merged_access = merged_access[['GID_2', 'total_population', 
                                           'mean_distance_km', 'nodes', 
                                           'strategy', 'algorithm', 'decile']]
            merged_access.to_csv(path_out, index = False)
            merged_regional = pd.merge(merged_regional, dec1, on = 'GID_1', 
                                     how = 'inner')
            merged_regional = merged_regional[['GID_1', 'total_population', 
                                           'mean_distance_km', 'nodes', 
                                           'strategy', 'algorithm', 'decile']]
            merged_regional.to_csv(path_out_2, index = False)

        except:

            pass


    return None


def process_fiber_deciles():
    """
    This is summarizes the population and distance covered by fiber cable at 
    decile level.

    """
    sub_dec = os.path.join(DATA_SSA, 'fiber_levels', 'SSA_fiber_access.csv')
    reg_dec = os.path.join(DATA_SSA, 'fiber_levels', 'SSA_fiber_regional.csv')
    df = pd.read_csv(sub_dec)
    df1 = pd.read_csv(reg_dec)

    df = df.groupby(['decile', 'strategy', 'algorithm']).agg(
        total_population = ('total_population', 'mean'),
        mean_distance_km = ('mean_distance_km', 'mean'),
        nodes = ('nodes', 'mean'),).reset_index()
    
    df1 = df1.groupby(['decile', 'strategy', 'algorithm']).agg(
        total_population = ('total_population', 'mean'),
        mean_distance_km = ('mean_distance_km', 'mean'),
        nodes = ('nodes', 'mean'),).reset_index()
    
    df2 = pd.concat([df, df1], ignore_index = True)

    fileout = 'population_connected_fiber.csv'
    folder_out = os.path.join(DATA_RESULTS, '..', 'SSA')
    if not os.path.exists(folder_out):

        os.makedirs(folder_out)

    path_out = os.path.join(folder_out, fileout)
    df2.to_csv(path_out, index = False)


    return None