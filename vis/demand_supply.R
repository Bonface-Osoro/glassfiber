library(ggpubr)
library(ggplot2)
library(tidyverse)
library(cowplot)
library(ggtext)
library(sf)
library(flextable)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
#######################
##TOTAL POPULATION ####
#######################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_subregional_population_deciles.csv'))
df = data %>%
  distinct(decile, population, .keep_all = TRUE) %>%
  group_by(decile) %>%
  summarize(total_pops = round(sum(population)/1e6))

df$decile = factor(df$decile,
  levels = c('decile 1', 'decile 2', 'decile 3', 'decile 4', 'decile 5',
  'decile 6', 'decile 7', 'decile 8', 'decile 9', 'decile 10'),
  labels = c('Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
  'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
  'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
  'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
  'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

total_population <- 
  ggplot(df, aes(x = decile, y = total_pops, fill = decile)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) + coord_flip() +
  geom_text(aes(label = as.character(signif(total_pops, 3))), size = 2.5, 
            position = position_dodge(0.9), vjust = 0.05, hjust = -0.1) +
  labs(colour = NULL, title = '(a) Population decile classification of SSA.',
       subtitle = 'Based on population geotypes.',
       x = NULL, y = "Population (millions)") + 
  scale_fill_brewer(palette = "Spectral") +
  theme(
    legend.position = 'none',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11, face = "bold"),
    plot.subtitle = element_text(size = 9),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    axis.title.x = element_text(size = 7)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Demand Scenario')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 280))
#######################
##TOTAL POPULATION ####
#######################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_subregional_population_deciles.csv'))
df = data %>%
  distinct(decile, area, .keep_all = TRUE) %>%
  group_by(decile) %>%
  summarize(total_area = round(sum(area)/1e6, 3))

df$decile = factor(df$decile,
   levels = c('decile 1', 'decile 2', 'decile 3', 'decile 4', 'decile 5',
   'decile 6', 'decile 7', 'decile 8', 'decile 9', 'decile 10'),
   labels = c('Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
   'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
   'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
   'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
   'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

total_area <- 
  ggplot(df, aes(x = decile, y = total_area, fill = decile)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) + coord_flip() +
  geom_text(aes(label = as.character(signif(total_area, 3))), size = 2.5, 
            position = position_dodge(0.9), vjust = 0.05, hjust = -0.1) +
  labs(colour = NULL, title = '(b) Total area classification of SSA.',
       subtitle = 'Based on population geotypes.',
       x = NULL, y = "Area (million km²)") + 
  scale_fill_brewer(palette = "Spectral") +
  theme(
    legend.position = 'none',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11, face = "bold"),
    plot.subtitle = element_text(size = 9),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    axis.title.x = element_text(size = 7)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6)) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 21))

################################
## CAPACITY DEMAND PANEL PLOT ##
################################
pop_panel <- ggarrange(total_population, 
  total_area,
  ncol = 2, nrow = 1)

path = file.path(folder, 'figures', 'population_area.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(path, units = "in", width = 11, height = 5, res = 480)
print(pop_panel)
dev.off()

############################
##TOTAL DEMAND PER AREA ####
############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_demand_user.csv'))

df = data %>%
  group_by(geotype, adoption_scenario, monthly_traffic) %>%
  summarize(average_demand = mean(demand_mbps_sqkm, na.rm = TRUE))

df$adoption_scenario = factor(
  df$adoption_scenario,
  levels = c('low', 'baseline', 'high'),
  labels = c('Low', 'Baseline', 'High')
)

df$monthly_traffic = factor(
  df$monthly_traffic,
  levels = c(10, 15, 20, 30),
  labels = c('10 GB', '15 GB', '20 GB', '30 GB')
)

df$geotype = factor(df$geotype,
  levels = c('decile 1', 'decile 2', 'decile 3', 'decile 4', 'decile 5',
  'decile 6', 'decile 7', 'decile 8', 'decile 9', 'decile 10'),
  labels = c('Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
  'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
  'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
  'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
  'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

demand_area <- 
  ggplot(df, aes(x = geotype, y = average_demand, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) + coord_flip() + 
  geom_text(aes(label = as.character(signif(average_demand, 3))), size = 2.2, 
    position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  labs(colour = NULL, title = '(a) Total Demand per Area.',
    subtitle = 'Based on geotype, demand scenario and monthly traffic.',
    x = NULL, y = "Total Demand per Area (Mbps per km²)") + 
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'none',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    axis.title.x = element_text(size = 7)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Demand Scenario')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
    labels = function(y)format(y, scientific = FALSE), limit = c(0, 280)) + 
  facet_wrap( ~ monthly_traffic, ncol = 2)

##################
##DEMAND MAPS ####
##################
africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 
     'Africa_Boundaries', 'SSA_combined_shapefile.shp'))
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
      'SSA_demand_user.csv'))
data <- data[data$adoption_scenario == 'baseline', ]

data = data %>%
  distinct(iso3, GID_2, monthly_traffic, .keep_all = TRUE) %>%
  group_by(GID_2, monthly_traffic) %>%
  summarize(avg_demand = sum(demand_mbps_sqkm))

merged_data <- merge(africa_data, data, by = "GID_2")
merged_data <- merged_data[!duplicated(merged_data$avg_demand), ]
demand_bins <- c(-Inf, 0.1, 0.5, 1, 3, 5, 10, 15, 20, Inf)
merged_data$demand_bins <- cut(merged_data$avg_demand, breaks = demand_bins, 
    labels = 
    c("Below 0.1", "0.11 - 0.5", "0.51 - 1", "1.1 - 3", "3.1 - 5", "5.1 - 10", 
      "11 - 15", "16 - 20", "Above 20"))
merged_data$monthly_traffic = factor(
  merged_data$monthly_traffic,
  levels = c(10, 15, 20, 30),
  labels = c('10 GB', '15 GB', '20 GB', '30 GB')
)

demand_map <- ggplot() +
  geom_sf(data = merged_data, aes(fill = demand_bins), linewidth = 0.001,) + 
  labs(title = "(b) Total demand per area distribution.",
  subtitle = "Estimated for baseline adoption scenario and different monthly traffic.",
       fill = "Demand per Area \n  (Mbps per km²)") + 
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 6),
    axis.title.y = element_markdown(size = 6),
    legend.title = element_text(size = 7),
    legend.text = element_text(size = 7)) + 
  guides(fill = guide_legend(nrow = 2)) + 
  facet_wrap( ~ monthly_traffic, ncol = 4) +
  guides(fill = guide_legend(nrow = 1))

################################
## CAPACITY DEMAND PANEL PLOT ##
################################
demand_panel <- ggarrange(
  demand_area, 
  demand_map,
  ncol = 1, nrow = 2, 
  legend = 'bottom',
  heights = c(2, 1) )


path = file.path(folder, 'figures', 'demand.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 8,
  height = 10,
  res = 480
)
print(demand_panel)
dev.off()

##############################
##TOTAL COST OF OWNERSHIP ####
##############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_tco_results.csv'))

df = data %>%
  group_by(algorithm, strategy) %>%
  summarize(total_tco = (sum(tco)) / 1e6) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 'New Access Network')
)

df$algorithm <- factor(
  df$algorithm,
  levels = c('none', 'Dijkstras', 'pcsf'),
  labels = c('Unknown', 'Dijkstras', 'PCSF')
)

totals <- df %>%
  group_by(algorithm) %>%
  summarize(value = signif(sum(total_tco)))

total_tco_algorithm <- 
  ggplot(df, aes(x = algorithm, y = total_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) +
  geom_text(aes(x = algorithm, y = value, label = round(value, 0)
  ),size = 2.5, data = totals, vjust = 0.06, hjust = 0.5, 
  position = position_dodge(0.9)) + 
  labs(colour = NULL, title = '(a) Total Cost of Ownership (TCO).',
       subtitle = 'Grouped by network level and algorithm.',
       x = 'Spatial Optimization Algorithm', y = "TCO (US$ millions)") + 
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 8),
    axis.title.x = element_text(size = 8)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 1499))

###########################
##AVERAGE TCO PER USER ####
###########################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
        'SSA_tco_results.csv'))

df = data %>%
  group_by(algorithm, strategy) %>%
  summarize(avg_tco_per_user = (mean(tco_per_user)) / 1e3) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 'New Access Network')
)

df$algorithm <- factor(
  df$algorithm,
  levels = c('none', 'Dijkstras', 'pcsf'),
  labels = c('Unknown', 'Dijkstras', 'PCSF')
)

totals <- df %>%
  group_by(algorithm) %>%
  summarize(value = signif(sum(avg_tco_per_user)))

average_tco_user <- 
  ggplot(df, aes(x = algorithm, y = avg_tco_per_user)) +
  geom_bar(stat = "identity", aes(fill = strategy)) +
  geom_text(aes(x = algorithm, y = value, label = round(value, 0)
  ),size = 2.5, data = totals, vjust = 0.06, hjust = 0.5, 
  position = position_dodge(0.9)) + 
  labs(colour = NULL, title = '(b) Average TCO per user.',
       subtitle = 'Per user TCO averaged for each SSA country.',
       x = 'Spatial Optimization Algorithm', y = "Average TCO (US$/User '000')") + 
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 8),
    axis.title.x = element_text(size = 8)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Fiber Hirearchy')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 115))

##############################
##ANNUALIZED TCO PER USER ####
##############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_tco_results.csv'))

df = data %>%
  group_by(algorithm, strategy) %>%
  summarize(avg_tco_per_user = (mean(tco_per_user)) / 30) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 'New Access Network')
)

df$algorithm <- factor(
  df$algorithm,
  levels = c('none', 'Dijkstras', 'pcsf'),
  labels = c('Unknown', 'Dijkstras', 'PCSF')
)

totals <- df %>%
  group_by(algorithm) %>%
  summarize(value = signif(sum(avg_tco_per_user)))

annualized_tco_user <- 
  ggplot(df, aes(x = algorithm, y = avg_tco_per_user)) +
  geom_bar(stat = "identity", aes(fill = strategy)) +
  geom_text(aes(x = algorithm, y = value, label = round(value, 0)
  ),size = 2.5, data = totals, vjust = 0.06, hjust = 0.5, 
  position = position_dodge(0.9)) + 
  labs(colour = NULL, title = '(c) Annualized TCO per user.',
       subtitle = 'Estimated for 20-year assessment period.',
       x = 'Spatial Optimization Algorithm', y = "Annualized TCO (US$/User)") + 
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 8),
    axis.title.x = element_text(size = 8)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network Level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 5599))

##############################
##MONTHLY TCO PER USER ####
##############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_tco_results.csv'))

df = data %>%
  group_by(algorithm, strategy) %>%
  summarize(avg_tco_per_user = (mean(tco_per_user)) / 360) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 'New Access Network')
)

df$algorithm <- factor(
  df$algorithm,
  levels = c('none', 'Dijkstras', 'pcsf'),
  labels = c('Unknown', 'Dijkstras', 'PCSF')
)

totals <- df %>%
  group_by(algorithm) %>%
  summarize(value = signif(sum(avg_tco_per_user)))

monthly_tco_user <- 
  ggplot(df, aes(x = algorithm, y = avg_tco_per_user)) +
  geom_bar(stat = "identity", aes(fill = strategy)) +
  geom_text(aes(x = algorithm, y = value, label = round(value, 1)
  ),size = 2.5, data = totals, vjust = -0.5, hjust = 0.5, 
  position = position_dodge(0.9)) + 
  labs(colour = NULL, title = '(d) Monthly TCO per user.',
       subtitle = 'Estimated for 20-year assessment period.',
       x = 'Spatial Optimization Algorithm', y = "Mean Monthly TCO (US$/User)") + 
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 8),
    axis.title.x = element_text(size = 8)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network Level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 479))

#################
##PER USER TCO ##
#################
per_user_tco_panel <- ggarrange(
  total_tco_algorithm, 
  average_tco_user, 
  annualized_tco_user,
  monthly_tco_user,
  legend = 'bottom',
  common.legend = TRUE,
  ncol = 4)

path = file.path(folder, 'figures', 'per_user_tco.png')
png(path, units = "in", width = 11, height = 3.5, res = 300)
print(per_user_tco_panel)
dev.off()

##########################################
##DIJKSTRAS: AVERAGE REVENUE PER USER ####
##########################################
africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 'Africa_Boundaries', 'SSA_combined_shapefile.shp'))
africa_shp <- africa_data %>%
  select(GID_0, NAME_0, GID_1, GID_2, geometry)

new_names <- c('iso3', 'country', 'GID_1', 'GID_2', 'geometry')
colnames(africa_shp) <- new_names
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_tco_results.csv'))

data = data %>%
  group_by(GID_2, tco_per_user) %>%
  summarize(tco_per_user)

merged_data <- merge(africa_shp, data, by = "GID_2")
pop_bins <- c(-Inf, 500, 1000, 5000, 10000, 15000, 20000, 
              30000, 40000, 50000, Inf)

merged_data$population_bin <- cut(merged_data$tco_per_user, breaks = pop_bins, 
   labels = c("Below 500", "501 - 1000", "1 - 5k", "5.1 - 10k", 
   "10.1 - 15k", "15.1 - 20k", "20.1 - 30k", 
   "30.1 - 40k", "40.1 - 50k", "Above 50k"))

djikstra_maps <- ggplot() + 
  geom_sf(data = africa_shp, fill = "red4", color = "black", linewidth = 0.01) + 
  geom_sf(data = merged_data, aes(fill = population_bin), 
          linewidth = 0.001,) +
  scale_fill_brewer(palette = "Spectral") +
  labs(title = "(c) TCO per user: Djikistra algorithm.",
       subtitle = "Based on fiber design using Djikistra's algorithm.",
       fill = "Range") + theme_void()+
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.6, "lines"),
    plot.subtitle = element_text(size = 10),
    plot.title = element_text(size = 10, face = "bold")
  )

############################
##TCO PER USER: DIJKSTRAS###
############################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_local_tco_results.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'tco_per_user')]

#### Regional TCO per user ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_regional_tco_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'tco_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_tco = mean(tco_per_user)) 

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

djikistra_tco <-
  ggplot(df, aes(x = decile, y = mean_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
    label = sprintf("%.0f", mean_value)), size = 3,
    position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Total Cost of Ownership (TCO) per user.",
       subtitle = "(a) Fiber design using Dijkstras algorithm.",
       x = NULL, y = bquote("TCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 10, face = "bold"),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 114000))

#######################
##TCO PER USER: PCSF###
#######################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_local_tco_results.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'tco_per_user')]

#### Regional TCO per user ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_regional_tco_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'tco_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_tco = mean(tco_per_user)) 

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

pcsf_tco <-
  ggplot(df, aes(x = decile, y = mean_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(b) Fiber design using PCSF algorithm.",
       x = NULL, y = bquote("TCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 10, face = "bold"),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 30000))

#######################################
##ANNUALIZED TCO PER USER: DIJKSTRAS###
#######################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_local_tco_results.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'tco_per_user')]

#### Regional TCO per user ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_regional_tco_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'tco_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_tco = (mean(tco_per_user))/30) 

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

djikistra_annualized_tco <-
  ggplot(df, aes(x = decile, y = mean_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Annualized TCO per user.",
       subtitle = "(c) Fiber design using Dijkstras algorithm.",
       x = NULL, y = bquote("Annualized TCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 10, face = "bold"),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 5700))

##################################
##ANNUALIZED TCO PER USER: PCSF###
##################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_local_tco_results.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'tco_per_user')]

#### Regional TCO per user ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_regional_tco_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'tco_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_tco = (mean(tco_per_user))/30) 

df$decile = factor(df$decile,
   levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
   'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
   labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
   'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
   'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
   'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
   'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

pcsf_annualized_tco <-
  ggplot(df, aes(x = decile, y = mean_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
  label = sprintf("%.0f", mean_value)), size = 3,
  position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(d) Fiber design using PCSF algorithm.",
       x = NULL, y = bquote("Annualized TCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 10, face = "bold"),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 5700))

#########################################
##MEAN MONTHLY TCO PER USER: DIJKSTRAS###
#########################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_local_tco_results.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'tco_per_user')]

#### Regional TCO per user ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_regional_tco_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'tco_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_tco = (mean(tco_per_user))/360) 

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

djikistra_monthly_tco <-
  ggplot(df, aes(x = decile, y = mean_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Mean Monthly TCO per user.",
       subtitle = "(e) Fiber design using Dijkstras algorithm.",
       x = NULL, y = bquote("Mean Monthly TCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 10, face = "bold"),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 459))

#####################################
##MEAN MONTHLY TCO PER USER: PCSF ###
#####################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_local_tco_results.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'tco_per_user')]

#### Regional TCO per user ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_regional_tco_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'tco_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_tco = (mean(tco_per_user))/360) 

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

pcsf_monthly_tco <-
  ggplot(df, aes(x = decile, y = mean_tco)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(f) Fiber design using PCSF algorithm.",
       x = NULL, y = bquote("Mean Monthly TCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 10, face = "bold"),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 459))

#######################
##PANEL TCO PER USER ##
#######################
aggregate_tco <- ggarrange(
  djikistra_tco, 
  pcsf_tco, 
  djikistra_annualized_tco,
  pcsf_annualized_tco,
  djikistra_monthly_tco,
  pcsf_monthly_tco,
  ncol = 2, nrow = 3, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_tco.png')
png(path, units="in", width=11, height=12, res=300)
print(aggregate_tco)
dev.off()
