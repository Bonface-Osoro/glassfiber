library(ggpubr)
library(ggplot2)
library(tidyverse)
library(ggtext)
library(sf)
library(readr)
library(RColorBrewer)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 
                                 'Africa_Boundaries', 'SSA_combined_shapefile.shp'))
africa_shp <- africa_data %>%
  select(GID_0, NAME_0, GID_1, GID_2, geometry)

new_names <- c('iso3', 'country', 'gid_1', 'GID_2', 'geometry')
colnames(africa_shp) <- new_names

create_sf_plot <-
  function(data, data_2, fill_variable, legend_title, plot_title,
           plot_subtitle) {
    # Get unique values
    unique_values <- unique(data[[fill_variable]])
    # Create a Brewer color palette
    num_colors <- length(unique_values) - 1
    colors <- brewer_color_ramp(num_colors)
    # Create a color gradient, including grey for zero
    gradient_colors <- c("grey", colors)
    gradient_breaks <- c(0, sort(unique_values[unique_values != 0]))
    plot_title <- paste0(plot_title, "\n")
    plot <-
      ggplot(data) + geom_sf(
        data = data_2,
        fill = NA,
        color = "dodgerblue",
        linewidth = 0.1,
        alpha = 1
      ) +
      geom_sf(
        aes(fill = .data[[fill_variable]]),
        linewidth = 0.01,
        alpha = 0.8,
        color = "white"
      ) +
      theme_transparent() + scale_fill_gradientn(
        colors = gradient_colors,
        values = scales::rescale(gradient_breaks),
        name = legend_title
      ) +
      labs(title = plot_title, subtitle = plot_subtitle) + theme(
        text = element_text(color = "#22211d", family = "Arial"),
        panel.background = element_rect(fill = "transparent", color = NA),
        plot.title = element_text(size = 12, face = 'bold', hjust = 0),
        plot.subtitle = element_text(size = 9),
        legend.position = 'bottom',
        legend.key.width = unit(0.05, "npc"),
        legend.text = element_text(size = 9),
        legend.title = element_text(size = 8)
      ) +
      guides(fill = guide_colourbar(title.position = 'top', direction = "horizontal")) +
      coord_sf()
    return(plot)
  }

########
##TCO ##
########
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_regional_tco_results.csv'))
data = data %>%
  distinct(iso3, tco, .keep_all = TRUE) %>%
  group_by(iso3) %>%
  summarize(tco = (tco)/ 1e6)

merged_data <- merge(africa_shp, data, by = "iso3")

brewer_color_ramp <- colorRampPalette(brewer.pal(11, "Spectral"))
num_colors <- length(unique(merged_data$tco))

tco_country <- create_sf_plot(
  data = merged_data,
  merged_data,
  fill_variable = "tco",
  legend_title = "Amount (US$ millions)",
  plot_title = "(A) Total Cost of Ownership (TCO).",
  plot_subtitle = 'Average TCO for Individual Countries.'
)

#####################
##SSA TCO Per User ##
#####################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_regional_tco_results.csv'))

data = data %>%
  distinct(iso3, tco_per_user, .keep_all = TRUE) %>%
  group_by(iso3) %>%
  summarize(tco_user = (tco_per_user)/ 1e6)

merged_data <- merge(africa_shp, data, by = "iso3")

brewer_color_ramp <- colorRampPalette(brewer.pal(11, "Spectral"))
num_colors <- length(unique(merged_data$tco_user))

tco_per_user <- create_sf_plot(
  data = merged_data,
  merged_data,
  fill_variable = "tco_user",
  legend_title = "Amount (US$ millions)",
  plot_title = "(B) Average TCO per Subscriber",
  plot_subtitle = 'Average TCO per subcriber for Individual Countries.'
)

###########################
##SSA Total GHG Emission ##
###########################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission.csv'))
data <- data[data$strategy == "regional", ]

data = data %>%
  distinct(iso3, total_ghg_emissions_kg, .keep_all = TRUE) %>%
  group_by(iso3) %>%
  summarize(total_ghgs = (total_ghg_emissions_kg)/ 1e9)

merged_data <- merge(africa_shp, data, by = "iso3")

brewer_color_ramp <- colorRampPalette(brewer.pal(11, "Spectral"))
num_colors <- length(unique(merged_data$total_ghgs))

country_total_ghg <- create_sf_plot(
  data = merged_data,
  merged_data,
  fill_variable = "total_ghgs",
  legend_title = ylab("GHG Emissions (Mt of Carbondioxide equivalent)"),
  plot_title = "(A) Total Greenhouse Gas (GHG) Emissions.",
  plot_subtitle = 'GHG emissions for each country due to construction of regional fiber network.'
)

###################################
##SSA GHG Emission per subscriber##
##################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission.csv'))
data <- data[data$strategy == "regional", ]

data = data %>%
  distinct(iso3, emissions_kg_per_subscriber, .keep_all = TRUE) %>%
  group_by(iso3) %>%
  summarize(ghg_per_user = (emissions_kg_per_subscriber)/ 1e6)

merged_data <- merge(africa_shp, data, by = "iso3")

brewer_color_ramp <- colorRampPalette(brewer.pal(11, "Spectral"))
num_colors <- length(unique(merged_data$ghg_per_user))

country_avg_ghg_per_user <- create_sf_plot(
  data = merged_data,
  merged_data,
  fill_variable = "ghg_per_user",
  legend_title = ylab("GHG Emissions (kt of Carbondioxide equivalent)"),
  plot_title = "(B) Average GHG Emissions per Subscriber.",
  plot_subtitle = 'GHG emissions per user for each country due to construction of regional fiber network.'
)

#####################
##PANEL PLOTS COSTS##
#####################
cost_panel <- ggarrange(tco_country, tco_per_user, 
              ncol = 2, nrow = 1, align = c('hv'),
              common.legend = FALSE, legend='bottom')

path = file.path(folder, 'figures', 'tco_maps.png')
png(path, units = "in", width = 10, height = 6, res = 300)
print(cost_panel)
dev.off()

#########################
##PANEL PLOTS EMISSIONS##
#########################
emission_panel <- ggarrange(country_total_ghg, country_avg_ghg_per_user, 
              ncol = 2, nrow = 1, align = c('hv'),
              common.legend = FALSE, legend='bottom')

path = file.path(folder, 'figures', 'emissions_maps.png')
png(path, units = "in", width = 10, height = 6, res = 300)
print(emission_panel)
dev.off()

############################
##FIBER INFRASTRUCTURE MAP##
############################
core_nodes <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
              'SSA_core_nodes_existing.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
              'SSA_core_edges_existing.shp'))
regional_nodes <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
              'SSA_combined_regional_nodes.shp'))
regional_edges <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
              'SSA_combined_regional_edges.shp'))
access_nodes <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
               'SSA_combined_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
  
                                               'SSA_combined_access_edges.shp'))

fiber_map <- ggplot() +
  geom_sf(data = access_nodes, color = "black", size = 0.05) +
  geom_sf(data = access_edges, color = "darkolivegreen2", size = 0.005) + 
  geom_sf(data = regional_nodes, color = "gold", size = 1) + 
  geom_sf(data = regional_edges, color = "magenta", size = 0.1) + 
  geom_sf(data = core_nodes, color = "tomato", size = 1.5) + 
  geom_sf(data = core_edges, color = "green4", size = 0.3) +  
  theme_transparent() +
  labs(title = "Spatial Distribution of Nodes and Edges", 
       subtitle = "\nDifferent color for different shapefiles") + theme(
    text = element_text(color = "#22211d", family = "Arial"),
    panel.background = element_rect(fill = "transparent", color = NA),
    plot.title = element_text(size = 12, face = 'bold', hjust = 0),
    plot.subtitle = element_text(size = 9),
    legend.position = 'bottom',
    legend.key.width = unit(0.05, "npc"),
    legend.text = element_text(size = 9),
    legend.title = element_text(size = 8)
  )

###################################
##POPULATION DENSITY DISTRIBUTION##
###################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_demand_metrics.csv'))
data = data %>% group_by(GID_2, area) %>%
  summarise(pop_sum = sum(population),
            pop_density_sqkm = (pop_sum / area))

pop_density <- ggplot(data, aes(x = pop_density_sqkm)) +
  geom_histogram(fill = "goldenrod", color = "black", bins = 50, binwidth = 4) +
  labs(title = "(A) Population density distribution of SSA.", 
  subtitle = 'For settlement areas with population density above the national average.',
       x = "Population density (persons per km²)", y = "Frequency") +
  scale_y_continuous(limits = c(0, 3900), labels = function(y)
      format(y, scientific = FALSE), expand = c(0, 0)) +
  scale_x_continuous(limits = c(1, 400), labels = function(x)
    format(x, scientific = FALSE), expand = c(0, 0)) + theme_minimal() +
    theme(
      axis.title.y = element_text(size = 6),
      strip.text.x = element_blank(),
      panel.border = element_blank(),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.x = element_text(size = 6),
      axis.text.y = element_text(size = 6),
      axis.line.x  = element_line(size = 0.15),
      axis.line.y  = element_line(size = 0.15),
      legend.position = 'bottom',
      axis.title = element_text(size = 6),
      plot.subtitle = element_text(size = 6),
      plot.title = element_text(size = 7, face = "bold"))

#####################################
##TOP 10 MOSTLY POPULATED COUNTRIES##
#####################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_demand_metrics.csv'))
data <- data[!duplicated(data$population), ]
data <- data[!duplicated(data$area), ]

data = data %>% group_by(iso3) %>%
  summarise(pop_sum = sum(population),
            total_area = sum(area),
            pop_density_sqkm = (pop_sum / total_area))

top_countries = data %>%
  group_by(iso3) %>%
  summarise(total_density = mean(pop_density_sqkm)) %>%
  arrange(desc(total_density)) %>%
  head(10)

top_countries$iso3 = factor(
  top_countries$iso3,
  levels = c('GMB', 'BDI', 'NGA', 'KEN', 'GHA', 'TGO', 'MWI', 'SEN', 'UGA', 'RWA'),
  labels = c('Gambia', 'Burundi', 'Nigeria', 'Kenya', 'Ghana', 'Togo', 
             'Malawi', 'Senegal', 'Uganda', 'Rwanda'))

countries_10 <- ggplot(data = top_countries, aes(x = reorder(iso3, 
  total_density), y = total_density, fill = iso3)) +
  geom_bar(stat = 'identity', position = position_dodge(0.9)) + coord_flip() + 
  geom_text(aes(label = formatC(signif(after_stat(y), 3), 
     digits = 3, format = "fg", flag = "#")), size = 1.8, position = 
     position_dodge(0.9), vjust = 0.5, hjust = -0.3) + 
  scale_fill_brewer(palette = "Set3") + theme_minimal() +
  labs(colour = NULL, title = '(B) Top 10 Densely populated SSA Countries.',
       subtitle = 'For settlement areas with population density above the national average.',
       y = 'National population density average (persons per km²)', 
       x = NULL, fill = NULL) +
  theme(axis.title.y = element_text(size = 6),
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.text.x = element_text(size = 6),
    axis.text.y = element_text(size = 6),
    axis.line.x  = element_line(size = 0.15),
    axis.line.y  = element_line(size = 0.15),
    legend.position = 'none',
    axis.title = element_text(size = 6),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) +
  expand_limits(y = 0) +
  guides(fill = guide_legend(ncol = 5, title = 'SSA Regions')) +
  scale_x_discrete(expand = c(0, 0.15)) +
  scale_y_continuous(expand = c(0, 0),
  labels = function(y) format(y, scientific = FALSE),limits = c(0, 150)) 


#########################################
##SETTLEMENT DISTRIBUTION (BELOW 50000)##
#########################################
data <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
        'SSA_gid_2_demand_metrics.shp'))
data <- data[!duplicated(data$population), ]

data = data %>% group_by(GID_2) %>%
  summarise(population = sum(population))

data_10 <- data[data$population <= 50000, ]

pop_bins <- c(-Inf, 20000, 30000, 40000, Inf)
data_10$population_bin <- cut(data_10$population, breaks = pop_bins, labels = 
      c("Below 20k", "20001 - 30k", "30001 - 40k", "Above 40k"))

below_50000 <- ggplot() + geom_sf(data = data_10, aes(fill = population_bin), 
  linewidth = 0.001,) +
  scale_fill_brewer(palette = "Set3") +
  labs(title = " ",
       subtitle = "(C) Below 50,000 people ",
       fill = "Range") +
  theme_void() +
  theme(
    axis.title.y = element_text(size = 6),
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(size = 6),
    legend.title = element_text(size = 5),
    legend.text = element_text(size = 5),
    legend.position = 'bottom',
    legend.key.size = unit(0.4, "lines"),
    plot.subtitle = element_text(size = 6, face = "bold"),
    plot.title = element_text(size = 10, face = "bold",hjust = -0.45, 
                              vjust = 2.12)) + 
  guides(fill = guide_legend(ncol = 2))


#########################################
##SETTLEMENT DISTRIBUTION (ABOVE 50000)##
#########################################
data_20 <- data[data$population >= 50000, ]

pop_bins <- c(-Inf, 50000, 150000, 300000, 500000, Inf)
data_20$population_bin <- cut(data_20$population, breaks = pop_bins, labels = 
     c("Below 50k", "50001 - 150k", "150001 - 300k",  
     "300001 - 500k","Above 500k"))

above_50000 <- ggplot() + geom_sf(data = data_20, aes(fill = population_bin), 
  linewidth = 0.001,) +
  scale_fill_brewer(palette = "Set3") +
  labs(title = " ",
       subtitle = "(D) Above 50,000 people ",
       fill = "Range") +
  theme_void() +
  theme(
    axis.title.y = element_text(size = 6),
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(size = 6),
    legend.title = element_text(size = 5),
    legend.text = element_text(size = 5),
    legend.position = 'bottom',
    legend.key.size = unit(0.4, "lines"),
    plot.subtitle = element_text(size = 6, face = "bold"),
    plot.title = element_text(size = 10, face = "bold",hjust = -0.45, 
                              vjust = 2.12)) + 
  guides(fill = guide_legend(ncol = 2))


##########################################
##SETTLEMENT DISTRIBUTION (ABOVE 100000)##
##########################################
data_50 <- data[data$population >= 100000, ]

pop_bins <- c(-Inf, 100000, 250000, 500000, 750000, Inf)
data_50$population_bin <- cut(data_50$population, breaks = pop_bins, labels = 
   c("Below 100k", "100001 - 250k", "250001 - 500k",  
   "500001 - 750k","Above 750k"))

above_100000 <- ggplot() + geom_sf(data = data_50, aes(fill = population_bin), 
                                   linewidth = 0.001,) +
  scale_fill_brewer(palette = "Set3") +
  labs(title = " ", subtitle = "(E) Above 100,000 people ", 
       fill = "Range") +
  theme_void() +
  theme(
    axis.title.y = element_text(size = 6),
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(size = 6),
    legend.title = element_text(size = 5),
    legend.text = element_text(size = 5),
    legend.position = 'bottom',
    legend.key.size = unit(0.4, "lines"),
    plot.subtitle = element_text(size = 6, face = "bold"),
    plot.title = element_text(size = 10, face = "bold",hjust = -0.45, 
                              vjust = 2.12)) + 
  guides(fill = guide_legend(ncol = 2))

###########################################
##SETTLEMENT DISTRIBUTION (ABOVE 500,000)##
###########################################
data_half <- data[data$population >= 500000, ]

pop_bins <- c(-Inf, 500000, 750000, 1000000, 1250000, Inf)
data_half$population_bin <- cut(data_half$population, breaks = pop_bins, labels = 
      c("Below 500k", "500001 - 750000", "750001 - 1 Million", 
        "1.1 - 1.25 Million", "Above 1.25 Million"))

above_half <- ggplot() + geom_sf(data = data_half, aes(fill = population_bin), 
                                   linewidth = 0.001,) +
  scale_fill_brewer(palette = "Set3") +
  labs(title = " ",
       subtitle = "(F) Above 500,000 people ",
       fill = "Range") +
  theme_void() +
  theme(
    axis.title.y = element_text(size = 6),
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(size = 6),
    legend.title = element_text(size = 5),
    legend.text = element_text(size = 5),
    legend.position = 'bottom',
    legend.key.size = unit(0.4, "lines"),
    plot.subtitle = element_text(size = 6, face = "bold"),
    plot.title = element_text(size = 8, face = "bold",hjust = -0.45, 
                              vjust = 2.12)) + 
  guides(fill = guide_legend(ncol = 2))


########################
##PANEL DEMAND METRICS##
########################
pop_den_panel <- ggarrange(
  pop_density, 
  countries_10, 
  ncol = 2)

settlement_panel <- ggarrange(
  below_50000, 
  above_50000, 
  above_100000,
  above_half,
  ncol = 2, nrow = 2, legend='bottom')

demand_panel <- ggarrange(
  pop_den_panel, 
  settlement_panel,
  ncol = 1, nrow = 2, heights = c(0.5, 1),
  common.legend = TRUE, legend='none')

path = file.path(folder, 'figures', 'population_demand_metrics.png')
png(path, units="in", width=7, height=7, res=300)
print(demand_panel)
dev.off()






