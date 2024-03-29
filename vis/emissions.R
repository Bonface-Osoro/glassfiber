library(ggpubr)
library(ggplot2)
library(dplyr)
library(tidyverse)
library("readxl")
library(ggtext)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

####################
##TOTAL EMISSIONS###
####################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission.csv'))
df = data %>%
  group_by(region, strategy) %>%
  summarize(total_ghgs = sum(total_ghg_emissions_kg)) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'local'),
  labels = c('Existing \nCore Network', 'New \nRegional Network', 'New \nAccess Network')
)

label_totals <- df %>%
  group_by(region, strategy) %>%
  summarize(total_value = sum(total_ghgs))

total_emissions <-
  ggplot(df, aes(x = strategy, y = total_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + 
  geom_text(data = label_totals, aes(x = strategy, y = total_value/1e9, 
                                     label = sprintf("%.2f", total_value/1e9)),
            vjust = -0.5,
            hjust = 0.5,
            position = position_stack(), 
            size = 2, color = "black") +
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(A) Total Greenhouse Gas (GHG) Emissions.",
    subtitle = "Classified by network level and regions.",
    x = NULL,
    fill = "LCA Material Type"
  ) +  ylab('Total GHG Emissions (Mt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 40),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + 
  theme(
    legend.position = 'none',
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

###################################
##AVERAGE EMISSIONS PER SUBSCRIBER###
###################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission.csv'))
df = data %>%
  group_by(region, strategy) %>%
  summarize(mean_ghg_user = mean(emissions_kg_per_subscriber)) 

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'local'),
  labels = c('Existing \nCore Network', 'New \nRegional Network', 'New \nAccess Network')
)

label_means <- df %>%
  group_by(region, strategy) %>%
  summarize(mean_value = sum(mean_ghg_user))

average_emissions <-
  ggplot(df, aes(x = strategy, y = mean_ghg_user/1e6)) +
  geom_bar(stat = "identity", aes(fill = strategy)) + 
  geom_text(data = label_means, aes(x = strategy, y = mean_value/1e6, 
                                     label = sprintf("%.3f", mean_value/1e6)),
            vjust = -0.5,
            hjust = 0.5,
            position = position_stack(), 
            size = 2, color = "black") +
  scale_fill_brewer(palette = "Dark2") +
  labs(
    colour = NULL,
    title = "(B) Average Greenhouse Gas (GHG) Emissions per Subscriber.",
    subtitle = "Classified by network level and regions.",
    x = NULL
  ) +  ylab('GHG Emissions per user (kt CO<sub>2</sub> eq.)') + 
  scale_y_continuous(
    limits = c(0, 5.9),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + 
  theme(
    legend.position = 'none',
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
data1 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_baseline_total_mfg.csv'))
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_total_mfg.csv'))
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_regional_total_mfg.csv'))
data4 <- merge(data2, data1, by = c("iso3", "strategy", "emission_category", 
                  "lca_phase_ghg_kg", "total_mfg_ghg_kg", "region"), all = TRUE)

data <- merge(data4, data3, by = c("iso3", "strategy", "emission_category", 
       "lca_phase_ghg_kg", "total_mfg_ghg_kg", "region"), all = TRUE)

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
  group_by(emission_category, region, strategy) %>%
  summarize(mfg_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'local'),
  labels = c('Existing \nCore Network', 'New \nRegional Network', 'New \nAccess Network')
)


label_totals <- df %>%
  group_by(region, strategy) %>%
  summarize(total_value = sum(mfg_ghgs))

manufacturing_emissions <-
  ggplot(df, aes(x = strategy, y = mfg_ghgs/1e9)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + 
  geom_text(data = label_totals, aes(x = strategy, y = total_value/1e9, 
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
    limits = c(0, 3.2),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + 
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
data1 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_baseline_total_eolt.csv'))
data2 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_total_eolt.csv'))
data3 <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_regional_total_eolt.csv'))
data4 <- merge(data2, data1, by = c("iso3", "strategy", "emission_category", 
        "lca_phase_ghg_kg", "total_eolt_ghg_kg", "region"), all = TRUE)
data <- merge(data4, data3, by = c("iso3", "strategy", "emission_category", 
        "lca_phase_ghg_kg", "total_eolt_ghg_kg", "region"), all = TRUE)

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
  group_by(emission_category, region, strategy) %>%
  summarize(eolt_ghgs = lca_phase_ghg_kg) %>%
  distinct(emission_category, .keep_all = TRUE)

df$strategy <- factor(
  df$strategy,
  levels = c('baseline', 'regional', 'local'),
  labels = c('Existing \nCore Network', 'New \nRegional Network', 'New \nAccess Network')
)

label_totals <- df %>%
  group_by(region, strategy) %>%
  summarize(total_value = sum(eolt_ghgs))

eolts_emissions <-
  ggplot(df, aes(x = strategy, y = eolt_ghgs/1e6)) +
  geom_bar(stat = "identity", aes(fill = emission_category)) + 
  geom_text(data = label_totals, aes(x = strategy, y = total_value/1e6, 
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
    limits = c(0, 44),
    labels = function(y)
      format(y, scientific = FALSE),
    expand = c(0, 0)
  ) + 
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
  total_emissions, 
  average_emissions, 
  ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='none')

emission_category_panel <- ggarrange(
  manufacturing_emissions, 
  eolts_emissions, 
  ncol = 1, nrow = 2, align = c('hv'),
  common.legend = TRUE, legend='bottom') 

path = file.path(folder, 'figures', 'user_emissions_region.png')
png(path, units="in", width=11, height=7, res=300)
print(emission_panel)
dev.off()

path = file.path(folder, 'figures', 'user_emissions_category.png')
png(path, units="in", width=11, height=7, res=300)
print(emission_category_panel)
dev.off()


