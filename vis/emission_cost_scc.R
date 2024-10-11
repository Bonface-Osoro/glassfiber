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
#######################
##TOTAL POPULATION ####
#######################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_subregional_population_deciles.csv'))
df = data %>%
  distinct(decile, population, .keep_all = TRUE) %>%
  group_by(decile) %>%
  summarize(total_pops = round(sum(population)/1e6))

df$decile = factor(df$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
   'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
   'Decile 10'), labels = c('Decile 1 \n(>958 per km²)', 
   'Decile 2 \n(456 - 957 per km²)', 'Decile 3 \n(273 - 455 per km²)', 
   'Decile 4 \n(172 - 272 per km²)', 'Decile 5 \n(107 - 171 per km²)', 
   'Decile 6 \n(64 - 106 per km²)', 'Decile 7 \n(40 - 63 per km²)', 
   'Decile 8 \n(22 - 39 per km²)', 'Decile 9 \n(10 - 21 per km²)', 
   'Decile 10 \n(<9 per km²)'))

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

#################
##TOTAL AREA ####
#################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_subregional_population_deciles.csv'))
df = data %>%
  distinct(decile, area, .keep_all = TRUE) %>%
  group_by(decile) %>%
  summarize(total_area = round(sum(area)))

df$decile = factor(df$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
   'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
   'Decile 10'), labels = c('Decile 1 \n(>958 per km²)', 
   'Decile 2 \n(456 - 957 per km²)', 'Decile 3 \n(273 - 455 per km²)', 
   'Decile 4 \n(172 - 272 per km²)', 'Decile 5 \n(107 - 171 per km²)', 
   'Decile 6 \n(64 - 106 per km²)', 'Decile 7 \n(40 - 63 per km²)', 
   'Decile 8 \n(22 - 39 per km²)', 'Decile 9 \n(10 - 21 per km²)', 
   'Decile 10 \n(<9 per km²)'))

total_area <- 
  ggplot(df, aes(x = decile, y = total_area, fill = decile)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) + coord_flip() +
  geom_text(aes(label = as.character(signif(total_area, 3))), size = 2.5, 
            position = position_dodge(0.9), vjust = 0.05, hjust = -0.1) +
  labs(colour = NULL, title = '(b) Area decile classification of SSA.',
       subtitle = 'Based on population geotypes.',
       x = NULL, y = "Area (km²)") + 
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
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 11000000))


########################################
###### AVERAGE PER USER EMISSIONS ######
########################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_fiber_emission_results.csv'))

data$decile = factor(data$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
   'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
   'Decile 10'), labels = c('Decile 1 \n(>958 per km²)', 
   'Decile 2 \n(456 - 957 per km²)', 'Decile 3 \n(273 - 455 per km²)', 
   'Decile 4 \n(172 - 272 per km²)', 'Decile 5 \n(107 - 171 per km²)', 
   'Decile 6 \n(64 - 106 per km²)', 'Decile 7 \n(40 - 63 per km²)', 
   'Decile 8 \n(22 - 39 per km²)', 'Decile 9 \n(10 - 21 per km²)', 
   'Decile 10 \n(<9 per km²)'))

data$strategy <- factor(data$strategy,
                      levels = c('regional', 'access'),
                      labels = c('New Regional Network', 'New Access Network'))

data$algorithm <- factor(data$algorithm,
                       levels = c('prims', 'pcsf'),
                       labels = c("Minimum Spanning Tree (Prim's algorithm)", 
                                  'Prize Collecting Steiner Tree (PCST)'))

df <- data %>% select(user_emissions_kg_per_user, strategy, decile, algorithm)

df = df %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(user_emissions_kg_per_user),
            sd = sd(user_emissions_kg_per_user))

label_totals <- df %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

per_user_emissions <- ggplot(df, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .2,
                position = position_dodge(.9), color = 'black',size = 0.2) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 2), 
       digits = 2, format = "fg", flag = "#")), color = 'black', size = 3.5, position = 
       position_dodge(0.9), vjust = -0.1, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = "Fiber Broadband Greenhouse Gas (GHG) Emissions", 
       subtitle = "(a) Per user emissions categorized by deciles and grouped by network level and spatial optimization algorithm.", 
       x = NULL, y = bquote("Average emissions (kg CO"["2"] ~ " eq. per user)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11, angle = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  facet_wrap( ~ algorithm, nrow = 2) + theme(strip.text = element_text(size = 14)) 

###########################################
###### ANNUALIZED PER USER EMISSIONS ######
###########################################
df1 <- data %>% select(annualized_per_user_emissions, strategy, decile, algorithm)

df1 = df1 %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(annualized_per_user_emissions),
            sd = sd(annualized_per_user_emissions))

label_totals <- df1 %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

annualized_per_user_emissions <- ggplot(df1, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .2,
                position = position_dodge(.9), color = 'black',size = 0.2) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
     digits = 2, format = "fg", flag = "#")), color = 'black', size = 3.5, position = 
     position_dodge(0.9), vjust = -0.1, hjust = 1.1) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = " ", 
       subtitle = "(b) Annualized per user emissions grouped by network level and spatial optimization algorithm.", 
       x = NULL, y = bquote("Annualized per user emissions (kg CO"["2"] ~ " eq. per user)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11, angle = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 11)) +
  facet_wrap( ~ algorithm, nrow = 2) + theme(strip.text = element_text(size = 14)) 

########################
##PANEL USER EMISSIONS##
########################
aggregate_emissions <- ggarrange(per_user_emissions, 
  annualized_per_user_emissions, ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_emissions.png')
png(path, units="in", width=14, height=14, res=300)
print(aggregate_emissions)
dev.off()

###################################################
###### PER USER SOCIAL CARBON COST EMISSIONS ######
###################################################
df2 <- data %>% select(per_user_scc_usd, strategy, decile, algorithm)

df2 = df2 %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(per_user_scc_usd),
            sd = sd(per_user_scc_usd))

label_totals <- df2 %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

per_user_scc_costs <- ggplot(df2, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .2,
                position = position_dodge(.9), color = 'black',size = 0.2) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 2), 
     digits = 2, format = "fg", flag = "#")), color = 'black', size = 3.5, position = 
     position_dodge(0.9), vjust = -0.1, hjust = 1.1) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = "Fiber Broadband Social Carbon Cost (SCC)", 
       subtitle = "(a) Per user SCC grouped by network level and spatial optimization algorithm.", 
       x = NULL, y = bquote("Average SCC per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11, angle = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_y_continuous(expand = c(0, 0),
    labels = function(y)format(y, scientific = FALSE), limit = c(0, 24)) +
  facet_wrap( ~ algorithm, nrow = 2) + theme(strip.text = element_text(size = 14)) 

##############################################################
###### ANNUALIZED PER USER SOCIAL CARBON COST EMISSIONS ######
##############################################################
df3 <- data %>% select(per_user_annualized_scc_usd, strategy, decile, algorithm)

df3 = df3 %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(per_user_annualized_scc_usd),
            sd = sd(per_user_annualized_scc_usd))

label_totals <- df3 %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

anualized_per_user_scc_costs <- ggplot(df3, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .2,
                position = position_dodge(.9), color = 'black',size = 0.2) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
     digits = 2, format = "fg", flag = "#")), color = 'black', size = 3.5, position = 
     position_dodge(0.9), vjust = -0.1, hjust = 1.1) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = " ", 
       subtitle = "(b) Annualized per user SCC grouped by network level and spatial optimization algorithm.", 
       x = NULL, y = bquote("Annualized average SCC per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11, angle = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_y_continuous(expand = c(0, 0),
     labels = function(y)format(y, scientific = FALSE), limit = c(0, 0.84)) +
  facet_wrap( ~ algorithm, nrow = 2) + theme(strip.text = element_text(size = 14)) 

##############
##PANEL SCC ##
##############
aggregate_SCC <- ggarrange(
  per_user_scc_costs, anualized_per_user_scc_costs, ncol = 1, nrow = 2, 
  align = c('hv'), common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_SCC.png')
png(path, units="in", width=14, height=14, res=300)
print(aggregate_SCC)
dev.off()

##############################################
## FIBER BROADBAND TOTAL COST OF OWNERSHIP ###
##############################################
data1 <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                           'SSA_fiber_cost_results.csv'))

data1$decile = factor(data1$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
   'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
   'Decile 10'), labels = c('Decile 1 \n(>958 per km²)', 
   'Decile 2 \n(456 - 957 per km²)', 'Decile 3 \n(273 - 455 per km²)', 
   'Decile 4 \n(172 - 272 per km²)', 'Decile 5 \n(107 - 171 per km²)', 
   'Decile 6 \n(64 - 106 per km²)', 'Decile 7 \n(40 - 63 per km²)', 
   'Decile 8 \n(22 - 39 per km²)', 'Decile 9 \n(10 - 21 per km²)', 
   'Decile 10 \n(<9 per km²)'))

data1$strategy <- factor(data1$strategy,
    levels = c('regional', 'access'),
    labels = c('New Regional Network', 'New Access Network'))

data1$algorithm <- factor(data1$algorithm,
    levels = c('prims', 'pcsf'),
    labels = c("Minimum Spanning Tree (Prim's algorithm)", 
    'Prize Collecting Steiner Tree (PCST)'))

###################
## TCO PER USER ###
###################
df4 <- data1 %>% select(per_user_annualized_usd, strategy, decile, algorithm)

df4 = df4 %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(per_user_annualized_usd),
            sd = sd(per_user_annualized_usd))

label_totals <- df4 %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

annualized_per_user_tco <- ggplot(df4, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .2,
                position = position_dodge(.9), color = 'black',size = 0.2) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 2), 
     digits = 2, format = "fg", flag = "#")), color = 'black', size = 3.5, position = 
     position_dodge(0.9), vjust = -0.1, hjust = 1.1) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = "Fiber Broadband Total Cost of Ownership (TCO)", 
       subtitle = "(a) Annualized average TCO per user grouped by network level and spatial optimization algorithm.", 
       x = NULL, y = bquote("Annualized average TCO per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11, angle = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_y_continuous(expand = c(0, 0),
     labels = function(y)format(y, scientific = FALSE), limit = c(0, 38)) +
  facet_wrap( ~ algorithm, nrow = 2) + theme(strip.text = element_text(size = 14)) 

###########################
## MONTHLY TCO PER USER ###
###########################
df5 <- data1 %>% select(per_monthly_tco_usd, strategy, decile, algorithm)

df5 = df5 %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(per_monthly_tco_usd),
            sd = sd(per_monthly_tco_usd))

label_totals <- df5 %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

monthly_per_user_tco <- ggplot(df5, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .2,
                position = position_dodge(.9), color = 'black',size = 0.2) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 2), 
     digits = 2, format = "fg", flag = "#")), color = 'black', size = 3.5, position = 
      position_dodge(0.9), vjust = -0.1, hjust = 1.1) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = " ", 
       subtitle = "(b) Monthly TCO per user grouped by network level and spatial optimization algorithm.", 
       x = NULL, y = bquote("Monthly TCO per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11, angle = 5),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 10)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Network level')) +
  scale_y_continuous(expand = c(0, 0),
     labels = function(y)format(y, scientific = FALSE), limit = c(0, 3.4)) +
  facet_wrap( ~ algorithm, nrow = 2) + theme(strip.text = element_text(size = 14)) 

###################
##PANEL USER TCO ##
###################
aggregate_tco <- ggarrange(annualized_per_user_tco, monthly_per_user_tco, 
     ncol = 1, nrow = 2, align = c('hv'),
     common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'aggregate_TCO.png')
png(path, units="in", width=14, height=14, res=300)
print(aggregate_tco)
dev.off()


