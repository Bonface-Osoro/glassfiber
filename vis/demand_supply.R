library(ggpubr)
library(ggplot2)
library(tidyverse)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_users_results.csv'))

#############################
##Total Revenue Per Area ####
#############################
df = data %>%
  group_by(region, adoption_scenario, geotype) %>%
  summarize(total = (sum(revenue_per_area))/1e6)

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

region_total_area_revenue <-
  ggplot(df,  aes(x = region, y = total, fill = adoption_scenario)) +
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
    title = 'Estimated Total Revenue per Area.',
    subtitle = 'Reported by African Union Regional Classification.',
    x = 'Sub-Saharan African Regions',
    y = "Total Revenue per Area",
  ) +  ylab(expression('Total Revenue per Area ($US Millions)'))  + 
  scale_fill_brewer(palette = "Set1") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 8),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_text(size = 8),
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 8),
    axis.title.x = element_text(size = 9)
  ) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 6, title = 'Demand Scenario')) +
  scale_x_discrete(expand = c(0, 0.15)) +
  facet_wrap( ~ geotype, ncol = 2, scales = 'free') + 
  theme(strip.text = element_text(angle = 0, hjust = -2)) +   scale_y_continuous(
    expand = c(0, 0),
    labels = function(y)
      format(y, scientific = FALSE), limits = c(0, max(df$total) + 3)) 


###############################
##Average Revenue Per Area ####
###############################
df = data %>%
  group_by(region, geotype, adoption_scenario) %>%
  summarize(average = (mean(revenue_per_area)))

df$adoption_scenario = factor(
  df$adoption_scenario,
  levels = c('low', 'baseline', 'high'),
  labels = c('Low', 'Baseline', 'High')
)

region_average_area_revenue <-
  ggplot(df,  aes(x = adoption_scenario, y = average, fill = geotype)) +
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
    title = 'Estimated Average Revenue per Area.',
    subtitle = 'Reported by African Union Regional Classification.',
    x = 'Sub-Saharan African Regions',
    y = "Total Revenue per Area",
  ) +  ylab(expression('Average Revenue per Area ($US)'))  + 
  scale_fill_brewer(palette = "Set1") +
  theme(
    legend.position = 'bottom',
    axis.text.x = element_text(size = 8),
    panel.spacing = unit(0.6, "lines"),
    plot.title = element_text(size = 11),
    plot.subtitle = element_text(size = 10),
    axis.text.y = element_text(size = 8),
    axis.title.y = element_text(size = 8),
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
      format(y, scientific = FALSE),
    limits = c(0, 41500)
  ) + facet_wrap( ~ region, ncol = 4)


#######################
##Revenue Aggregates ##
#######################
revenues <-
  ggarrange(
    region_total_area_revenue,
    region_average_area_revenue,
    ncol = 2,
    common.legend = TRUE,
    labels = c('A', 'B'),
    legend = 'bottom'
  )


path = file.path(folder, 'figures', 'total_average.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
png(
  path,
  units = "in",
  width = 8,
  height = 6.5,
  res = 480
)
print(revenues)
dev.off()






