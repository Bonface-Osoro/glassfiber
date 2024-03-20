library(ggpubr)
library(ggplot2)
library(tidyverse)
library(cowplot)

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
  levels = c(10, 20, 30, 40),
  labels = c('10 GB', '20 GB', '30 GB', '40 GB')
)

df$geotype = factor(
  df$geotype,
  levels = c('remote', 'rural', 'suburban', 'urban'),
  labels = c('Decile 1 \n(<50 per km²)', 'Decile 2 \n(50 - 500 per km²)', 
             'Decile 3 \n(500 - 1000 per km²)', 'Decile 4 \n(>1000 per km²)')
)

demand_area <- 
  ggplot(df, aes(x = geotype, y = average_demand, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average_demand, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    title = '(A) Average Demand per Area.',
    subtitle = 'Based on geotype, demand scenario and monthly traffic.',
    x = NULL,
    y = "Average Demand per Area",
  ) + ylab("Demand per Area (Mbps per km<sup>2)") +
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 6),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_markdown(size = 6),
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 8),
    axis.title.x = element_text(size = 9)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Demand Scenario')) +
  scale_x_discrete(expand = c(0, 0.15)) +
  scale_y_continuous(
    expand = c(0, 0),
    labels = function(y)
      format(y, scientific = FALSE), limit = c(0, 400)
  ) + facet_wrap( ~ monthly_traffic, nrow = 2)



################################
## CAPACITY DEMAND PANEL PLOT ##
################################
path = file.path(folder, 'figures', 'demand.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 7,
  height = 6,
  res = 480
)
print(demand_area)
dev.off()

