# A global assessment of fixed broadband infrastructure (glassfibre)

## Paper Citation

Osoro, O. B., Oughton, E. J., & Kauker, F. (2024). Geospatial sustainability assessment of universal Fiber-To-The-Neighborhood (FTTnb) broadband infrastructure strategies for Sub-Saharan Africa. arXiv preprint arXiv:2411.18633. 

Even though fiber has been deployed in most parts of SSA, its installation is only justified in densely populated areas due to the high drilling and trenching costs. Notably, there are emerging innovative efforts to connect rural SSA but majority of the studies focuses on the technical aspects such as capacity. However, the deployment of innovative fiber broadband in SSA need to integrate the geographic location, population density of the targeted uncovered areas as a function of the cost and environmental impacts. A series of spatial optimization techniques can be used to optimally connect the unconnected rural population while reducing fixed, operational costs and carbon footprints. Against this background, we set to answer three important research questions as follows.

  1)	What is the best way to model fixed broadband networks to estimate their design and cost under different scenarios, using a globally generalizable method? 
  2)	How much investment is required in fixed broadband digital infrastructure to achieve affordable universal connectivity, for example, focusing on a fiber-to-the-neighborhood approach?
  3)	What is the quantity of emissions per user for different fiber network design options?



Methodology
==============
A general theoretical model for providing Fiber-to-the-Neighborhood (FTTnb) is now defined, consisting of demand, supply, and emissions components. 
In this model, we quantify the environmental carbon emissions and costs incurred in building a fiber network access node to the local area (neighborhood). 
An overview of the model is visualized in (see `Figure 1`). 

## Method Box

#### Figure 1 Proposed Method.
<p align="center">
  <img src="/docs/method_box.jpg" />
</p>

Results
=======
`Figure 2` shows the spatial distribution of the targeted population for fixed broadband service.
#### Figure 2 Demand Results.
<p align="center">
  <img src="/docs/population_point_demand_metrics.png" />
</p>

In `Figure 3`, a least-cost network design using Prize Collecting Steiner Tree (PCST) algorithm for routing fiber closer to settlement areas in SSA is shown.
#### Figure 3 Designed Least-Cost Network.
<p align="center">
  <img src = "/docs/pcst_fiber_network_design.png" />
</p>


## Install
```
conda create -n "glass" python=3.11
conda activate glass
python setup.py develop
```

## Run network solver

```
python src/glassfibre/pcst.py
```


## Required Data
[1]	Population Data. “Open Spatial Demographic Data and Research,” WorldPop. https://www.worldpop.org/ (accessed May 08, 2023).

[2]	Statistical Areas Data. GADM, “Global Administrative Areas Boundaries.” https://gadm.org/download_world.html (accessed Sep. 14, 2022).

[3] Country metadafile. Contained in `/data/countries.csv`

[4] Sub-Saharan Africa roads data.  Overture Maps Foundation, “Overture 2024-02-15-alpha.0 Release Notes,” 2024. Accessed: Apr. 17, 2024. [Online]. Available: https://overturemaps.org/download/ 

[5] Mobile Subscriber data. The World Bank Group, “Mobile Cellular Subscriptions,” World Bank Open Data. Accessed: Jan. 29, 2024. [Online]. Available: https://data.worldbank.org/indicator/IT.CEL.SETS

[6] Existing Fiber Networks Data for Sub-Saharan Africa. S. Song, “African Terrestrial Fibre Optic Cable Mapping Project,” Many Possibilities. Accessed: Feb. 11, 2024. [Online]. Available: https://manypossibilities.net/afterfibre/

[7] Cost of Electricity Data. “Household electricity prices worldwide in June 2024, by country,” Statista. Accessed: Feb. 21, 2025. [Online]. Available: https://www.statista.com/statistics/263492/electricity-prices-in-selected-countries/

[8] LCA Carbon Emission Factors. United Kingdom Government, “Government conversion factors for company reporting of greenhouse gas emissions,” Department of Business, Energy and Industrial Strategy, London, Jun. 2023. Accessed: Feb. 07, 2024. [Online]. Available: https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting
