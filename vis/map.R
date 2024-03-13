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

#####################
##SSA TCO Per User ##
#####################
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'SSA_baseline_tco_results.csv'))

data = data %>%
  distinct(iso3, tco_per_user, .keep_all = TRUE) %>%
  group_by(iso3) %>%
  summarize(tco_user = mean(tco_per_user))

merged_data <- merge(africa_shp, data, by = "iso3")

brewer_color_ramp <- colorRampPalette(brewer.pal(11, "Spectral"))
num_colors <- length(unique(merged_data$poor_pops))

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

###########################
##Emission per Subscriber##
###########################
tco_per_user <- create_sf_plot(
  data = merged_data,
  merged_data,
  fill_variable = "tco_user",
  legend_title = "Amount (US$ millions)",
  plot_title = "Total Cost of Ownership",
  plot_subtitle = 'Average TCO for Individual Countries.'
)


