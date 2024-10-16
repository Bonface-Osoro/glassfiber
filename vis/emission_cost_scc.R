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

########################################
###### AVERAGE PER USER EMISSIONS ######
########################################
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
                            'SSA_fiber_emission_results.csv'))

data$decile = factor(data$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
   'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
   'Decile 10'), labels = c('Decile 1 \n(>958 km²)', 
   'Decile 2 \n(<957 km²)', 'Decile 3 \n(<455 km²)', 
   'Decile 4 \n(<272 km²)', 'Decile 5 \n(<171 km²)', 
   'Decile 6 \n(<106 km²)', 'Decile 7 \n(<63 km²)', 
   'Decile 8 \n(<39 km²)', 'Decile 9 \n(<21 km²)', 
   'Decile 10 \n(<9 km²)'))

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

per_user_emissions <- 
  ggplot(df, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .1,
                position = position_dodge(.9), color = 'red',size = 0.5) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 2), 
       digits = 2, format = "fg", flag = "#")), color = 'black', size = 3, position = 
       position_dodge(0.9), vjust = -0.2, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, title = "(A) Fiber Broadband Greenhouse Gas (GHG) Emissions Reported Per User", 
       subtitle = "Per user emissions categorized by deciles, grouped by network level and spatial optimization algorithm.", 
       x = "Population Density Decile (Population per km²)", 
       y = bquote("Average emissions (kg CO"["2"] ~ " eq. per user)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 12)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 3, title = 'Network level')) +
  facet_wrap( ~ algorithm, nrow = 2) + 
    theme(strip.text = element_text(size = 14)) 
  

###########################################
###### ANNUALIZED PER USER EMISSIONS ######
###########################################
df1 <- data %>% 
  select(annualized_per_user_emissions, strategy, decile, algorithm)

data$decile = factor(data$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
   'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
   'Decile 10'), labels = c('Decile 1 \n(>958 km²)', 
   'Decile 2 \n(<957 km²)', 'Decile 3 \n(<455 km²)', 
   'Decile 4 \n(<272 km²)', 'Decile 5 \n(<171 km²)', 
   'Decile 6 \n(<106 km²)', 'Decile 7 \n(<63 km²)', 
   'Decile 8 \n(<39 km²)', 'Decile 9 \n(<21 km²)', 
   'Decile 10 \n(<9 km²)'))
df1 = df1 %>%
  group_by(strategy, decile, algorithm) %>%
  summarize(mean = mean(annualized_per_user_emissions),
            sd = sd(annualized_per_user_emissions))

label_totals <- df1 %>%
  group_by(decile, strategy) %>%
  summarize(mean_value = sum(mean))

annualized_per_user_emissions <- 
  ggplot(df1, aes(x = decile, y = mean, fill = strategy)) +
  geom_bar(stat = "identity", position = position_dodge(), width = 0.9) +
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .1,
                position = position_dodge(.9), color = 'red',size = 0.5) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
     digits = 2, format = "fg", flag = "#")), color = 'black', size = 3, position = 
     position_dodge(0.9), vjust = -0.2, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") + 
  labs(colour = NULL, 
       title = "(B) Fiber Broadband Greenhouse Gas (GHG) Emissions Per User", 
       subtitle = "Annualized per user emissions grouped by network level and spatial optimization algorithm.", 
       x = "Population Density Decile (Population per km²)", 
       y = bquote("Annualized per user emissions (kg CO"["2"] ~ " eq. per user)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 11)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 3, title = 'Network level')) +
  scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 11)) +
  facet_wrap( ~ algorithm, nrow = 2) + 
  theme(strip.text = element_text(size = 14)) 

########################
##PANEL USER EMISSIONS##
########################
aggregate_emissions <- ggarrange(per_user_emissions, 
  annualized_per_user_emissions, ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'aggregate_emissions.png')
png(path, units="in", width=12, height=14, res=300)
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
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .1,
                position = position_dodge(.9), color = 'red',size = 0.5) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
                                digits = 2, format = "fg", flag = "#")), color = 'black', size = 3, position = 
              position_dodge(0.9), vjust = -0.2, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(A) Fiber Broadband Social Carbon Cost (SCC) Reported Per User",
       subtitle = "Per user SCC categorized by deciles, grouped by network level and spatial optimization algorithm.",
       x = "Population Density Decile (Population per km²)", 
       y = bquote("Average SCC per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 11)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 3, title = 'Network level')) +
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
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .1,
                position = position_dodge(.9), color = 'red',size = 0.5) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
       digits = 2, format = "fg", flag = "#")), color = 'black', size = 3, position = 
              position_dodge(0.9), vjust = -0.2, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(B) Fiber Broadband Social Carbon Cost (SCC) Reported Per User",
       subtitle = "Annualized per user SCC categorized by deciles, grouped by network level and spatial optimization algorithm.",
       x = "Population Density Decile (Population per km²)", 
       y = bquote("Annualized average SCC per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 11)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 3, title = 'Network level')) +
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
png(path, units="in", width=12, height=14, res=300)
print(aggregate_SCC)
dev.off()

##############################################
## FIBER BROADBAND TOTAL COST OF OWNERSHIP ###
##############################################
data1 <- read.csv(file.path(folder, '..', 'results', 'SSA',
                           'SSA_fiber_cost_results.csv'))

data1$decile = factor(data1$decile, levels = c('Decile 1', 'Decile 2', 'Decile 3', 
     'Decile 4', 'Decile 5', 'Decile 6', 'Decile 7', 'Decile 8', 'Decile 9', 
     'Decile 10'), labels = c('Decile 1 \n(>958 km²)', 
     'Decile 2 \n(<957 km²)', 'Decile 3 \n(<455 km²)', 
     'Decile 4 \n(<272 km²)', 'Decile 5 \n(<171 km²)', 
     'Decile 6 \n(<106 km²)', 'Decile 7 \n(<63 km²)', 
     'Decile 8 \n(<39 km²)', 'Decile 9 \n(<21 km²)', 
     'Decile 10 \n(<9 km²)'))

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
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .1,
                position = position_dodge(.9), color = 'red',size = 0.5) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
      digits = 2, format = "fg", flag = "#")), color = 'black', size = 3, position = 
              position_dodge(0.9), vjust = -0.2, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(A) Fiber Broadband Total Cost of Ownership (TCO) Reported Per User",
       subtitle = "Annualized average TCO per user categorized by deciles, grouped by network level and spatial optimization algorithm.",
       x = "Population Density Decile (Population per km²)", 
       y = bquote("Annualized average TCO per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 11)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 3, title = 'Network level')) +
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
  geom_errorbar(aes(ymin = mean - sd, ymax = mean + sd), width = .1,
                position = position_dodge(.9), color = 'red',size = 0.5) + 
  geom_text(aes(label = formatC(signif(after_stat(y), 1), 
       digits = 2, format = "fg", flag = "#")), color = 'black', size = 3, position = 
              position_dodge(0.9), vjust = -0.2, hjust = 1.2) +
  scale_fill_brewer(palette = "Dark2") +
  labs(colour = NULL, title = "(B) Fiber Broadband Total Cost of Ownership (TCO) Reported Per User",
       subtitle = "Monthly TCO per user categorized by deciles, grouped by network level and spatial optimization algorithm.",
       x = "Population Density Decile (Population per km²)", 
       y = bquote("Monthly TCO per user ($US/User)")) +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 11),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 14),
    axis.text.y = element_text(size = 10),
    axis.title.y = element_text(size = 12),
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 12),
    axis.title.x = element_text(size = 11)
  ) + expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 3, title = 'Network level')) +
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
png(path, units="in", width=12, height=14, res=300)
print(aggregate_tco)
dev.off()


