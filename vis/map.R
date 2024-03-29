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


###################################
##POPULATION DENSITY DISTRIBUTION##
###################################
africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 
     'Africa_Boundaries', 'SSA_combined_shapefile.shp'))

data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_demand_metrics.csv'))
data <- data %>%mutate(iso3 = case_when(iso3 %in% c('NGA', 'ETH', 'COD', 'TZA', 
        'ZAF', 'KEN', 'UGA', 'SDN', 'AGO', 'GHA') ~ as.character(iso3),
        TRUE ~ "Others")) 

data$iso3 = factor(data$iso3,
  levels = c('NGA', 'ETH', 'COD', 'TZA', 'ZAF', 'KEN', 'UGA', 'SDN', 'AGO', 
             'GHA','Others'),
  labels = c('Nigeria', 'Ethiopia', 'DRC', 'Tanzania', 'South Africa', 
             'Kenya', 'Uganda', 'Sudan', 'Angola', 'Ghana', 'Other Countries'))

data = data %>% group_by(GID_2, area, iso3) %>%
  summarise(pop_sum = sum(population),
            pop_density_sqkm = (pop_sum / area))

pop_density <- ggplot(data, aes(x = pop_density_sqkm)) +
  geom_histogram(bins = 50, binwidth = 4,  color = "black", linewidth = 0.05, 
  aes(fill = iso3)) + scale_fill_brewer(palette = "Set3") +
  labs(title = "(a) Population density distribution of SSA countries.", 
  subtitle = 'Grouped by the top 10 most populated countries.',
       x = "Population density (persons per km²)", y = "Frequency", fill = NULL) +
  scale_y_continuous(limits = c(0, 3999), labels = function(y)
      format(y, scientific = FALSE), expand = c(0, 0)) +
  scale_x_continuous(limits = c(1, 250), labels = function(x)
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
      legend.title = element_text(size = 5),
      legend.text = element_text(size = 5),
      legend.position = 'bottom',
      axis.title = element_text(size = 6),
      plot.subtitle = element_text(size = 6),
      plot.title = element_text(size = 7, face = "bold")) +
      guides(fill = guide_legend(ncol = 11, nrow = 1))


#########################################
##SETTLEMENT DISTRIBUTION (ABOVE 1000)##
#########################################
data <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                          'SSA_gid_2_demand_metrics.shp'))
data <- data[!duplicated(data$population), ]

data = data %>% group_by(GID_2) %>%
  summarise(population = sum(population))

data_20 <- data[data$population >= 500, ]

pop_bins <- c(-Inf, 20000, 50000, 100000, 500000, 750000, 1000000, 
              1250000, Inf)
data_20$population_bin <- cut(data_20$population, breaks = pop_bins, labels = 
    c("1 - 20k", "20001 - 50k", "50001 - 100k", "100001 - 500k", 
      "500001 - 750k", "750001 - 1 Million", "1.1 - 1.25 Million", 
      "Above 1.25 Million"))

above_50000 <- ggplot() + 
  geom_sf(data = africa_data, fill = "white", color = "black", linewidth = 0.02) +
  geom_sf(data = data_20, aes(fill = population_bin), 
  linewidth = 0.001,) +
  scale_fill_brewer(palette = "Set3") +
  labs(title = "(B) Above 1,000 people.",
       subtitle = "Summed for all GID 2 sub-regions for each country.",
       fill = "Range") +
  theme_void() +
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.6, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) + 
  guides(fill = guide_legend(nrow = 2))


##########################################
##SETTLEMENT DISTRIBUTION (ABOVE 100000)##
##########################################
data_50 <- data[data$population >= 100000, ]

pop_bins <- c(-Inf, 20000, 50000, 100000, 500000, 750000, 1000000, 
              1250000, Inf)
data_50$population_bin <- cut(data_50$population, breaks = pop_bins, labels = 
  c("Below 20k", "20001 - 50k", "50001 - 100k", "100001 - 500k", "500001 - 750k", 
    "750001 - 1 Million", "1.1 - 1.25 Million", "Above 1.25 Million"))

data_50 <- data_50[, c("population", "population_bin", "geometry")]
lon <- c(6.2, 6.2, 6.2) 
lat <- c(6.2, 6.2, 6.2)
df <- data.frame(population_bin = c("Below 20k", "20001 - 50k", 
      "50001 - 100k"), population = c(0, 0, 0), lat, lon)
df <- st_as_sf(df, coords = c("lon", "lat"), crs = 4326) 

data_50 <- rbind(data_50, df)


above_100000 <- ggplot() + 
  geom_sf(data = africa_data, fill = "white", color = "black", linewidth = 0.02) +
  geom_sf(data = data_50, aes(fill = population_bin), 
           linewidth = 0.001,color = 'white') +
  scale_fill_brewer(palette = "Set3") +
  labs(title = "(C) Above 100,000 people.", 
       subtitle = "Summed for all GID 2 sub-regions for each country.", 
       fill = "Range") +
  theme_void() +
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.6, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) + 
  guides(fill = guide_legend(nrow = 2))

###########################################
##SETTLEMENT DISTRIBUTION (ABOVE 500,000)##
###########################################
data_half <- data[data$population >= 500000, ]

pop_bins <- c(-Inf, 20000, 50000, 100000, 500000, 750000, 1000000, 
              1250000, Inf)
data_half$population_bin <- cut(data_half$population, breaks = pop_bins, labels = 
  c("Below 20k", "20001 - 50k", "50001 - 100k", "100001 - 500k", "500001 - 750k", 
    "750001 - 1 Million", "1.1 - 1.25 Million", "Above 1.25 Million"))

data_half <- data_half[, c("population", "population_bin", "geometry")]
lon <- c(6.2, 6.2, 6.2, 6.2) 
lat <- c(6.2, 6.2, 6.2, 6.2)
df <- data.frame(population_bin = c("Below 20k", "20001 - 50k", "50001 - 100k", 
      "100001 - 500k"), population = c(0, 0, 0, 0), lat, lon)
df <- st_as_sf(df, coords = c("lon", "lat"), crs = 4326) 

data_half <- rbind(data_half, df)

above_half <- ggplot() + 
  geom_sf(data = africa_data, fill = "white", color = "black", linewidth = 0.02) +
  geom_sf(data = data_half, aes(fill = population_bin), 
     linewidth = 0.001, color = 'white') +
  scale_fill_brewer(palette = "Set3") +
  labs(title = "(D) Above 500,000 people.",
       subtitle = "Summed for all GID 2 sub-regions for each country.",
       fill = "Range") +
  theme_void() +
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.6, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) + 
  guides(fill = guide_legend(nrow = 2))


########################
##PANEL DEMAND METRICS##
########################
pop_den_panel <- ggarrange(
  pop_density, legend = 'bottom',
  ncol = 1)

settlement_panel <- ggarrange(
  above_50000, 
  above_100000,align = c('hv'),
  above_half, common.legend = TRUE,
  ncol = 3, nrow = 1, legend = 'bottom')

demand_panel <- ggarrange(
  pop_den_panel, 
  settlement_panel,
  ncol = 1, nrow = 2, 
  common.legend = TRUE, legend='none')

path = file.path(folder, 'figures', 'population_demand_metrics.png')
png(path, units = "in", width = 7.2, height = 7, res = 300)
print(demand_panel)
dev.off()


###############################################
##POINT SETTLEMENT DISTRIBUTION (ABOVE 20000)##
###############################################
data <- st_read(file.path(folder, '..', 'results', 'SSA', 'shapefiles', 
                          'SSA_demand_metrics.shp'))
data <- data[!duplicated(data$population), ]

data_20 <- data[data$population >= 500 & data$population <= 20000, ]

pop_bins <- c(-Inf, 2000, 10000, 20000, 30000, 50000, 500000, 750000, Inf)
data_20$population_bin <- cut(data_20$population, breaks = pop_bins, labels = 
  c("Below 2,000", "2,001 - 10,000", "10,001 - 20,000", "20,001 - 30,000", 
    "30,001 - 50,000", "50,001 - 100,000", "100,001 - 500,000", 
    "Above 500,000"))

data_20 <- data_20[, c("population", "population_bin", "geometry")]
lon <- c(6.2, 6.2, 6.2, 6.2, 6.2) 
lat <- c(6.2, 6.2, 6.2, 6.2, 6.2)
df <- data.frame(population_bin = c("20,001 - 30,000", "30,001 - 50,000", 
  "50,001 - 100,000", "100,001 - 500,000", "Above 500,000"), 
  population = c(0, 0, 0, 0, 0), lat, lon)
df <- st_as_sf(df, coords = c("lon", "lat"), crs = 4326) 

data_20 <- rbind(data_20, df)

below_20000 <- ggplot() + 
  geom_sf(data = africa_data,linewidth = 0.02, fill = "gray96") +
  geom_sf(data = data_20, aes(color = population_bin), 
          size = 0.1) +
  labs(title = "(b) Below 20,000 people.",
       subtitle = "For all settlement points with less than 20,000 people.",
       color = NULL) +
  scale_color_brewer(palette = "Dark2") +
  theme_void() +
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.9, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) + 
  guides(color = guide_legend(ncol = 8, nrow = 1))

##########################################################
##POINT SETTLEMENT DISTRIBUTION (BETWEEN 20000 TO 50000)##
##########################################################
data_50 <- data[data$population >= 20001 & data$population <= 50000, ]

pop_bins <- c(-Inf, 2000, 10000, 20000, 30000, 50000, 500000, 750000, Inf)
data_50$population_bin <- cut(data_50$population, breaks = pop_bins, labels = 
    c("Below 2,000", "2,001 - 10,000", "10,001 - 20,000", "20,001 - 30,000", 
      "30,001 - 50,000", "50,001 - 100,000", "100,001 - 500,000", 
      "Above 500,000"))

data_50 <- data_50[, c("population", "population_bin", "geometry")]
lon <- c(6.2, 6.2, 6.2, 6.2, 6.2, 6.2) 
lat <- c(6.2, 6.2, 6.2, 6.2, 6.2, 6.2)
df <- data.frame(population_bin = c("Below 2,000", "2,001 - 10,000", 
   "10,001 - 20,000", "50,001 - 100,000", "100,001 - 500,000", "Above 500,000"), 
    population =  c(0, 0, 0, 0, 0, 0), lat, lon)
df <- st_as_sf(df, coords = c("lon", "lat"), crs = 4326) 

data_50 <- rbind(data_50, df)

above_20000 <- ggplot() + 
  geom_sf(data = africa_data, linewidth = 0.02, fill = "gray96") +
  geom_sf(data = data_50, aes(color = population_bin), 
          size = 0.1) +
  labs(title = "(c) Between 20,000 - 50,000 people",
       subtitle = "For all settlement points with 20,000 - 50,000 people.",
       color = NULL) +
  scale_color_brewer(palette = "Dark2") +
  theme_void() +
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.9, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) + 
  guides(color = guide_legend(ncol = 8, nrow = 1))

################################################
##POINT SETTLEMENT DISTRIBUTION (ABOVE 50,000)##
################################################
data_half <- data[data$population >= 50001, ]

pop_bins <- c(-Inf, 2000, 10000, 20000, 30000, 50000, 500000, 750000, Inf)
data_half$population_bin <- cut(data_half$population, breaks = pop_bins, labels = 
    c("Below 2,000", "2,001 - 10,000", "10,001 - 20,000", "20,001 - 30,000", 
      "30,001 - 50,000", "50,001 - 100,000", "100,001 - 500,000", 
      "Above 500,000"))

data_half <- data_half[, c("population", "population_bin", "geometry")]
lon <- c(6.2, 6.2, 6.2, 6.2, 6.2) 
lat <- c(6.2, 6.2, 6.2, 6.2, 6.2)
df <- data.frame(population_bin = c("Below 2,000", "2,001 - 10,000", 
   "10,001 - 20,000", "20,001 - 30,000",  "30,001 - 50,000"), 
   population = c(0, 0, 0, 0, 0), lat, lon)

df <- st_as_sf(df, coords = c("lon", "lat"), crs = 4326) 
data_half <- rbind(data_half, df)

above_50000 <- ggplot() + 
  geom_sf(data = africa_data, linewidth = 0.02, fill = "gray96") + 
  geom_sf(data = data_half, aes(color = population_bin), 
          size = 0.1) +
  labs(title = "(d) Above 50,000 people",
       subtitle = "For all settlement points with over 50,000 people.",
       color = NULL) +
  scale_color_brewer(palette = "Dark2") +
  theme_void() +
  theme(
    strip.text.x = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_text(size = 6),
    legend.position = 'bottom',
    axis.title = element_text(size = 8),
    legend.title = element_text(size = 6),
    legend.text = element_text(size = 6),
    legend.key.size = unit(0.9, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 7, face = "bold")) + 
  guides(color = guide_legend(ncol = 8, nrow = 1))

##############################
##PANEL POINT DEMAND METRICS##
##############################
pop_den_panel <- ggarrange(
  pop_density, legend = 'bottom',
  ncol = 1)

settlement_point_panel <- ggarrange(
  below_20000, 
  above_20000,
  above_50000, common.legend = TRUE, align = c('hv'),
  ncol = 3, nrow = 1, legend = 'bottom') 

demand_point_panel <- ggarrange(
  pop_den_panel, 
  settlement_point_panel,
  ncol = 1, nrow = 2, 
  common.legend = TRUE, legend='none') 
  

path = file.path(folder, 'figures', 'population_point_demand_metrics.png')
png(path, units = "in", width = 7.2, height = 7, res = 300)
print(demand_point_panel)
dev.off()








