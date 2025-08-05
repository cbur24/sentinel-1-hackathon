<img src="https://raw.githubusercontent.com/cbur24/sentinel-1-hackathon/blob/main/banner.png" width="900" alt="Digital Earth Australia logo" />

# Geoscience Australia's Sentinel-1 Hackathon

Info on the hackathon here

## Data availability

Geoscience Australia's Sentinel-1 data is published across multiple products, one for each polarisation mode used to capture the data.
You can see the distribution of captured data over time and space in the DEA Dev Explorer:
* [VV+VH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_iw_vv_vh_c0)
* [VV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_iw_vv_c0)
* [HH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_iw_hh_c0)

## Contributing notebooks

Info on how and where to push case-study notebooks during the hack.

## Example data loading

This repository provides examples for how to load data in two ways:
* Using DE's STAC API, which can be run on any computer.
* Using DE's dev Open Data Cube, which is only available in DE's Dev Sandbox environment. 

If you are not a Geoscience Australia employee, you will need to use the STAC API approach.

### STAC API

* [STAC-loading-notebook](notebooks/loading_with_stac.ipynb)

### DE's Dev Open Data Cube (via Dev Sandbox)

* [Datacube-loading-notebook](notebooks/loading_with_datacube.ipynb)

## Environment set up

### Cloning the repository
To access and run the iPython notebooks, you will need to clone this repository into your local computing environment, or the DE Dev Sandbox. 

In a terminal, navigate to where you wish to keep the repository and run
```
git clone https://github.com/cbur24/sentinel-1-hackathon.git
```

### Setting up the environment

If using DEA's Sandbox, no environment set up is required.

If using your own computer to run the STAC API notebook, you will need a Python environment with the required packages. 

You can follow the instructions in the [virtual_env_instructions](virtual_env_instructions.md) to set this up.
