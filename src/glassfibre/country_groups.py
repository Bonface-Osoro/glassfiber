'''This scripts provides the classification of countries by region 
and income according to world bank

[1] “World Bank Country and Lending Groups - World Bank Data Help Desk.
” https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups 
(accessed Aug. 09, 2023).
'''

##### INCOME CLASSIFICATION ####
low_income = ['AFG', 'PRK', 'SSD', 'BFA', 'LBR', 'SDN', 'BDI', 'MDG', 'SYR', 
              'CAF', 'MWI', 'TGO', 'TCD', 'MLI', 'UGA', 'COD', 'MOZ', 'YEM', 
              'ERI', 'NER', 'ETH', 'RWA', 'GMB', 'SLE', 'GNB', 'SOM', 'VEN']

low_middle = ['AGO', 'JOR', 'PHL', 'DZA', 'IND', 'WSM', 'BGD', 'IRN', 'STP', 
              'BEN', 'KEN', 'SEN', 'BTN', 'KIR', 'SLB', 'BOL', 'KGZ', 'LKA', 
              'CPV', 'LAO', 'TZA', 'KHM', 'LBN', 'TJK', 'CMR', 'LSO', 'TLS', 
              'COM', 'MRT', 'TUN', 'COG', 'FSM', 'UKR', 'CIV', 'MNG', 'UZB', 
              'DJI', 'MAR', 'VUT', 'EGY', 'MMR', 'VNM', 'SWZ', 'NPL', 'ZMB',
              'GHA', 'NIC', 'ZWE', 'GIN', 'NGA', 'HTI', 'PAK', 'HND', 'PNG']

upper_income = ['ALB', 'FJI', 'MKD', 'ARG', 'GAB', 'PLW', 'ARM', 'GEO', 'PRY', 
                'AZE', 'GRD', 'PER', 'BLR', 'GTM', 'RUS', 'BLZ', 'IDN', 'SRB', 
                'BIH', 'IRQ', 'ZAF', 'BWA', 'JAM', 'LCA', 'BRA', 'KAZ', 'VCT', 
                'BGR', 'XKX', 'SUR', 'CHN', 'LBY', 'THA', 'COL', 'MYS', 'TON', 
                'CRI', 'MDV', 'TUR', 'CUB', 'MHL', 'TKM', 'DMA', 'MUS', 'TUV',
                'DOM', 'MEX', 'PSE', 'SLV', 'MDA', 'GNQ', 'MNE', 'ECU', 'NAM',
                'GUY']

high_income = ['ASM', 'DEU', 'OMN', 'AND', 'GIB', 'PAN', 'ATG', 'GRC', 'POL', 'ABW',
               'GRL', 'PRT', 'AUS', 'GUM', 'PRI', 'AUT', 'HKG', 'QAT', 'BHS', 'HUN',
               'ROU', 'BHR', 'ISL', 'SMR', 'BRB', 'IRL', 'SAU', 'BEL', 'IMN', 'SYC',
               'BMU', 'ISR', 'SGP', 'VGB', 'ITA', 'SXM', 'BRN', 'JPN', 'SVK', 'CAN',
               'KOR', 'SVN', 'CYM', 'KWT', 'ESP', 'JEY', 'LVA', 'KNA', 'CHL', 'LIE',
               'MAF', 'HRV', 'LTU', 'SWE', 'CUW', 'LUX', 'CHE', 'CYP', 'MAC', 'TWN',
               'CZE', 'MLT', 'TTO', 'DNK', 'MCO', 'TCA', 'EST', 'NRU', 'ARE', 'FRO',
               'NLD', 'GBR', 'FIN', 'NCL', 'USA', 'FRA', 'NZL', 'URY', 'PYF', 'MNP',
               'VIR', 'NOR']

##### REGIONAL CLASSIFICATION ######
middle_north_africa = ['DZA', 'JOR', 'QAT', 'BHR', 'KWT', 'SAU', 'DJI', 'LBN', 'SYR', 
                       'EGY', 'LBY', 'TUN', 'IRN', 'MLT', 'ARE', 'IRQ', 'MAR', 'PSE', 
                       'ISR', 'OMN', 'YEM']

sub_saharan_africa = ['AGO', 'ETH', 'NER', 'BEN', 'GAB', 'NGA', 'BWA', 'GMB', 'RWA', 'BFA', 
                      'GHA', 'STP', 'BDI', 'GIN', 'SEN', 'CPV', 'GNB', 'SYC', 'CMR', 'KEN', 
                      'SLE', 'CAF', 'LSO', 'SOM', 'TCD', 'LBR', 'ZAF', 'COM', 'MDG', 'SSD', 
                      'COD', 'MWI', 'SDN', 'COG', 'MLI', 'TZA', 'CIV', 'MRT', 'TGO', 'GNQ', 
                      'MUS', 'UGA', 'ERI', 'MOZ', 'ZMB', 'SWZ', 'NAM', 'ZWE']