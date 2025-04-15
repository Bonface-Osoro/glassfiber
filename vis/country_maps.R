library(ggplot2)
library(dplyr)
library(tidyr)
library(sf)
library(ggpubr)
library(ggspatial)
library(grid)
library(osmdata)
library(prettymapr)
library(ggmap)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

############################################
##PRIM'S FIBER INFRASTRUCTURE NIGERIA MAP ##
############################################
NGA_data <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA', 
                                 'regions', 'regions_2_NGA.shp'))
access_nodes <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA',
                                  'buffer_routing_zones', 'combined',
                                  'NGA_combined_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA', 
                                  'buffer_routing_zones', 'combined',
                                  'NGA_combined_access_edges.shp'))

core_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA',
                                'network_existing',
                                'NGA_core_edges_existing.shp'))

core_edges$Type <- 'Existing Fiber Line'
access_edges$Type <- 'Designed Fiber Access Lines'

NGA_access_prims_fiber <- ggplot() +
  annotation_map_tile(type = "osm", zoom = 6) +
  geom_sf(data = NGA_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, size = 0.05) + 
  geom_sf(data = access_edges, aes(color = Type), size = 0.3, linewidth = 0.5, show.legend = TRUE) + 
  geom_sf(data = core_edges, aes(color = Type), linewidth = 0.3, show.legend = TRUE) +
  labs(title = "(A) Nigeria", 
       subtitle = "MST Prim's algorithm", color = "Network Level") + 
  scale_color_manual(values = c("Existing Fiber Line" = "green4", 
                                "Designed Fiber Access Lines" = "darkorange")) +
  theme(axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 14),
    plot.title = element_text(size = 16, face = "bold"),
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)) + 
  annotation_scale(location = "bl", width_hint = 0.2) +
  coord_sf(crs = 4326) 


access_nodes <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA',
                                  'buffer_routing_zones', 'combined',
                                  'NGA_combined_pcsf_subregional_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA', 
                                  'buffer_routing_zones', 'combined',
                                  'NGA_combined_pcsf_access_edges.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'NGA',
                                'network_existing',
                                'NGA_core_edges_existing.shp'))

core_edges$Type <- 'Existing Fiber Line'
access_edges$Type <- 'Designed Fiber Access Lines'

NGA_access_pcsf_fiber <- ggplot() +
  annotation_map_tile(type = "osm", zoom = 6) +
  geom_sf(data = NGA_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, size = 0.05) + 
  geom_sf(data = access_edges, aes(color = Type), size = 0.3, linewidth = 0.5, show.legend = TRUE) + 
  geom_sf(data = core_edges, aes(color = Type), linewidth = 0.3, show.legend = TRUE) + 
  labs(title = " ", 
       subtitle = "PCST algorithm", color = "Network Level") + 
  scale_color_manual(values = c("Existing Fiber Line" = "green4", 
                                "Designed Fiber Access Lines" = "darkorange")) +
  theme(axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 14),
    plot.title = element_text(size = 16, face = "bold"),
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)) + 
  annotation_scale(location = "bl", width_hint = 0.2) +
  coord_sf(crs = 4326) 

#############################################
##PRIM'S FIBER INFRASTRUCTURE ETHIOPIA MAP ##
#############################################
ETH_data <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH', 
                              'regions', 'regions_2_ETH.shp'))

access_nodes <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH',
                                  'buffer_routing_zones', 'combined',
                                  'ETH_combined_access_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH', 
                                  'buffer_routing_zones', 'combined',
                                  'ETH_combined_access_edges.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH',
                                'network_existing',
                                'ETH_core_edges_existing.shp'))
core_edges$Type <- 'Existing Fiber Line'
access_edges$Type <- 'Designed Fiber Access Lines'

ETH_access_prims_fiber <- ggplot() +
  annotation_map_tile(type = "osm", zoom = 6) +
  geom_sf(data = ETH_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, size = 0.05) + 
  geom_sf(data = access_edges, aes(color = Type), size = 0.3, linewidth = 0.5, show.legend = TRUE) + 
  geom_sf(data = core_edges, aes(color = Type), linewidth = 0.3, show.legend = TRUE) +
  labs(title = "(B) Ethiopia", 
       subtitle = "MST Prim's algorithm", color = "Network Level") + 
  scale_color_manual(values = c("Existing Fiber Line" = "green4", 
                                "Designed Fiber Access Lines" = "darkorange")) +
  theme(axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 14),
    plot.title = element_text(size = 16, face = "bold"),
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)) + 
  annotation_scale(location = "bl", width_hint = 0.2) +
  coord_sf(crs = 4326) 


access_nodes <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH',
                                  'buffer_routing_zones', 'combined',
                                  'ETH_combined_pcsf_subregional_nodes.shp'))
access_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH', 
                                  'buffer_routing_zones', 'combined',
                                  'ETH_combined_pcsf_access_edges.shp'))
core_edges <- st_read(file.path(folder, '..', 'results', 'processed', 'ETH',
                                'network_existing',
                                'ETH_core_edges_existing.shp'))

core_edges$Type <- 'Existing Fiber Line'
access_edges$Type <- 'Designed Fiber Access Lines'

ETH_access_pcsf_fiber <- ggplot() +
  annotation_map_tile(type = "osm", zoom = 6) +
  geom_sf(data = ETH_data, fill = "gray96", color = "black", linewidth = 0.05) +
  geom_sf(data = access_nodes, size = 0.05) + 
  geom_sf(data = access_edges, aes(color = Type), size = 0.3, linewidth = 0.5, show.legend = TRUE) + 
  geom_sf(data = core_edges, aes(color = Type), linewidth = 0.3, show.legend = TRUE) + 
  labs(title = " ", 
       subtitle = "PCST algorithm", color = "Network Level") + 
  scale_color_manual(values = c("Existing Fiber Line" = "green4", 
                                "Designed Fiber Access Lines" = "darkorange")) +
  theme(axis.title.y = element_text(size = 6),
    axis.title = element_text(size = 12),
    axis.text.x = element_text(size = 9),
    axis.text.y = element_text(size = 9),
    plot.subtitle = element_text(size = 14),
    plot.title = element_text(size = 16, face = "bold"),
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)) + 
  annotation_scale(location = "bl", width_hint = 0.2) +
  coord_sf(crs = 4326)


#################
## PANEL PLOTS ##
#################
country_plots <- ggarrange(
  NGA_access_prims_fiber, NGA_access_pcsf_fiber,
  ETH_access_prims_fiber, ETH_access_pcsf_fiber,
  common.legend = TRUE, align = c('hv'),
  ncol = 2, nrow = 2, legend = 'bottom') 

path = file.path(folder, 'figures', 'country_plots.png')
png(path, units = "in", width = 8, height = 8, res = 300)
print(country_plots)
dev.off()







