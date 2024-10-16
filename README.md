# A global assessment of fixed broadband infrastructure (glassfibre)
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

In `Figure 3`, the quantitative emission results for different fiber network design approach is presented.
#### Figure 3 Emission Results.
<p align="center">
  <img src = "/docs/emissions.png" />
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
[1]	“Open Spatial Demographic Data and Research,” WorldPop. https://www.worldpop.org/ (accessed May 08, 2023).

[2]	GADM, “Global Administrative Areas Boundaries.” https://gadm.org/download_world.html (accessed Sep. 14, 2022).

[3] Country metadafile. Contained in `/data/countries.csv`
