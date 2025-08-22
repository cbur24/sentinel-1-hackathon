<img src="banner.jpg" width="900" alt="banner image" />

# Geoscience Australia's Sentinel-1 Hackathon

This **Sentinel‑1 Hackathon** is a collaborative event bringing together Earth Observation scientists and developers from the Digital Earth teams (among others) to explore the power of **Synthetic Aperture Radar (SAR)** for remote sensing mapping applications. Over the course of this two-day hackathon, participants will deepen their skills in Sentinel‑1 theory and analysis, develop practical **use‑case notebooks**, prototype new Sentinel‑1–derived products, and showcase the impact of adding new satellite datasets to the **Digital Earth Australia/Antarctica** catalogues. This is an opportunity to experiment, share knowledge, and create tangible outputs that can guide future SAR‑based applications.

A number of resources and instruction have been written to help you get started, use the TOC below to find the resource you need. 

**Importantly**, at the bottom of this README is a table outlining potential [SAR use cases](#sar-use-cases), **please use this table to decide which project you would like to pursue**, and then use the link provided to assign yourself to a given project - a github projects board has been created to track assignments.

⚠️ **Please read through this README** before starting work to ensure you are aware of all available resources, and understand how to contribute to this repository.

## Table of Contents
- [Data availability](#data-availability)
- [Getting Started and python environment set up](#getting-started-and-python-environment-set-up)
  - [Cloning the repository](#cloning-the-repository)
  - [Setting up the environment](#setting-up-your-own-environment)
- [Contributing notebooks](#contributing-notebooks)
- [Example data loading](#example-data-loading)
  - [STAC API](#stac-api)
  - [DE's Dev Open Data Cube (via Dev Sandbox)](#des-dev-open-data-cube-via-dev-sandbox)
- [External resources](#external-resources)
  - [SAR theory](#sar-theory)
  - [Existing notebooks](#existing-notebooks)
- [SAR use cases](#sar-use-cases)

## Data availability

Geoscience Australia's Sentinel-1 data is published across multiple products, one for each polarisation mode used to capture the data.
You can see the distribution of captured data over time and space in the DEA Dev Explorer:
* [VV+VH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_iw_vv_vh_c0)
* [VV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_iw_vv_c0)
* [HH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_iw_hh_c0)

## Getting started and python environment set up
If using DEA's Sandbox, no environment set up is required. Though you will need to clone this repository into your Sandbox (see below).

🚀 If you prefer, you can also **launch a GitHub CodeSpace Visual Studio Code** instance by clicking the badge below. The session will contain all the necessary python libraries and the notebooks and code in this repo.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/cbur24/sentinel-1-hackathon?quickstart=1)

> [!TIP]
> Allow CodeSpaces a few minutes to bootup and for all python libraries to install. 
> To **open Jupyterlab** within the vscode session (if you perfer that IDE), in the terminal run `jupyter lab --no-browser --NotebookApp.token=''`, and jupyter lab will open in a seperate browser tab. Note, you may have to **disable any pop-up blockers** in your browser. Alternatively, you can configure your Github CodeSpaces settings to open Jupyterlab by default; go to [Editor preferences](https://github.com/settings/codespaces).

> [!WARNING]  
> When you open a Codespace, the compute time is billed to **your own GitHub account** (using your free monthly allowance or any paid plan you may have).
> [Free users](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) get 120 compute hours per month. The compute size set up for this repo is **4 cores, 16GB RAM, 15GB of storage.** On a free account, this means you have 30 free hours of usage per month.


To instead use your own environment, follow the instructions below.

### Cloning the repository
To access and run the iPython notebooks, you will need to clone this repository into your local computing environment, or the DEA Sandbox. 

In a terminal, navigate to where you wish to keep the repository and run

`git clone https://github.com/cbur24/sentinel-1-hackathon.git`

### Setting up your own environment

If using your own computer to run the STAC API notebook, you will need a Python environment with the required packages. 

You can follow the instructions in the [virtual_env_instructions](virtual_env_instructions.md) to set this up.

## Contributing notebooks

Use-case notebooks developed throughout this hackathon should be pushed into the `notebooks` folder within this repo. Create a folder with a simple name describing your project, and then push all notebooks, python scripts, and ancillary data into this folder. This will ensure your work does not clash with another group's project, thereby reducing the chances of git conflicts.  An example has been created under [notebooks/urban_classifier](notebooks/urban_classifier) to demonstrate the pattern.  

> ⚠️ Please use the [DEA-notebooks-template](notebooks/DEA_notebooks_template.ipynb) for creating use case examples, this will ensure less work is required to tidy up and document notebooks if/when it comes time to port them into the `dea-notebooks` repository.

## Example data loading

This repository provides examples for how to load data in two ways:
* Using DE's STAC API, which can be run on any computer.
* Using DE's dev Open Data Cube, which is only available in DE's Dev Sandbox environment. 

If you are not a Geoscience Australia employee, you will need to use the STAC API approach.

### STAC API

* [STAC-loading-notebook](notebooks/loading_with_stac.ipynb)

### DE's Dev Open Data Cube (via Dev Sandbox)

* [Datacube-loading-notebook](notebooks/loading_with_datacube.ipynb)

## External resources

### SAR theory
Links to lectures or other content explaining SAR principles.
* [Lecture series on SAR and its applications](https://radar.community.uaf.edu/module-1/#)
* [SAR-Training](https://github.com/ASFOpenSARlab/opensarlab-notebooks/tree/master/SAR_Training/English)

### Existing notebooks
These links direct to existing jupyter notebooks that use SAR data

* **Alaskan Satellite Facility (ASF)**
    * [OpenSARlab notebooks](https://github.com/ASFOpenSARlab/opensarlab-notebooks)
* **Digital Earth Africa**
    *  [Phenology using Radar Vegetation Index](https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Real_world_examples/Phenology_radar.ipynb)
    *  [Radar urban mapping](https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Real_world_examples/Radar_urban_area_mapping.ipynb)
    *  [Radar water extent](https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Real_world_examples/Radar_water_detection.ipynb)
    *  [Ship Detection](https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Real_world_examples/Ship_detection_with_radar.ipynb)
    *  [Surface miniing detection](https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Use_cases/Surface_mining_screening/Surface_mining_screening.ipynb)
    *  [Sentinel-1 monthly mosaics - datsets description notebook](https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Datasets/Sentinel_1_Mosaic.ipynb)
* **FrontierSI**:
    * [Coastline extraction with S1](https://github.com/frontiersi/DEAfrica_coastlines_s1)
* **ESA/Copernicus**
  * [LULC toolbox](https://step.esa.int/docs/tutorials/S1TBX%20Landcover%20classification%20with%20Sentinel-1%20GRD.pdf)
  * [Oil Spill mapping](https://documentation.dataspace.copernicus.eu/APIs/openEO/openeo-community-examples/python/OilSpill/OilSpillMapping.html)
  * [Radar Vegetation Index](https://documentation.dataspace.copernicus.eu/APIs/openEO/openeo-community-examples/python/RVI/RVI.html)
  * [ICE Monitoring](https://documentation.dataspace.copernicus.eu/notebook-samples/sentinelhub/ice_monitoring.html)
* **MS Planetary Computer**
  * [Flood mapping](https://github.com/microsoft/PlanetaryComputerExamples/blob/main/competitions/s1floods/benchmark_tutorial.ipynb)  

## SAR use cases

In the table below we list a number of potential SAR use cases. For the hackathon, you can assign yourself to one of these project ideas by clicking on the "assign youself" link below, which will take you to a github projects board where you can click on the corresponding card title and assign yourself within the pop-up box.

⚠️ [Assign yourself to a project idea](https://github.com/users/cbur24/projects/1/views/1)

| SAR data use | SAR requirements | Added value | Scientific maturity and suitability for operationalisation |
|--------------|------------------|-------------|------------------------------------------------------------|
| **Historical floodwater extent and depth** | Backscatter. VV + VH. C-band. L-band will provide under-canopy inundation. | Value added via observing through clouds and potential to produce a harmonised product. A historical product will inform community preparedness and hazard modelling. | Advanced. An operational dynamic surface water extent algorithm has been developed by NASA/ASF. It is intended to apply this at a 30 m resolution globally (including Aus) to Sentinel 1 A/B scenes. Many other scientific algorithms exist for flood mapping applications. <br>[DSWx Product Suite](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite) • [HydroSAR](https://github.com/HydroSAR/HydroSAR) • [NASA PROTEUS](https://github.com/nasa/PROTEUS) • [Opera DSWX-SAR](https://github.com/opera-adt/DSWX-SAR) |
| **Ground Displacement** <br>- Ground water <br>- Earthquakes <br>- Volcanic activity <br>- Landslides <br>- Mine displacement | InSAR, pixel offset tracking | Not hazards DEA has immediate interests in investigating. Geodesy team is piloting continental-scale ground line-of-sight displacement. The Community Safety Branch would be interested in earthquake impact tools and possibly landslides. | Advanced. Often requires scientific oversight. In the future the NISAR displacement product could be rolled out over Australia. <br>[DISP Product Suite](https://www.jpl.nasa.gov/go/opera/products/disp-product-suite) |
| **Coastal erosion / shoreline extraction** | Geo-located backscatter. HH is likely the best, and X-Band > L-Band > C-Band for detectability. C-band won’t detect inundation below canopies well. | Different overpass times allow observation of different tides vs optical. Combines sources to increase temporal resolution for models. Improved mapping in cloudy areas. Potential for tidal inundation detection under mangroves. Could remove tidal coverage bias in monsoon cloud areas. | Developed. Algorithms exist but need QC for speckle, rough seas, bright coastal targets. Validation with Landsat/Sentinel-2 needed. Problems may occur at low tide. Sub-aperture interferometric processing may detect waves and delineate shorelines. Wave conditions limits apply. <br>[Sentinel-1 algorithms](https://doi.org/10.3390/jmse11030627) • [Coastline extraction L-band](https://doi.org/10.1080/21664250.2019.1619252) • [Observation geometry L- & X-band](https://doi.org/10.1080/21664250.2018.1560685) |
| **Vegetation mapping and Land-Cover** | Dual-pol or quad-pol backscatter. C-band and L-band. InSAR (coherence) | SAR can determine woody from non-woody vegetation via double-bounce scattering. Coherence improves classification accuracy. | Developed. Proof-of-concepts in QLD show biomass-SAR relationships. More work needed for integration into classifiers. <br>[Multi-sensor classifier](https://doi.org/10.1016/j.jag.2020.102209) • [Structural classification](https://doi.org/10.3390/rs11020147) • [Crop mapping](https://doi.org/10.3390/rs13163300) |
| **Forest Stand Height** | InSAR (interferometry) | Provides age/history of forest, habitat info, biomass monitoring. Estimated by combining repeat-pass InSAR with DEM. | Developed. Applied to large-scale mosaics. <br>[Forest height mapping](http://dx.doi.org/10.3390/rs70505639) |
| **Flood mapping and wetlands** | Single-pol (HH) backscatter. C- and L-band. InSAR (coherence, interferometry) | Real-time mapping done by Community Safety Branch (ICEYE). Longer-term DEA monitoring possible. SAR backscatter can separate water and land; coherence helps map wetland vegetation. L-band penetrates canopy. | Developed. Used RADARSAT-2 for flood/wetland mapping. Challenges include coherence loss and atmospheric phase delay. <br>[Review paper](https://doi.org/10.1080/07038992.2018.1477680) |
| **Urban cover** | Dual-pol or quad-pol backscatter. C-band and L-band | Improves distinction between urban and bare land vs optical alone. Structural insights from polarimetry. | Developed. Many proofs-of-concept and global mapping efforts. <br>[SAR+Optical mapping](https://doi.org/10.1186/s40068-023-00324-5) • [Sentinel-1+2 workflow](https://doi.org/10.3390/rs14010036) • [OpenSARUrban dataset](https://doi.org/10.1109/JSTARS.2019.2954850) • [DEA Africa Notebook](https://docs.digitalearthafrica.org/en/latest/sandbox/notebooks/Real_world_examples/Radar_urban_area_mapping.html) |
| **Coastal habitat separation** | Backscatter, all polarisations C- and L-band. InSAR/Top-of-canopy DEM | Potential to distinguish saltmarsh, mangrove, supratidal habitats based on canopy height and backscatter. | Experimental. No established algorithm; NISAR quad-pol may help. Fusion with optical enhances results. <br>[Mangrove polarimetry](https://doi.org/10.3390/rs70708563) • [Inundated vegetation classification](https://doi.org/10.1016/j.rse.2021.112864) |
| **Historical burn area mapping** | Backscatter, VV + VH. C-band. L-band can observe under-canopy fires. | Detects burns under canopy, through clouds/smoke. Informs preparedness and hazard modelling. | Experimental. Difficult to map accurately at large scales; requires ML and change detection tuned to vegetation/landscape type. <br>[Burn area mapping](https://doi.org/10.1071/WF23124) |
| **Crop classification and yields** | Dual-pol or quad-pol backscatter + coherence. Time series/change detection. C-band | Could enhance DEA land-cover agriculture information. | Experimental. Successful in Wales (Sentinel-1) but coverage higher than Australia’s. <br>[Living Wales approach](https://doi.org/10.3390/rs13050846) |
| **Soil Moisture** | Backscatter and emissivity | No known DEA value add. | Operational product exists — ESA CCI daily active+passive SAR soil moisture product. <br>[ESA CCI Soil Moisture](https://climate.esa.int/en/projects/soil-moisture/) |
| **Ice shelf front, ice calving events and iceberg tracking** | Backscatter HH + HV | Cloud free and winter observations. | Advanced. An existing IceLines product exists. An events-based database and iceberg tracking could be built from this dataset. <br>[IceLines](https://doi.org/10.1038/s41597-023-02045-x) • [Iceberg Detection](https://doi.org/10.1016/j.isprsjprs.2020.12.006) • [Iceberg Tracking](https://doi.org/10.5194/tc-15-4727-2021) |
| **Ice Crevasse detection** | Backscatter HH | Can detect crevasses that may be hidden in optical imagery. | Advanced. Some limitations exist due to SAR image quality, observation geometry and terrain. <br>[Continental-scale algorithm](https://doi.org/10.3390/rs14030487) |
| **Snow classification (dry/wet/permafrost) and melting** | Backscatter, polarimetry | High resolution meltwater dynamics and freezing/thawing dynamics. | Advanced. <br>[Snow classification](https://doi.org/10.3390/rs9111171) • [Melt detection](https://doi.org/10.3390/w12092620) • [Melting algorithm](https://doi.org/10.1016/j.rse.2021.112318) |
| **High-resolution sea-ice concentration and extent** | Backscatter – all polarisations | Cloud-free, over winter high resolution sea-ice can provide more detailed observations that will benefit ocean modellers and Antarctic researchers. Information on types of sea-ice may also be distinguished. | Developed. Most sea-ice concentration algorithms have been developed using CNN or U-net. Cross-pol images can help classify types of sea-ice. Collaboration with sea-ice group would be required to produce an operational product. <br>[Denmark Antarctic Product](https://doi.org/10.48670/mds-00320) • [Baltic product](https://doi.org/10.1016/j.asr.2015.03.039) • [Sentinel-1 CNN](https://doi.org/10.3390/rs13091734) |
| **Meltwater and supra-glacial lakes** | InSAR, coherence, backscatter HH, VH | High-resolution data. Cloud-free and observations over winter. | Developed. PhD work ongoing at IMAS on supra-glacial lake collapse detection. InSAR more common in literature but harder to operationalise. <br>[Review](https://doi.org/10.1038/s43017-021-00246-9) • [S1+L8 method](https://doi.org/10.3389/feart.2017.00058) • [S1 neural network](https://doi.org/10.3390/rs13020197) |
| **Fast-ice extent** | InSAR, coherence, offset tracking backscatter HH, VH | Cloud-free and observations over winter. | Experimental. ARC Future Fellowship developing operational algorithm. <br>[InSAR fast-ice](https://doi.org/10.3390/rs10050720) • [Fast-ice monitoring](https://doi.org/10.5194/tc-13-557-2019) • [Displacement tracking](https://doi.org/10.3390/rs13183783) |
| **Grounding line** | InSAR | High-coverage repeat-pass motion detection to monitor change. | Experimental. Algorithm appears robust but dependent on observation geometry. <br>[Grounding line extraction](https://doi.org/10.1080/17538947.2023.2229785) |
| **Ice velocity and basal melt** | Backscatter offset tracking, InSAR, Multi-temporal DEM | Regional, high-quality InSAR products could provide additional value to existing products, in slow moving areas. | Operational product exists. ITS_LIVE provides continental-scale elevation change and ice velocity from offset tracking. InSAR robustness depends on observation/flow geometry; only valuable in slow areas <50 m/yr. Multiple Aperture InSAR may allow fast glacier measurement. <br>[ITS_LIVE](https://its-live.jpl.nasa.gov/) • [Ascending/Descending InSAR](https://doi.org/10.3390/rs9050442) |


