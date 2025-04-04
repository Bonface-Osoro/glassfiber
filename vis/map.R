library(ggpubr)
library(ggplot2)
library(tidyverse)
library(ggtext)
library(sf)
library(readr)
library(RColorBrewer)
library(ggspatial)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 
                                 'Africa_Boundaries', 'SSA_combined_shapefile.shp'))
africa_shp <- africa_data %>%
  select(GID_0, NAME_0, GID_1, GID_2, geometry)

new_names <- c('iso3', 'country', 'gid_1', 'GID_2', 'geometry')
colnames(africa_shp) <- new_names

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
  labs(title = "A", 
       x = "Population density (persons per km²)", y = "Frequency", fill = NULL) +
  scale_y_continuous(limits = c(0, 3999), labels = function(y)
      format(y, scientific = FALSE), expand = c(0, 0)) +
  scale_x_continuous(limits = c(1, 250), labels = function(x)
    format(x, scientific = FALSE), expand = c(0, 0)) + theme_minimal() +
    theme(
      axis.title.y = element_text(size = 9),
      axis.title.x = element_text(size = 9),
      strip.text.x = element_blank(),
      panel.border = element_blank(),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      axis.text.x = element_text(size = 8),
      axis.text.y = element_text(size = 8),
      axis.line.x  = element_line(size = 0.15),
      axis.line.y  = element_line(size = 0.15),
      legend.title = element_text(size = 9),
      legend.text = element_text(size = 8),
      legend.position = 'bottom',
      axis.title = element_text(size = 6),
      plot.subtitle = element_text(size = 6),
      plot.title = element_text(size = 9, face = "bold")) +
      guides(fill = guide_legend(ncol = 6, nrow = 2))


###############################################
##POINT SETTLEMENT DISTRIBUTION (ABOVE 20000)##
###############################################
data <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
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
  labs(title = "B",
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
    legend.title = element_text(size = 9),
    legend.text = element_text(size = 8),
    legend.key.size = unit(0.9, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 9, face = "bold")) + 
  guides(color = guide_legend(ncol = 4, nrow = 2))

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
  labs(title = "C",
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
    legend.title = element_text(size = 9),
    legend.text = element_text(size = 8),
    legend.key.size = unit(0.9, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 9, face = "bold")) + 
  guides(color = guide_legend(ncol = 4, nrow = 2))

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
  labs(title = "D",
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
    legend.title = element_text(size = 9),
    legend.text = element_text(size = 8),
    legend.key.size = unit(0.9, "lines"),
    plot.subtitle = element_text(size = 6),
    plot.title = element_text(size = 9, face = "bold")) + 
  guides(color = guide_legend(ncol = 4, nrow = 2))

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
png(path, units = "in", width = 7.2, height = 8, res = 300)
print(demand_point_panel)
dev.off()

############################
##FIBER INFRASTRUCTURE MAP##
############################
africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 
                                 'Africa_Boundaries', 'SSA_combined_shapefile.shp'))

#################################
##CORE FIBER INFRASTRUCTURE MAP##
#################################
core_nodes <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
                                'SSA_core_nodes_existing.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
                                'SSA_core_edges_existing.shp'))
core_nodes$Type <- 'Core Nodes'
core_edges$Type <- 'Core Fiber'

core_fiber <- ggplot() +
  geom_sf(data = africa_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = core_nodes, color = "tomato", size = 0.5, aes(fill = Type)) + 
  geom_sf(data = core_edges, color = "green4", linewidth = 0.3) + 
  labs(title = "(e) Existing fiber infrastructure in SSA", 
       subtitle = "Only live fiber lines with core nodes are mapped", 
       fill = NULL) + 
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
    plot.subtitle = element_text(size = 10),
    plot.title = element_text(size = 10, face = "bold")
  ) +   annotation_scale(location = "bl", width_hint = 0.5) + 
  coord_sf(crs = 4326) + 
  ggspatial::annotation_north_arrow(
    location = "tr", which_north = "true",
    pad_x = unit(0.1, "in"), pad_y = unit(0.1, "in"),
    style = ggspatial::north_arrow_nautical(
      fill = c("grey40", "white"),
      line_col = "grey20",
      text_family = "ArcherPro Book"
    )
  ) 

####################################
##PRIM'S FIBER INFRASTRUCTURE MAP ##
####################################
access_nodes <- st_read(file.path(folder, '..', 'results', 'design_shapefiles',
                                  'SSA_combined_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
                                  'SSA_combined_access_edges.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
                                'SSA_core_edges_existing.shp'))
core_edges$Type <- 'Existing Fiber Line'
access_edges$Type <- 'Designed Fiber Access Lines'

access_prims_fiber <- ggplot() +
  geom_sf(data = africa_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, size = 0.05) + 
  geom_sf(data = access_edges, aes(color = Type), size = 0.3, linewidth = 0.5, show.legend = TRUE) + 
  geom_sf(data = core_edges, aes(color = Type), linewidth = 0.3, show.legend = TRUE) +
  labs(color = "Network Level") + 
  scale_color_manual(values = c("Existing Fiber Line" = "green4", 
         "Designed Fiber Access Lines" = "darkorange")) +
  theme(
    axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 14),
    plot.title = element_text(size = 16, face = "bold"),
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)
  ) + annotation_scale(location = "bl", width_hint = 0.5) + 
  coord_sf(crs = 4326) 

#################################
##PCST FIBER INFRASTRUCTURE MAP##
#################################
access_nodes <- st_read(file.path(folder, '..', 'results', 'design_shapefiles',
                                  'SSA_combined_pcsf_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
                                  'SSA_combined_pcsf_access_edges.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'design_shapefiles', 
                                'SSA_core_edges_existing.shp'))

core_edges$Type <- 'Existing Fiber Line'
access_edges$Type <- 'Designed Fiber Access Lines'

access_pcsf_fiber <- ggplot() +
  geom_sf(data = africa_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, size = 0.05) + 
  geom_sf(data = access_edges, aes(color = Type), size = 0.3, linewidth = 0.5, show.legend = TRUE) + 
  geom_sf(data = core_edges, aes(color = Type), linewidth = 0.3, show.legend = TRUE) + 
  labs(color = "Network Level") + 
  scale_color_manual(values = c("Existing Fiber Line" = "green4", 
        "Designed Fiber Access Lines" = "darkorange")) +
  theme(
    axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 14),
    plot.title = element_text(size = 16, face = "bold"),
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)
  ) + annotation_scale(location = "bl", width_hint = 0.5) + 
  coord_sf(crs = 4326) 

#######################
##PANEL FIBER DESIGN ##
#######################
path = file.path(folder, 'figures', 'prims_fiber_network_design.png')
png(path, units = "in", width = 7, height = 7, res = 300)
print(access_prims_fiber)
dev.off()

path = file.path(folder, 'figures', 'pcst_fiber_network_design.png')
png(path, units = "in", width = 7, height = 7, res = 300)
print(access_pcsf_fiber)
dev.off()


