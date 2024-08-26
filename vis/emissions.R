library(ggpubr)
library(ggplot2)
library(dplyr)
library(tidyverse)
library("readxl")
library(ggtext)
library(sf)
library(ggspatial)
library(ggmap)
library(tidyr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
#############################
##TOTAL EMISSIONS: PRIM'S ###
#############################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'total_ghg_emissions_kg')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'total_ghg_emissions_kg')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(total_ghgs = sum(total_ghg_emissions_kg)) 

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
  summarize(total_value = sum(total_ghgs))

prims_total_emissions <-
  ggplot(df, aes(x = decile, y = total_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e9, 
  label = sprintf("%.0f", total_value/1e9)), size = 3,
  position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Total GHG Emissions.",
       subtitle = "(a) Fiber design using Prim's algorithm.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 19900))

##########################
##TOTAL EMISSIONS: PCST###
##########################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'total_ghg_emissions_kg')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'total_ghg_emissions_kg')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(total_ghgs = sum(total_ghg_emissions_kg)) 

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
  summarize(total_value = sum(total_ghgs))

pcsf_total_emissions <-
  ggplot(df, aes(x = decile, y = total_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e9, 
  label = sprintf("%.0f", total_value/1e9)), size = 3,
  position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = ' ',
       subtitle = "(b) Fiber design using PCST algorithm.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 19900))

########################################
###### AVERAGE PER USER EMISSIONS ######
########################################

###############################
##AVERAGE EMISSIONS: PRIM'S ###
###############################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(avg_ghgs = mean(emissions_kg_per_subscriber)) 

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
  summarize(mean_value = sum(avg_ghgs))

prims_average_emissions <-
  ggplot(df, aes(x = decile, y = avg_ghgs/1e3)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value/1e3, 
  label = sprintf("%.0f", mean_value/1e3)), size = 3,
  position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Average GHG Emissions",
       subtitle = "(c) Fiber design using Prim's algorithm.",
       x = NULL, 
       y = bquote("Average GHG emissions (t CO"[2]*" eq. per user)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 19900))

###########################
##AVERAGE EMISSIONS: PCST##
###########################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(avg_ghgs = mean(emissions_kg_per_subscriber)) 

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
  summarize(mean_value = sum(avg_ghgs))

pcsf_average_emissions <-
  ggplot(df, aes(x = decile, y = avg_ghgs/1e3)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value/1e3, 
    label = sprintf("%.0f", mean_value/1e3)), size = 3,
    position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = ' ',
       subtitle = "(d) Fiber design using PCST algorithm.",
       x = NULL, 
       y = bquote("Average GHG emissions (t CO"[2]*" eq. per user)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 19900))

##########################################
##ANNUALIZED AVERAGE EMISSIONS: PRIM'S ###
##########################################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(avg_ghgs = mean(emissions_kg_per_subscriber/30)) 

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
  summarize(mean_value = sum(avg_ghgs))

prims_annualized_emissions <-
  ggplot(df, aes(x = decile, y = avg_ghgs/1e3)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value/1e3, 
                                     label = sprintf("%.2f", mean_value/1e3)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Annualized GHG Emissions",
       subtitle = "(e) Fiber design using Prim's algorithm.",
       x = NULL, 
       y = bquote("Annualized GHG emissions (t CO"[2]*" eq. per user)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 19900))

###########################
##AVERAGE EMISSIONS: PCST##
###########################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'emissions_kg_per_subscriber')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(avg_ghgs = sum(emissions_kg_per_subscriber/30)) 

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
  summarize(mean_value = mean(avg_ghgs))

pcsf_annualized_emissions <-
  ggplot(df, aes(x = decile, y = avg_ghgs/1e3)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value/1e3, 
                                     label = sprintf("%.0f", mean_value/1e3)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = ' ',
       subtitle = "(f) Fiber design using PCST algorithm.",
       x = NULL, 
       y = bquote("Annualized GHG emissions (t CO"[2]*" eq. per user)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 19900))


########################
##PANEL USER EMISSIONS##
########################
aggregate_emissions <- ggarrange(
  prims_total_emissions, 
  pcsf_total_emissions, 
  prims_average_emissions,
  pcsf_average_emissions,
  prims_annualized_emissions,
  pcsf_annualized_emissions,
  ncol = 2, nrow = 3, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_emissions.png')
png(path, units="in", width=11, height=12, res=300)
print(aggregate_emissions)
dev.off()

#########################################
##SOCIAL CARBON COST PER USER: PRIM'S ###
#########################################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'ssc_per_user')]

#### Regional emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'ssc_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_scc = mean(ssc_per_user)) 

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
  summarize(mean_value = sum(mean_scc))

prims_per_user_scc <-
  ggplot(df, aes(x = decile, y = mean_scc)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
    label = sprintf("%.0f", mean_value)), size = 3,
    position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Social Carbon Cost (SCC) per User.",
       subtitle = "(a) Fiber design using Prim's algorithm.",
       x = NULL, y = bquote("SCC per user (US$/User)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0,59000))

#######################################
##SOCIAL CARBON COST PER USER: PCST ###
#######################################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'ssc_per_user')]

#### Regional emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'ssc_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_scc = mean(ssc_per_user)) 

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
  summarize(mean_value = sum(mean_scc))

pcsf_per_user_scc <-
  ggplot(df, aes(x = decile, y = mean_scc)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(b) Fiber design using PCST algorithm.",
       x = NULL, y = bquote("SCC per user (US$/User)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 59000))

####################################################
##ANNUALIZED SOCIAL CARBON COST PER USER: PRIM'S ###
####################################################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'ssc_per_user')]

#### Regional emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'ssc_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_scc = ((mean(ssc_per_user)))/30) 

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
  summarize(mean_value = sum(mean_scc))

prims_annualized_per_user_scc <-
  ggplot(df, aes(x = decile, y = mean_scc)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Annualized Social Carbon Cost (SCC) per User.",
       subtitle = "(c) Fiber design using Prim's algorithm.",
       x = NULL, y = bquote("SCC per user (US$/User)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 59000))

##################################################
##ANNUALIZED SOCIAL CARBON COST PER USER: PCST ###
##################################################
#### Access total emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_local_emission_results.csv'))
data2 <- na.omit(data2)
## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'decile', 'ssc_per_user')]

#### Regional emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'fiber_levels', 
                            'SSA_pcsf_regional_emission_results.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'decile', 'ssc_per_user')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

df = data %>%
  group_by(decile, strategy) %>%
  summarize(mean_scc = ((mean(ssc_per_user)))/30) 

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
  summarize(mean_value = sum(mean_scc))

pcsf_annualized_per_user_scc <-
  ggplot(df, aes(x = decile, y = mean_scc)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value, 
                                     label = sprintf("%.0f", mean_value)), size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(d) Fiber design using PCST algorithm.",
       x = NULL, y = bquote("SCC per user (US$/User)")) + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 59000))

##############
##PANEL SCC ##
##############
scc_costs <- ggarrange(
  prims_per_user_scc, 
  pcsf_per_user_scc, 
  prims_annualized_per_user_scc, 
  pcsf_annualized_per_user_scc, 
  ncol = 2, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_scc.png')
png(path, units="in", width=10, height=9, res=300)
print(scc_costs)
dev.off()

############################
##FIBER INFRASTRUCTURE MAP##
############################
africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 
   'Africa_Boundaries', 'SSA_combined_shapefile.shp'))

#################################
##CORE FIBER INFRASTRUCTURE MAP##
#################################
core_nodes <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                                'SSA_core_nodes_existing.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                                'SSA_core_edges_existing.shp'))
core_nodes$Type <- 'Core Nodes'
core_edges$Type <- 'Core Fiber'

core_fiber <- ggplot() +
  geom_sf(data = africa_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = core_nodes, color = "tomato", size = 0.5, aes(fill = Type)) + 
  geom_sf(data = core_edges, color = "green4", linewidth = 0.3) + 
  labs(title = "(e) Existing fiber infrastructure in SSA", 
       subtitle = "Only live fiber lines with core nodes are mapped", 
       fill = NULL) + 
  theme_void() +
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
  ) +   annotation_scale(location = "bl", width_hint = 0.5) + 
  coord_sf(crs = 4326) + 
  ggspatial::annotation_north_arrow(
    location = "tr", which_north = "true",
    pad_x = unit(0.1, "in"), pad_y = unit(0.1, "in"),
    style = ggspatial::north_arrow_nautical(
      fill = c("grey40", "white"),
      line_col = "grey20",
      text_family = "ArcherPro Book"
    )
  ) 


####################################
##PRIM'S FIBER INFRASTRUCTURE MAP ##
####################################
access_nodes <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                                  'SSA_combined_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                                  'SSA_combined_access_edges.shp'))
access_nodes$Type <- 'Access Nodes'
access_edges$Type <- 'Access Fiber'

access_prims_fiber <- ggplot() +
  geom_sf(data = africa_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, color = "gray35", size = 0.002, aes(fill = Type)) + 
  geom_sf(data = access_edges, color = "coral", size = 0.3, linewidth = 0.3) + 
  labs(title = "Fixed fiber network design.", 
       subtitle = "(a) Designed access fiber network using Prim's algorithm.", fill = NULL) + 
  theme(
    axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 12),
    plot.title = element_text(size = 13, face = "bold")
  ) + annotation_scale(location = "bl", width_hint = 0.5) + 
  coord_sf(crs = 4326) + 
  ggspatial::annotation_north_arrow(
    location = "tr", which_north = "true",
    pad_x = unit(0.1, "in"), pad_y = unit(0.1, "in"),
    style = ggspatial::north_arrow_nautical(
      fill = c("grey40", "white"),
      line_col = "grey20",
      text_family = "ArcherPro Book")) 

#################################
##PCST FIBER INFRASTRUCTURE MAP##
#################################
access_nodes <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                                  'SSA_combined_pcsf_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                                  'SSA_combined_pcsf_access_edges.shp'))
access_nodes$Type <- 'Access Nodes'
access_edges$Type <- 'Access Fiber'

access_pcsf_fiber <- ggplot() +
  geom_sf(data = africa_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, color = "darkorange", size = 0.002, aes(fill = Type)) + 
  geom_sf(data = access_edges, color = "aquamarine4", size = 0.3, linewidth = 0.3) + 
  labs(title = " ", 
  subtitle = "(b) Designed access fiber network using PCST algorithm.", fill = NULL) + 
  theme(
    axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 12),
    plot.title = element_text(size = 13, face = "bold")
  ) + annotation_scale(location = "bl", width_hint = 0.5) + 
  coord_sf(crs = 4326) + 
  ggspatial::annotation_north_arrow(
    location = "tr", which_north = "true",
    pad_x = unit(0.1, "in"), pad_y = unit(0.1, "in"),
    style = ggspatial::north_arrow_nautical(
      fill = c("grey40", "white"),
      line_col = "grey20",
      text_family = "ArcherPro Book")) 

#######################
##PANEL FIBER DESIGN ##
#######################
fiber_design <- ggarrange(
  access_prims_fiber, 
  access_pcsf_fiber, 
 legend = 'none',
  ncol = 2)

path = file.path(folder, 'figures', 'fiber_network_design.png')
png(path, units = "in", width = 13, height = 13, res = 300)
print(fiber_design)
dev.off()


###################################
##AVERAGE EMISSIONS PER SUBSCRIBER###
###################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission.csv'))
df = data %>%
  group_by(algorithm, strategy) %>%
  summarize(mean_ghg_user = mean(emissions_kg_per_subscriber)) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing \nCore Network', 'New \nRegional Network', 'New \nAccess Network')
)

df$algorithm <- factor(
  df$algorithm,
  levels = c('none', 'Dijkstras', 'pcsf'),
  labels = c('Unknown', 'Dijkstras', 'PCSF')
)

label_means <- df %>%
  group_by(algorithm) %>%
  summarize(mean_value = sum(mean_ghg_user))

average_emissions <-
  ggplot(df, aes(x = algorithm, y = mean_ghg_user/1e6)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + 
  geom_text(data = label_means, aes(x = algorithm, y = mean_value/1e6, 
  label = sprintf("%.3f", mean_value/1e6)), vjust = -0.5,
  hjust = 0.5, position = position_stack(), size = 2, color = "black") + 
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(B) Average Greenhouse Gas (GHG) Emissions per Subscriber.",
    subtitle = "Classified by network level and regions.",
    x = NULL
  ) +  ylab('GHG Emissions per user (kt CO<sub>2</sub> eq.)') + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 7),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 9, face = "bold"),
    plot.subtitle = element_text(size = 8),
    axis.text.y = element_text(size = 7),
    axis.title.y = element_markdown(size = 7),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    axis.title.x = element_text(size = 7)) + 
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Fiber Hirearchy')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 3.2))


##################################
##TOTAL MANUFACTURING EMISSIONS###
##################################
#################
### DJIKSTRAS ###
#################
#### Access manufacturing emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_total_mfg.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
           'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_mfg_ghg_kg', 'decile')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_regional_total_mfg.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
      'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_mfg_ghg_kg', 'decile')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

data$emission_category = factor(
  data$emission_category,
  levels = c("aluminium_mfg_ghg", "steel_iron_mfg_ghg", "other_metals_mfg_ghg",
    "concrete_mfg_ghg", "optic_fiber_mfg_ghg", "plastics_mfg_ghg"),
  labels = c("Aluminium", "Steel and Iron", "Other Metals", "Concrete",
    "Optic Fiber", "Plastics"))

df = data %>%
  group_by(emission_category, decile) %>%
  summarize(mfg_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(mfg_ghgs))

djikistra_manufacturing_emissions <-
  ggplot(df, aes(x = decile, y = mfg_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e9, 
  label = sprintf("%.2f", total_value/1e9)), size = 3,
  position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(a) Manufacturing phase: Dijkstras.",
    subtitle = "Classified by population deciles and LCA material type.",
    x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
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
  guides(fill = guide_legend(ncol = 6, title = 'LCA Material Type')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 0.58))


############
### PCSF ###
############
#### Access manufacturing emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_pcsf_local_total_mfg.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_mfg_ghg_kg', 'decile')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_pcsf_regional_total_mfg.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_mfg_ghg_kg', 'decile')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

data$emission_category = factor(
  data$emission_category,
  levels = c("aluminium_mfg_ghg", "steel_iron_mfg_ghg", "other_metals_mfg_ghg",
             "concrete_mfg_ghg", "optic_fiber_mfg_ghg", "plastics_mfg_ghg"),
  labels = c("Aluminium", "Steel and Iron", "Other Metals", "Concrete",
             "Optic Fiber", "Plastics"))

df = data %>%
  group_by(emission_category, decile) %>%
  summarize(mfg_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(mfg_ghgs))

pcsf_manufacturing_emissions <-
  ggplot(df, aes(x = decile, y = mfg_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e9, 
    label = sprintf("%.2f", total_value/1e9)), size = 3,
     position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(b) Manufacturing phase: PCSF.",
       subtitle = "Classified by population deciles and LCA material type.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
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
  guides(fill = guide_legend(ncol = 3, title = 'LCA Material Type')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 0.58))


###########################################
###TOTAL END OF LIFE TREATMENT EMISSIONS###
###########################################
#################
### PRIM'S ###
#################
#### Access manufacturing emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_total_eolt.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_eolt_ghg_kg', 'decile')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_regional_total_eolt.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_eolt_ghg_kg', 'decile')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

data$emission_category = factor(
  data$emission_category,
  levels = c("aluminium_eolt_ghg", "steel_iron_eolt_ghg", "other_metals_eolt_ghg",
    "concrete_eolt_ghg", "optic_fiber_eolt_ghg", "plastics_eolt_ghg"),
  labels = c("Aluminium", "Steel and Iron", "Other Metals", "Concrete",
    "Optic Fiber","Plastics"))

df = data %>%
  group_by(emission_category, decile) %>%
  summarize(eolt_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$decile = factor(df$decile,
   levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
   'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
   labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
   'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
   'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
   'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
   'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))


label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(eolt_ghgs))

djikstras_eolts_emissions <-
  ggplot(df, aes(x = decile, y = eolt_ghgs/1e6)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + coord_flip() +
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e6, 
  label = sprintf("%.2f", total_value/1e6)),size = 3,
  position = position_dodge(0.9), vjust = 0.5, hjust = -0.1)  +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(c) End of Life Treatment phase: Dijkstras.",
  subtitle = "Classified by population deciles and LCA material type.", 
  x = NULL,fill = "LCA Material Type", 
  y = bquote("Total GHG Emissions (kt CO"[2]*" eq.)")) + 
  scale_y_continuous(limits = c(0, 8.4), labels = function(y)
  format(y, scientific = FALSE), expand = c(0, 0)) + 
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
    axis.title.x = element_text(size = 10))
    
#################
### PCSF ###
#################
#### Access manufacturing emissions ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_pcsf_local_total_eolt.csv'))

## Combine the merged data with deciles
access_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                                 'SSA_subregional_population_deciles.csv'))
data2 <- merge(data2, access_pop, by = "GID_2")
data2 <- data2[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_eolt_ghg_kg', 'decile')]

#### Regional manufacturing emissions ####
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_pcsf_regional_total_eolt.csv'))

## Combine the merged data with deciles
reg_pop <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                              'SSA_regional_population_deciles.csv'))
data3 <- merge(reg_pop, data3, by = "GID_1")
data3 <- data3[, c('strategy', 'algorithm', 'emission_category', 
                   'lca_phase_ghg_kg', 'total_eolt_ghg_kg', 'decile')]

### Combine baseline, regional and access results
data <- rbind(data2, data3)

data$emission_category = factor(
  data$emission_category,
  levels = c("aluminium_eolt_ghg", "steel_iron_eolt_ghg", "other_metals_eolt_ghg",
             "concrete_eolt_ghg", "optic_fiber_eolt_ghg", "plastics_eolt_ghg"),
  labels = c("Aluminium", "Steel and Iron", "Other Metals", "Concrete",
             "Optic Fiber","Plastics"))

df = data %>%
  group_by(emission_category, decile) %>%
  summarize(eolt_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$decile = factor(df$decile,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
  'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
  'Decile 8 \n(75 - 100 per km²)', 'Decile 7 \n(100 - 200 per km²)', 
  'Decile 6 \n(200 - 300 per km²)', 'Decile 5 \n(300 - 400 per km²)',
  'Decile 4 \n(400 - 500 per km²)', 'Decile 3 \n(500 - 600 per km²)',
  'Decile 2 \n(600 - 700 per km²)', 'Decile 1 \n(>700 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(eolt_ghgs))

pcsf_eolts_emissions <-
  ggplot(df, aes(x = decile, y = eolt_ghgs/1e6)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + coord_flip() +
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e6, 
                                     label = sprintf("%.2f", total_value/1e6)),size = 3,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1)  +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(d) End of Life Treatment phase: PCSF.",
       subtitle = "Classified by population deciles and LCA material type.", 
       x = NULL,fill = "LCA Material Type", 
       y = bquote("Total GHG Emissions (kt CO"[2]*" eq.)")) + 
  scale_y_continuous(limits = c(0, 8.4), labels = function(y)
    format(y, scientific = FALSE), expand = c(0, 0)) + 
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
    axis.title.x = element_text(size = 10))

########################
##PANEL USER EMISSIONS##
########################
mfg_emissions <- ggarrange(
  djikistra_manufacturing_emissions, 
  pcsf_manufacturing_emissions, 
  djikstras_eolts_emissions, 
  pcsf_eolts_emissions, 
  ncol = 2, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'user_emissions_category.png')
png(path, units="in", width=10, height=9, res=300)
print(mfg_emissions)
dev.off()


