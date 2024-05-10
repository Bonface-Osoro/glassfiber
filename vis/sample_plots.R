library(ggpubr)
library(ggplot2)
library(dplyr)
library(tidyverse)
library("readxl")
library(ggtext)
library(sf)
library(ggspatial)
library(ggmap)
library(tidyr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
data <- read.csv(file.path(folder, '..', 'results', 'SSA', 'sample',
                            'djikstras_total_emission.csv'))