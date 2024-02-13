library(ggpubr)
library(ggplot2)
library(dplyr)
library(tidyverse)
library("readxl")
library(ggtext)

# Set default folder
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
###############################
##AVERAGE EMISSIONS PER USER###
###############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission_subscriber_average.csv')) #%>%
  #filter(geotype != 'remote')

df = data %>%
  group_by(geotype, adoption_scenario, region) %>%
  summarize(mean_emissions = mean(emissions_kg_per_subscriber)/1e3)

df$adoption_scenario = factor(
  df$adoption_scenario,
  levels = c('low', 'baseline', 'high'),
  labels = c('Low', 'Baseline', 'High')
)

df$geotype = factor(
  df$geotype,
  levels = c('remote', 'rural', 'suburban', 'urban'),
  labels = c('Remote', 'Rural', 'Suburban', 'Urban')
)

average_emissions_per_subscriber <- 
  ggplot(df, aes(x = geotype, y = mean_emissions, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(mean_emissions, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  scale_fill_brewer(palette = "YlGnBu") +
  labs(
    colour = NULL,
    title = "(A) Average Emissions per User",
    subtitle = "Classified by geotype, LCA material type and regions",
    x = NULL,
    fill = "Demand Scenario"
  ) + ylab('Average GHG Emissions <br>per User (t CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 6303000),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + scale_x_discrete(limits = rev) +
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
  ) + facet_wrap( ~ region, ncol = 4)

#############################
##TOTAL EMISSION PER AREA ####
#############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission_subscriber_total.csv')) %>%
  filter(geotype != 'remote')

df = data %>%
  group_by(geotype, adoption_scenario, region) %>%
  summarize(total_emissions = sum(emissions_kg_per_subscriber)/1e6)

df$adoption_scenario = factor(
  df$adoption_scenario,
  levels = c('low', 'baseline', 'high'),
  labels = c('Low', 'Baseline', 'High')
)

df$geotype = factor(
  df$geotype,
  levels = c('remote', 'rural', 'suburban', 'urban'),
  labels = c('Remote', 'Rural', 'Suburban', 'Urban')
)

region_total_emissions <- 
  ggplot(df, aes(x = geotype, y = total_emissions, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total_emissions, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) + scale_fill_brewer(palette = "YlGnBu") +
  labs(
    colour = NULL,
    title = '(B) Total Emissions per User',
    subtitle = 'Classified by geotype, demand scenario and region.',
    x = NULL
  ) + ylab('Total GHG Emissions <br>per User (kt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 22000),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + scale_x_discrete(limits = rev) +
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
  ) + facet_wrap( ~ region, ncol = 4)


##################################
##TOTAL MANUFACTURING EMISSIONS###
##################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_total_mfg.csv'))
data$emission_category = factor(
  data$emission_category,
  levels = c(
    "aluminium_mfg_ghg",
    "steel_iron_mfg_ghg",
    "other_metals_mfg_ghg",
    "concrete_mfg_ghg",
    "optic_fiber_mfg_ghg",
    "plastics_mfg_ghg"
  ),
  labels = c(
    "Aluminium",
    "Steel and Iron",
    "Other Metals",
    "Concrete",
    "Optic Fiber",
    "Plastics"
  )
)

df = data %>%
  group_by(emission_category, geotype, region) %>%
  summarize(mfg_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$geotype = factor(
  df$geotype,
  levels = c('remote', 'rural', 'suburban', 'urban'),
  labels = c('Remote', 'Rural', 'Suburban', 'Urban')
)

totals <- df %>%
  group_by(geotype, emission_category, region) %>%
  summarize(value = signif(sum(mfg_ghgs)))

label_totals <- df %>%
  group_by(geotype, region) %>%
  summarize(total_value = sum(mfg_ghgs))

manufacturing_emissions <-
  ggplot(df, aes(x = geotype, y = mfg_ghgs/1e6)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + 
  geom_text(data = label_totals, aes(x = geotype, y = total_value/1e6, 
    label = sprintf("%.2f", total_value/1e6)),
    vjust = -0.5,
    hjust = 0.5,
    position = position_stack(), 
    size = 2, color = "black") +
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(A) Manufacturing Phase",
    subtitle = "Classified by geotype, LCA material type and regions",
    x = NULL,
    fill = "LCA Material Type"
  ) +  ylab('Total GHG Emissions (kt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 4000),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + scale_x_discrete(limits = rev) +
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
  ) + facet_wrap( ~ region, ncol = 4)

###########################################
###TOTAL END OF LIFE TREATMENT EMISSIONS###
###########################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_total_eolt.csv')) 
data$emission_category = factor(
  data$emission_category,
  levels = c(
    "aluminium_eolt_ghg",
    "steel_iron_eolt_ghg",
    "other_metals_eolt_ghg",
    "concrete_eolt_ghg",
    "optic_fiber_eolt_ghg",
    "plastics_eolt_ghg"
  ),
  labels = c(
    "Aluminium",
    "Steel and Iron",
    "Other Metals",
    "Concrete",
    "Optic Fiber",
    "Plastics"
  )
)

df = data %>%
  group_by(emission_category, geotype, region) %>%
  summarize(eolt_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$geotype = factor(
  df$geotype,
  levels = c('remote', 'rural', 'suburban', 'urban'),
  labels = c('Remote', 'Rural', 'Suburban', 'Urban')
)

totals <- df %>%
  group_by(geotype, emission_category, region) %>%
  summarize(value = signif(sum(eolt_ghgs)))

label_totals <- df %>%
  group_by(geotype, region) %>%
  summarize(total_value = sum(eolt_ghgs))

eolts_emissions <-
  ggplot(df, aes(x = geotype, y = eolt_ghgs/1e6)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + 
  geom_text(data = label_totals, aes(x = geotype, y = total_value/1e6, 
    label = sprintf("%.2f", total_value/1e6)),
    vjust = -0.5,
    hjust = 0.5,
    position = position_stack(), 
    size = 2, color = "black")  +
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(B) End of Life Treatment Phase",
    subtitle = "Classified by geotype, LCA material type and regions",
    x = NULL,
    fill = "LCA Material Type"
  ) + ylab('Total GHG Emissions (kt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 15),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + scale_x_discrete(limits = rev) +
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
  ) + facet_wrap( ~ region, ncol = 4)


########################
##PANEL USER EMISSIONS##
########################
emission_panel <- ggarrange(
  average_emissions_per_subscriber, 
  region_total_emissions, 
  ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom')

emission_category_panel <- ggarrange(
  manufacturing_emissions, 
  eolts_emissions, 
  ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'user_emissions_region.png')
png(path, units="in", width=8.3, height=7, res=300)
print(emission_panel)
dev.off()

path = file.path(folder, 'figures', 'user_emissions_category.png')
png(path, units="in", width=8.3, height=7, res=300)
print(emission_category_panel)
dev.off()



