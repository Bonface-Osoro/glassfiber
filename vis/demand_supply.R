library(ggpubr)
library(ggplot2)
library(tidyverse)
library(cowplot)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_rev_per_area_average.csv'))


###############################
##AVERAGE REVENUE PER AREA ####
###############################

df = data %>%
  group_by(geotype, adoption_scenario) %>%
  summarize(total_rev = mean(revenue_per_area) / 1e3)

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

area_average_revenue <- 
  ggplot(df, aes(x = geotype, y = total_rev, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total_rev, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    title = '',
    subtitle = 'Average Revenue per Area.',
    x = NULL,
    y = "Average Revenue per Area",
  ) + ylab(expression("Average Revenue per Area ($US '0000')")) +
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 6),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 6),
    axis.title.y = element_text(size = 6),
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
      format(y, scientific = FALSE), limit = c(0, 45)
  ) 


#############################
##TOTAL REVENUE PER AREA ####
#############################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_rev_per_area_total.csv'))

df = data %>%
  group_by(geotype, adoption_scenario) %>%
  summarize(total_rev = sum(revenue_per_area)/1e6)

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

area_total_revenue <- 
  ggplot(df, aes(x = geotype, y = total_rev, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total_rev, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    title = '',
    subtitle = 'Total Revenue per Area.',
    x = NULL,
    y = "Total Revenue per Area",
  ) + ylab(expression("Total Revenue per Area ($US Millions)")) +
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 6),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 6),
    axis.title.y = element_text(size = 6),
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
      format(y, scientific = FALSE), limit = c(0, 18)
  ) 

###########################
##AVERAGE TCO PER USER ####
###########################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_tco_per_user_average.csv'))

df = data %>%
  group_by(geotype, adoption_scenario) %>%
  summarize(average_tco = mean(tco_per_user, na.rm = TRUE) / 1e6)

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

user_average_tco <- 
  ggplot(df, aes(x = geotype, y = average_tco, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average_tco, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    title = '',
    subtitle = 'Average TCO per User.',
    x = NULL,
    y = "Average TCO per User",
  ) + ylab(expression("Average TCO per User ($US Millions)")) +
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 6),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 6),
    axis.title.y = element_text(size = 6),
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
      format(y, scientific = FALSE), limit = c(0, 11)
  ) 

#########################
##TOTAL TCO PER USER ####
#########################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_tco_per_user_total.csv'))

df = data %>%
  group_by(geotype, adoption_scenario) %>%
  summarize(average_tco = sum(tco_per_user, na.rm = TRUE) / 1e9)

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

user_total_tco <- 
  ggplot(df, aes(x = geotype, y = average_tco, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average_tco, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    title = '',
    subtitle = 'Total TCO per User.',
    x = NULL,
    y = "Total TCO per User",
  ) + ylab(expression("Total TCO per User ($US Billions)")) +
  scale_fill_brewer(palette = "YlGnBu") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 6),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 6),
    axis.title.y = element_text(size = 6),
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
      format(y, scientific = FALSE), limit = c(0, 12)
  ) 


##############################
## Total Revenue Aggregates ##
##############################
revenues <-
  ggarrange(
    area_average_revenue,
    area_total_revenue,
    user_average_tco,
    user_total_tco,
    ncol = 4,
    nrow = 1,
    common.legend = TRUE,
    labels = c('A', 'B', 'C', 'D'),
    legend = 'bottom'
  ) 

path = file.path(folder, 'figures', 'revenue_and_tco.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 9,
  height = 3,
  res = 480
)
print(revenues)
dev.off()

