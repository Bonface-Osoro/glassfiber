library(ggpubr)
library(ggplot2)
library(tidyverse)
library(cowplot)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_users_results.csv'))


############################
##Total REVNUE PER AREA ####
############################

#############
##Remote ####
#############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == "remote") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(revenue_per_area)) / 1e4)

# Rest of your plotting code
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

remote_total_area_revenue <- ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Total Revenue per Area",
  ) + ylab(expression("Total Revenue per Area ($US '0000')")) +
  scale_fill_brewer(palette = "Set1") +
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
      format(y, scientific = FALSE), limit = c(0, 0.35)
  ) + facet_wrap(~ geotype, ncol = 2)


#############
##Rural ####
#############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == "rural") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(revenue_per_area)) / 1e5)

# Rest of your plotting code
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

rural_total_area_revenue <- ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Total Revenue per Area",
  ) + ylab(expression("Total Revenue per Area ($US '00000')")) +
  scale_fill_brewer(palette = "Set1") +
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
      format(y, scientific = FALSE), limit = c(0, 2.2)
  ) + facet_wrap(~ geotype, ncol = 2)


###############
##suburban ####
###############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == 'suburban') %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(revenue_per_area)) / 1e6)

# Rest of your plotting code
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

suburban_total_area_revenue <- ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Total Revenue per Area",
  ) + ylab(expression('Total Revenue per Area ($US Millions)')) +
  scale_fill_brewer(palette = "Set1") +
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
      format(y, scientific = FALSE), limit = c(0, 0.3)
  ) + facet_wrap(~ geotype, ncol = 2)


############
##Urban ####
############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == 'urban') %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(revenue_per_area)) / 1e6)

# Rest of your plotting code
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

urban_total_area_revenue <- ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(total, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
  ) + ylab(expression('Total Revenue per Area ($US Millions)')) +
  scale_fill_brewer(palette = "Set1") +
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
  ) + facet_wrap(~ geotype, ncol = 2)



##############################
## Total Revenue Aggregates ##
##############################

revenues <-
  ggarrange(
    remote_total_area_revenue,
    rural_total_area_revenue,
    suburban_total_area_revenue,
    urban_total_area_revenue,
    ncol = 2,
    nrow = 2,
    common.legend = TRUE,
    labels = c('A', 'B', 'C', 'D'),
    legend = 'bottom'
  ) 


path = file.path(folder, 'figures', 'total_revenue.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 7,
  height = 6.5,
  res = 480
)
print(revenues)
dev.off()


###############################
##AVERAGE REVENUE PER AREA ####
###############################

#############
##Remote ####
#############

# Filter data for the desired geotype (e.g., "urban")
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_users_results.csv'))
df <- data %>%
  filter(geotype == "remote") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(revenue_per_area))

# Rest of your plotting code
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

remote_mean_area_revenue <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average Revenue per Area",
  ) + ylab(expression("Average Revenue per Area ($US)")) +
  scale_fill_brewer(palette = "Set1") +
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
  ) + facet_wrap(~ geotype, ncol = 2)


#############
##Rural ####
#############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == "rural") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(revenue_per_area))

# Rest of your plotting code
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

rural_mean_area_revenue <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average Revenue per Area",
  ) + ylab(expression("Average Revenue per Area ($US)")) +
  scale_fill_brewer(palette = "Set1") +
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
      format(y, scientific = FALSE), limit = c(0, 1600)
  ) + facet_wrap(~ geotype, ncol = 2)


###############
##suburban ####
###############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == 'suburban') %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(revenue_per_area))

# Rest of your plotting code
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

suburban_mean_area_revenue <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average Revenue per Area",
  ) + ylab(expression('Average Revenue per Area ($US)')) +
  scale_fill_brewer(palette = "Set1") +
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
      format(y, scientific = FALSE), limit = c(0, 9100)
  ) + facet_wrap(~ geotype, ncol = 2)


############
##Urban ####
############

# Filter data for the desired geotype (e.g., "urban")
df <- data %>%
  filter(geotype == 'urban') %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = (mean(revenue_per_area)) / 1e6)

# Rest of your plotting code
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

urban_mean_area_revenue <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(width = 1, stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 2,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
  ) + ylab(expression('Average Revenue per Area ($US Millions)')) +
  scale_fill_brewer(palette = "Set1") +
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
      format(y, scientific = FALSE), limit = c(0, 0.55)
  ) + facet_wrap(~ geotype, ncol = 2)


##############################
## Total Revenue Aggregates ##
##############################
avg_revenues <-
  ggarrange(
    remote_mean_area_revenue,
    rural_mean_area_revenue,
    suburban_mean_area_revenue,
    urban_mean_area_revenue,
    ncol = 2,
    nrow = 2,
    common.legend = TRUE,
    labels = c('A', 'B', 'C', 'D'),
    legend = 'bottom'
  ) 


path = file.path(folder, 'figures', 'average_revenue.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 7,
  height = 6.5,
  res = 480
)
print(avg_revenues)
dev.off()

