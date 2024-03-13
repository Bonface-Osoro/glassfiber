library(ggpubr)
library(ggplot2)
library(dplyr)
library(tidyverse)
library("readxl")
library(ggtext)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
###################################
##TOTAL PER SUBSCRIBER EMISSIONS###
###################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_baseline_emission_results.csv'))
df = data %>%
  group_by(iso3) %>%
  summarize(sum_emission = sum(emissions_kg_per_subscriber))

###########################################
##TOTAL BASELINE MANUFACTURING EMISSIONS###
###########################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_baseline_total_mfg.csv'))
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
  group_by(emission_category, region) %>%
  summarize(mfg_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

totals <- df %>%
  group_by(emission_category, region) %>%
  summarize(value = signif(sum(mfg_ghgs)))

label_totals <- df %>%
  group_by(region) %>%
  summarize(total_value = sum(mfg_ghgs))

manufacturing_emissions <-
  ggplot(df, aes(x = region, y = mfg_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + 
  geom_text(data = label_totals, aes(x = region, y = total_value/1e9, 
                                     label = sprintf("%.2f", total_value/1e9)),
            vjust = -0.5,
            hjust = 0.5,
            position = position_stack(), 
            size = 2, color = "black") +
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(A) Manufacturing Phase",
    subtitle = "Classified by LCA material type and regions.",
    x = NULL,
    fill = "LCA Material Type"
  ) +  ylab('Total GHG Emissions (Mt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 3.499),
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
  )

###########################################
###TOTAL END OF LIFE TREATMENT EMISSIONS###
###########################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_baseline_total_eolt.csv')) 
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
  group_by(emission_category, region) %>%
  summarize(eolt_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

totals <- df %>%
  group_by(emission_category, region) %>%
  summarize(value = signif(sum(eolt_ghgs)))

label_totals <- df %>%
  group_by(region) %>%
  summarize(total_value = sum(eolt_ghgs))

eolts_emissions <-
  ggplot(df, aes(x = region, y = eolt_ghgs/1e6)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + 
  geom_text(data = label_totals, aes(x = region, y = total_value/1e6, 
                                     label = sprintf("%.2f", total_value/1e6)),
            vjust = -0.5,
            hjust = 0.5,
            position = position_stack(), 
            size = 2, color = "black")  +
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(B) End of Life Treatment Phase",
    subtitle = "Classified by LCA material type and regions",
    x = NULL,
    fill = "LCA Material Type"
  ) + ylab('Total GHG Emissions (kt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 45),
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
  )





