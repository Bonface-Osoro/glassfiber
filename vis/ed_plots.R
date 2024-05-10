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

###############################
##TOTAL EMISSIONS: DIJKSTRAS###
###############################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
df <- read.csv(file.path(folder, '..', 'results', 'SSA', 'sample',
                         'djikstras_total_emission.csv'))
df <- df[df$decile != "National", ]

df$decile = factor(df$decile,
  levels = c('National', 'Decile 10 \n(>700 per km²)', 'Decile 9 \n(600 - 700 per km²)', 
  'Decile 8 \n(500 - 600 per km²)', 'Decile 7 \n(400 - 500 per km²)', 
  'Decile 6 \n(300 - 400 per km²)', 'Decile 5 \n(200 - 300 per km²)',
  'Decile 4 \n(100 - 200 per km²)', 'Decile 3 \n(75 - 100 per km²)',
  'Decile 2 \n(50 - 75 per km²)', 'Decile 1 \n(<50 per km²)'),
  labels = c('National', 'Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
  'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
  'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
  'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
  'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(total_ghgs))

djikistra_total_emissions <-
  ggplot(df, aes(x = decile, y = total_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e9, 
                                     label = sprintf("%.0f", total_value/1e9)), size = 2,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(A) Total GHG Emissions: Dijkstras.",
       subtitle = "Classified by population deciles and network level.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
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
    axis.title.x = element_text(size = 7)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 32900))

##########################
##TOTAL EMISSIONS: PCSF###
##########################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
df <- read.csv(file.path(folder, '..', 'results', 'SSA', 'sample',
                         'pcsf_total_emission.csv'))
df <- df[df$decile != "National", ]

df$decile = factor(df$decile,
  levels = c('National', 'Decile 10 \n(>700 per km²)', 'Decile 9 \n(600 - 700 per km²)', 
  'Decile 8 \n(500 - 600 per km²)', 'Decile 7 \n(400 - 500 per km²)', 
  'Decile 6 \n(300 - 400 per km²)', 'Decile 5 \n(200 - 300 per km²)',
  'Decile 4 \n(100 - 200 per km²)', 'Decile 3 \n(75 - 100 per km²)',
  'Decile 2 \n(50 - 75 per km²)', 'Decile 1 \n(<50 per km²)'),
  labels = c('National', 'Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
  'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
  'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
  'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
  'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(total_value = sum(total_ghgs))

pcsf_total_emissions <-
  ggplot(df, aes(x = decile, y = total_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = total_value/1e9, 
                                     label = sprintf("%.0f", total_value/1e9)), size = 2,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(B) Total GHG Emissions: PCSF.",
       subtitle = "Classified by population deciles and network level.",
       x = NULL, y = bquote("Total GHG Emissions (Mt CO"[2]*" eq.)")) + 
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
    axis.title.x = element_text(size = 7)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
                                                             labels = function(y)format(y, scientific = FALSE), limit = c(0, 32900))

#################################
##AVERAGE EMISSIONS: DIJKSTRAS###
#################################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
df <- read.csv(file.path(folder, '..', 'results', 'SSA', 'sample',
                         'dijkstras_average_emission.csv'))
df <- df[df$decile != "National", ]

df$decile = factor(df$decile,
   levels = c('National', 'Decile 10 \n(>700 per km²)', 'Decile 9 \n(600 - 700 per km²)', 
   'Decile 8 \n(500 - 600 per km²)', 'Decile 7 \n(400 - 500 per km²)', 
   'Decile 6 \n(300 - 400 per km²)', 'Decile 5 \n(200 - 300 per km²)',
   'Decile 4 \n(100 - 200 per km²)', 'Decile 3 \n(75 - 100 per km²)',
   'Decile 2 \n(50 - 75 per km²)', 'Decile 1 \n(<50 per km²)'),
   labels = c('National', 'Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
   'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
   'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
   'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
   'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(avg_ghgs))

djikistra_average_emissions <-
  ggplot(df, aes(x = decile, y = avg_ghgs/1e3)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value/1e3, 
                                     label = sprintf("%.0f", mean_value/1e3)), size = 2,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(C) Average GHG Emissions: Dijkstras.",
       subtitle = "Classified by population deciles and network level.",
       x = NULL, 
       y = bquote("Average emissions per GHG emissions (t CO"[2]*" eq. per user)")) + 
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
    axis.title.x = element_text(size = 7)) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 6100))

############################
##AVERAGE EMISSIONS: PCSF###
############################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
df <- read.csv(file.path(folder, '..', 'results', 'SSA', 'sample',
                         'pcsf_average_emission.csv'))
df <- df[df$decile != "National", ]

df$decile = factor(df$decile,
  levels = c('National', 'Decile 10 \n(>700 per km²)', 'Decile 9 \n(600 - 700 per km²)', 
  'Decile 8 \n(500 - 600 per km²)', 'Decile 7 \n(400 - 500 per km²)', 
  'Decile 6 \n(300 - 400 per km²)', 'Decile 5 \n(200 - 300 per km²)',
  'Decile 4 \n(100 - 200 per km²)', 'Decile 3 \n(75 - 100 per km²)',
  'Decile 2 \n(50 - 75 per km²)', 'Decile 1 \n(<50 per km²)'),
  labels = c('National', 'Decile 1 \n(>700 per km²)', 'Decile 2 \n(600 - 700 per km²)', 
  'Decile 3 \n(500 - 600 per km²)', 'Decile 4 \n(400 - 500 per km²)', 
  'Decile 5 \n(300 - 400 per km²)', 'Decile 6 \n(200 - 300 per km²)',
  'Decile 7 \n(100 - 200 per km²)', 'Decile 8 \n(75 - 100 per km²)',
  'Decile 9 \n(50 - 75 per km²)', 'Decile 10 \n(<50 per km²)'))

label_totals <- df %>%
  group_by(decile) %>%
  summarize(mean_value = sum(avg_ghgs))

pcsf_average_emissions <-
  ggplot(df, aes(x = decile, y = avg_ghgs/1e3)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + coord_flip() + 
  geom_text(data = label_totals, aes(x = decile, y = mean_value/1e3, 
                                     label = sprintf("%.0f", mean_value/1e3)), size = 2,
            position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(D) Average GHG Emissions: PCSF.",
       subtitle = "Classified by population deciles and network level.",
       x = NULL, 
       y = bquote("Average emissions per GHG emissions (t CO"[2]*" eq. per user)")) + 
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
    axis.title.x = element_text(size = 7)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 6100))

########################
##PANEL USER EMISSIONS##
########################
aggregate_emissions <- ggarrange(
  djikistra_total_emissions, 
  pcsf_total_emissions, 
  djikistra_average_emissions,
  pcsf_average_emissions,
  ncol = 2, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'ED_aggregate_emissions.png')
png(path, units="in", width=10, height=9, res=300)
print(aggregate_emissions)
dev.off()