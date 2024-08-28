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

df$strategy <- factor(df$strategy, levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(total_ghgs))

prims_total_emissions <- ggplot(df,  aes(x = decile, y = total_ghgs/1e9, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = 
  formatC(signif(after_stat(y), 3), digits = 3, format = "fg", flag = "#")),
  size = 2.5, position = position_dodge(0.9), vjust = -0.3, hjust = 0.5) + 
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Total GHG Emissions.",
       subtitle = "(a) Fiber design using Prim's algorithm.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  )+ expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 7500))

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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
    'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
    'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
    'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
    'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
    'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
    'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
    'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(total_ghgs))

pcst_total_emissions <-
  ggplot(df,  aes(x = decile, y = total_ghgs/1e9, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5)  +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = ' ',
       subtitle = "(b) Fiber design using PCST algorithm.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 7500))

total_emissions <- ggarrange(
  prims_total_emissions, 
  pcst_total_emissions, 
  ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
   'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
   'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 'Decile 9 \n(50 - 75 per km²)', 
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

prims_average_emissions <- ggplot(df,  aes(x = decile, y = avg_ghgs/1e3, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5)  +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Average GHG Emissions",
       subtitle = "(a) Fiber design using Prim's algorithm.",
       x = NULL, 
       y = bquote("Average emissions \n(t CO'[2]*' eq. per user)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 350))

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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
   'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
   'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
   'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
   'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
   'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
   'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
   'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(avg_ghgs))

pcst_average_emissions <- ggplot(df,  aes(x = decile, y = avg_ghgs/1e3, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = ' ',
       subtitle = "(b) Fiber design using PCST algorithm.",
       x = NULL, 
       y = bquote("Average emissions \n(t CO'[2]*' eq. per user)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 2000))

average_emissions <- ggarrange(prims_average_emissions, pcst_average_emissions, 
  ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='none') 


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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
    'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
    'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
    'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
    'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
    'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
    'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
    'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(avg_ghgs))

prims_annualized_emissions <- ggplot(df,  aes(x = decile, y = avg_ghgs/1e3, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Annualized GHG Emissions",
       subtitle = "(e) Fiber design using Prim's algorithm.",
       x = NULL, 
       y = bquote("Annualized Emissions \n(t CO'[2]*' eq. per user)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 13))


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
  summarize(avg_ghgs = mean(emissions_kg_per_subscriber/30)) 

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
    'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
    'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
    'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
    'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
    'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
    'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
    'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = mean(avg_ghgs))

pcst_annualized_emissions <- ggplot(df,  aes(x = decile, y = avg_ghgs/1e3, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = ' ',
       subtitle = "(f) Fiber design using PCST algorithm.",
       x = NULL, 
       y = bquote("Annualized emissions \n(t CO'[2]*' eq. per user)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 65))

annualized_emissions <- ggarrange(prims_annualized_emissions, 
    pcst_annualized_emissions, ncol = 1, nrow = 2, align = c('hv'), 
    common.legend = TRUE, legend='bottom') 

########################
##PANEL USER EMISSIONS##
########################
aggregate_emissions <- ggarrange(average_emissions, 
  annualized_emissions, ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_emissions.png')
png(path, units="in", width=11, height=14, res=300)
print(aggregate_emissions)
dev.off()

#####################################
##ANNUALIZED TCO PER USER: PRIM'S ###
#####################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_local_tco_results.csv'))
data2 <- na.omit(data2)

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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
    'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
    'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
    'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
    'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
    'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
    'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
    'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

prims_annualized_tco <- ggplot(df,  aes(x = decile, y = mean_tco, 
   fill = strategy)) + geom_bar(stat = 'identity', position = 
   position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
   digits = 3, format = "fg", flag = "#")), size = 3, position = 
   position_dodge(0.9), vjust = -0.3, hjust = 0.5) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Annualized TCO per user.",
       subtitle = "(a) Fiber design using Prim's algorithm.",
       x = NULL, y = bquote("Annualized \nTCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 2500))

##################################
##ANNUALIZED TCO PER USER: PCST###
##################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_local_tco_results.csv'))
data2 <- na.omit(data2)

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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
   'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
   'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
   'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
   'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
   'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
   'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
   'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

pcsf_annualized_tco <- ggplot(df,  aes(x = decile, y = mean_tco, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(b) Fiber design using PCST algorithm.",
       x = NULL, y = bquote("Annualized \nTCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 2500))

average_tco <- ggarrange(prims_annualized_tco, pcsf_annualized_tco, 
    ncol = 1, nrow = 2, align = c('hv'), common.legend = TRUE, legend='none') 

#######################################
##MEAN MONTHLY TCO PER USER: PRIM'S ###
#######################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_local_tco_results.csv'))
data2 <- na.omit(data2)
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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
    'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
    'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
    'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
    'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
    'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
    'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
    'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

prims_monthly_tco <- ggplot(df,  aes(x = decile, y = mean_tco, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
    position_dodge(0.9), vjust = -0.3, hjust = 0.5)  +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "Mean Monthly TCO per user.",
       subtitle = "(c) Fiber design using Prim's algorithm.",
       x = NULL, y = bquote("Mean Monthly \nTCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 130))

#####################################
##MEAN MONTHLY TCO PER USER: PCST ###
#####################################
#### Access TCO per user ####
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_pcsf_local_tco_results.csv'))
data2 <- na.omit(data2)

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

df$decile = factor(df$decile, levels = c('decile 10', 'decile 9', 'decile 8', 
    'decile 7', 'decile 6', 'decile 5', 'decile 4', 'decile 3', 'decile 2', 
    'decile 1'), labels = c('Decile 10 \n(<50 per km²)', 
    'Decile 9 \n(50 - 75 per km²)', 'Decile 8 \n(75 - 100 per km²)', 
    'Decile 7 \n(100 - 200 per km²)', 'Decile 6 \n(200 - 300 per km²)', 
    'Decile 5 \n(300 - 400 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
    'Decile 3 \n(500 - 600 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
    'Decile 1 \n(>700 per km²)'))

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'access'),
  labels = c('Existing Core Network', 'New Regional Network', 
             'New Access Network'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(mean_tco))

pcsf_monthly_tco <- ggplot(df,  aes(x = decile, y = mean_tco, 
  fill = strategy)) + geom_bar(stat = 'identity', position = 
  position_dodge(0.9)) + geom_text(aes(label = formatC(signif(after_stat(y), 3), 
  digits = 3, format = "fg", flag = "#")), size = 3, position = 
  position_dodge(0.9), vjust = -0.3, hjust = 0.5)  +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = " ",
       subtitle = "(d) Fiber design using PCST algorithm.",
       x = NULL, y = bquote("Mean Monthly \nTCO per user (US$/User)")) + 
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 10, angle = 15),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 15, face = "bold"),
    plot.subtitle = element_text(size = 13),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 9),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 200))

monthly_tco <- ggarrange(prims_monthly_tco, pcsf_monthly_tco, 
    ncol = 1, nrow = 2, align = c('hv'), common.legend = TRUE, legend='none')

###################
##PANEL USER TCO ##
###################
aggregate_tco <- ggarrange(average_tco, monthly_tco, 
     ncol = 1, nrow = 2, align = c('hv'),
     common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_TCO.png')
png(path, units="in", width=11, height=14, res=300)
print(aggregate_tco)
dev.off()

