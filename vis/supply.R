library(ggpubr)
library(ggplot2)
library(tidyverse)
library(cowplot)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_supply_results.csv'))


#########################
##TOTAL TCO PER USER ####
#########################

#############
##Remote ####
#############

df <- data %>%
  filter(geotype == "remote") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(tco_per_user)) / 1e6)

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

remote_total_tco <- 
  ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
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
    y = "Total TCO per Area",
  ) + ylab(expression("Total TCO per User ($US Millions)")) +
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
      format(y, scientific = FALSE), limit = c(0, 31)
  ) + facet_wrap(~ geotype, ncol = 2)



############
##Rural ####
############
df <- data %>%
  filter(geotype == "rural") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(tco_per_user)) / 1e6)

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

rural_total_tco <- 
  ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
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
    y = "Total TCO per Area",
  ) + ylab(expression("Total TCO per User ($US Millions)")) +
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
      format(y, scientific = FALSE), limit = c(0, 1.2)
  ) + facet_wrap(~ geotype, ncol = 2)


###############
##Suburban ####
###############

df <- data %>%
  filter(geotype == "suburban") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(tco_per_user)) / 1e3)

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

suburban_total_tco <- 
  ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
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
    y = "Total TCO per Area",
  ) + ylab(expression("Total TCO per User ($US '000')")) +
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
      format(y, scientific = FALSE), limit = c(0, 53)
  ) + facet_wrap(~ geotype, ncol = 2)


############
##Urban ####
############

df <- data %>%
  filter(geotype == "urban") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(tco_per_user)) / 1e3)

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

urban_total_tco <- 
  ggplot(df, aes(x = region, y = total, fill = adoption_scenario)) +
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
    y = "Total TCO per Area",
  ) + ylab(expression("Total TCO per User ($US '000')")) +
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
      format(y, scientific = FALSE), limit = c(0, 14.6)
  ) + facet_wrap(~ geotype, ncol = 2)


###################################
## Total TCO per User Aggregates ##
###################################
total_tco <-
  ggarrange(
    remote_total_tco,
    rural_total_tco,
    suburban_total_tco,
    urban_total_tco,
    ncol = 2,
    nrow = 2,
    common.legend = TRUE,
    labels = c('A', 'B', 'C', 'D'),
    legend = 'bottom'
  ) 


path = file.path(folder, 'figures', 'total_tco.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 7,
  height = 6.5,
  res = 480
)
print(total_tco)
dev.off()



###########################
##AVERAGE TCO PER USER ####
###########################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_supply_results.csv'))

#############
##Remote ####
#############
df <- data %>%
  filter(geotype == "remote") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(tco_per_user))

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

remote_mean_tco <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 1.5,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average TCO per Area",
  ) + ylab(expression("Average TCO per User ($US)")) +
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
      format(y, scientific = FALSE), limit = c(0, 120000)
  ) + facet_wrap(~ geotype, ncol = 2)


############
##Rural ####
############
df <- data %>%
  filter(geotype == "rural") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(tco_per_user))

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

rural_mean_tco <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 1.5,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average TCO per Area",
  ) + ylab(expression("Average TCO per User ($US)")) +
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
      format(y, scientific = FALSE), limit = c(0, 2200)
  ) + facet_wrap(~ geotype, ncol = 2)


###############
##Suburban ####
###############
df <- data %>%
  filter(geotype == "suburban") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(tco_per_user))

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

suburban_mean_tco <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 1.5,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average TCO per Area",
  ) + ylab(expression("Average TCO per User ($US)")) +
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
      format(y, scientific = FALSE), limit = c(0, 380)
  ) + facet_wrap(~ geotype, ncol = 2)


############
##Urban ####
############
df <- data %>%
  filter(geotype == "urban") %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(average = mean(tco_per_user))

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

urban_mean_tco <- 
  ggplot(df, aes(x = region, y = average, fill = adoption_scenario)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_text(
    aes(label = as.character(signif(average, 3))),
    size = 1.5,
    position = position_dodge(0.9),
    vjust = 0.5,
    hjust = -0.1,
    angle = 90
  ) +
  labs(
    colour = NULL,
    x = NULL,
    y = "Average TCO per Area",
  ) + ylab(expression("Average TCO per User ($US)")) +
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
      format(y, scientific = FALSE), limit = c(0, 120)
  ) + facet_wrap(~ geotype, ncol = 2)


#####################################
## Average TCO per User Aggregates ##
#####################################
average_tco <-
  ggarrange(
    urban_mean_tco,
    suburban_mean_tco,
    rural_mean_tco,
    remote_mean_tco,
    ncol = 4,
    nrow = 1,
    common.legend = TRUE,
    labels = c('A', 'B', 'C', 'D'),
    legend = 'bottom'
  ) 

path = file.path(folder, 'figures', 'average_tco.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 8,
  height = 3,
  res = 480
)
print(average_tco)
dev.off()



