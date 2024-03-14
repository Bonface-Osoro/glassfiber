library(ggpubr)
library(ggplot2)
library(tidyverse)
library(ggtext)
library(sf)
library(readr)
library(RColorBrewer)

suppressMessages(library(tidyverse))
folder <- dirname(rstudioapi::getSourceEditorContext()$path)

africa_data <- st_read(file.path(folder, '..', 'data', 'raw', 'Africa_Boundaries', 'SSA_combined_shapefile.shp'))
africa_shp <- africa_data %>%
  select(GID_0, NAME_0, GID_1, GID_2, geometry)

new_names <- c('iso3', 'country', 'gid_1', 'GID_2', 'geometry')
colnames(africa_shp) <- new_names

############
##SSA TCO ##
############
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_tco_results.csv'))

data = data %>%
  distinct(iso3, tco, .keep_all = TRUE) %>%
  group_by(iso3) %>%
  summarize(tco = (tco)/ 1e6)

merged_data <- merge(africa_shp, data, by = "iso3")

brewer_color_ramp <- colorRampPalette(brewer.pal(11, "Spectral"))
num_colors <- length(unique(merged_data$tco))

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

######################
##TCO per Subscriber##
######################
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
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_local_tco_results.csv'))

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
data <- data[data$strategy == "local", ]

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
  plot_subtitle = 'GHG emissions for each country due to construction of local fiber network.'
)

###################################
##SSA GHG Emission per subscriber##
##################################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_emission.csv'))
data <- data[data$strategy == "local", ]

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
  plot_subtitle = 'GHG emissions per user for each country due to construction of local fiber network.'
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
