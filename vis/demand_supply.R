library(ggpubr)
library(ggplot2)
library(tidyverse)
library(cowplot)
library(ggtext)
library(sf)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)


############################
##TOTAL DEMAND PER AREA ####
############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_average_demand.csv'))

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

df$geotype = factor(
  df$geotype,
  levels = c('decile 10', 'decile 9', 'decile 8', 'decile 7', 'decile 6',
             'decile 5', 'decile 4', 'decile 3', 'decile 2', 'decile 1'),
  labels = c('Decile 10 \n(>700 per km²)', 'Decile 9 \n(600 - 700 per km²)', 
             'Decile 8 \n(500 - 600 per km²)', 'Decile 7 \n(400 - 500 per km²)', 
             'Decile 6 \n(300 - 400 per km²)', 'Decile 5 \n(200 - 300 per km²)',
             'Decile 4 \n(100 - 200 per km²)', 'Decile 3 \n(75 - 100 per km²)',
             'Decile 2 \n(50 - 75 per km²)', 'Decile 1 \n(<50 per km²)')
)

demand_area <- 
  ggplot(df, aes(x = geotype, y = average_demand, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) + coord_flip() + 
  geom_text(aes(label = as.character(signif(average_demand, 3))), size = 2, 
    position = position_dodge(0.9), vjust = 0.5, hjust = -0.1) +
  labs(colour = NULL, title = '(a) Average Demand per Area.',
    subtitle = 'Based on geotype, demand scenario and monthly traffic.',
    x = NULL, y = "Average Demand per Area (Mbps per km²)") + 
  scale_fill_brewer(palette = "YlGnBu") +
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
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Demand Scenario')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
    labels = function(y)format(y, scientific = FALSE), limit = c(0, 280)) + 
  facet_wrap( ~ monthly_traffic, ncol = 4)

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
  labs(title = "(b) Average demand per area.",
  subtitle = "Estimated for baseline adoption scenario and different monthly traffic.",
       fill = "Demand per Area \n  (Mbpsper km²)") + 
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
  legend = 'bottom')


path = file.path(folder, 'figures', 'demand.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 11,
  height = 10,
  res = 480
)
print(demand_panel)
dev.off()

###############################
##AVERAGE REVENUE PER USER ####
###############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 
        'SSA_tco_results.csv'))

df = data %>%
  group_by(algorithm, strategy) %>%
  summarize(avg_tco_per_user = (mean(tco_per_user)) / 1e3) 

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

totals <- df %>%
  group_by(algorithm) %>%
  summarize(value = signif(sum(avg_tco_per_user)))

revenue_area <- 
  ggplot(df, aes(x = algorithm, y = avg_tco_per_user)) +
  geom_bar(stat = "identity", aes(fill = strategy)) +
  geom_text(aes(x = algorithm, y = value, label = round(value, 2)
    ),size = 2.5, data = totals, vjust = 0.06, hjust = -0.1, 
    position = position_dodge(0.9)) + 
  labs(colour = NULL, title = '(a) Average TCO per user.',
       subtitle = 'Estimated by averaging the per user TCO for each SSA country.',
       x = 'Spatial Optimization Algorithm', y = "Average TCO per user ($ '000')") + 
  scale_fill_brewer(palette = "YlGnBu") +
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
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Fiber Hirearchy')) +
  scale_x_discrete(expand = c(0, 0.15)) + scale_y_continuous(expand = c(0, 0),
  labels = function(y)format(y, scientific = FALSE), limit = c(0, 73))
