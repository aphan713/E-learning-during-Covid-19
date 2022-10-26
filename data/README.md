# Datasets

## Primary Data Sources

### Currently Supported Data Sources

##### LearnPlatform

Download directly from [here](https://www.kaggle.com/competitions/learnplatform-covid19-impact-on-digital-learning/data) and unzip to ```\raw_data\LearnPlatform```

##### BroadbandNow

Download directly from [here](https://github.com/BroadbandNow/Open-Data) and drop the .csv in ```\raw_data\BroadbandNow```

### Adding New Data Sources

1. See ```\datasets\generic_dataset.py```. Make a copy of this file in ```\datasets``` and override the specified methods (see ```\datasets\BroadbandNow.py``` and ```\datasets\LearnPlatform.py``` for examples).
2. Update ```\datasets\__init__.py```, adding the name of your new dataset (_your new file and the dataset object within that file must have the same name, including capitalization!_). 

## Geographic Crosswalks

### Overview

Since the LearnPlatform data is only available at the (anonymized) school district level, we cannot directly map new data to our target data. 
Instead, we will estimate the district-level values of any new data by computing a state- and locale-level weighted average of a given value.

Weights are currently available for (see ```\alignment_data\_temp```):
- ZIP codes

(i.e., if you have data with ZIP code or state identifiers, the data loader in ```\dataset.py``` will be able to align it to the rest of the data)

Currently we are just computing crosswalk weights based on area, but we have the census data for a population-based weights, as well.

Also, it is worth noting that NCES actually classifies districts to a locale type according to the locale type that the enrollment-weighted _majority_ (or plurality, if no majority exists) of schools are located in within the district ([see section 4.4](https://files.eric.ed.gov/fulltext/ED577162.pdf)). It is therefore possible that a large number of students might actually live in different locales, even in the same district. 
Ideally each district could be weighted by how urban vs. rural it is, but in the absence of de-anonymized data, it is probably not possible to do this.

### Re-computing Alignment Data

Since the alignment process is computationally intensive and requires a lot of geographic data, re-compute it only when needed.

You will need to download the datasets described below and also install geopandas.

#### Data Sources

##### NCES EDGE Locale Data

Download directly from [here](https://nces.ed.gov/programs/edge/data/EDGE_Locale21_US.zip) and drag all data from the zip into ```\alignment_data\edge_locales```

##### NCES EDGE School Location Data

Download directly from [here](https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2021.zip) and drag all data from the ```Shapefile_SCH``` folder inside the zip into ```\alignment_data\edge_locations```

##### ZIP Code Tabulation Area Data

Download directly from [here](https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_2022_us_zcta520.zip) and drag all data from the zip into ```\alignment_data\zip_codes```

##### State Area Data

Download directly from [here](https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip) and drag all data from the zip into ```\alignment_data\states```

#### Census Tract Area Data

Download directly from [here](https://www2.census.gov/geo/tiger/TIGER2022/TRACT/) and drag all data into ```\alignment_data\census_tracts```

#### Census Tract Level Population Data

Download directly from [here](https://data.census.gov/cedsci/table?t=Population%20Total&g=0100000US%241400000&tid=ACSDT5Y2020.B01003) and drag all data from the zip into ```\alignment_data\census_tracts```

