# Datasets

## Primary Data Sources

### Currently Supported Data Sources

##### LearnPlatform

Download directly from [here](https://www.kaggle.com/competitions/learnplatform-covid19-impact-on-digital-learning/data) and unzip to ```\raw_data\LearnPlatform```

##### BroadbandNow

Download directly from [here](https://github.com/BroadbandNow/Open-Data) and drop the .csv in ```\raw_data\BroadbandNow```

##### Test Scores (Nation's Report Card)

Already downloaded from [here](https://www.nationsreportcard.gov/) and parsed/reformatted, can be found in ```\raw_data\NationsReportCard```

##### SAT Scores (Compiled by Anh)

Already downloaded from

- SAT (2019 and 2020): https://ipsr.ku.edu/ksdata/ksah/education/6ed16.pdf
- SAT (2022): https://blog.prepscholar.com/average-sat-scores-by-state-most-recent

and parsed/reformatted, can be found in ```\raw_data\SATScores```

### Adding New Data Sources

See ```Data Preprocessing.ipynb```. The BroadbandNow dataset is provided as an example - new datasets should be similar, assuming they are indexed at either the state or ZIP code level. If not, new geographic crosswalk weights will have to be defined.

Adding temporal datasets is a work-in-progress.

## Geographic Crosswalks

### Overview

Since the LearnPlatform data is only available at the (anonymized) school district level, we cannot directly map new data to our target data. 
Instead, we will estimate the district-level values of any new data by computing a state- and locale-level weighted average of a given value.

Weights are currently available for (see ```\alignment_data\weights```):
- ZIP codes
- States

(i.e., if you have data with ZIP code or state identifiers, the data loader in ```Data Preprocessing.ipynb``` will be able to align it to the rest of the data)

### Methodology

Currently we are just computing crosswalk weights based on area, but we have the census data for a population-based weights, as well (weights are already computed for census tract crosswalks with states and ZIP codes, which could be used to weight the crosswalk by _any_ census value).

This is done by merging all locale polygons at the state-level into one polygon (e.g., creating one big "Arizona City" polygon) to create a _target geography_, $T$. Then for each _source geography_, $S$, (e.g., ZIP code in Arizona), we compute two values (let $A(G)$ be the area of geography $G$):

$$FRACAREA\_TARGET(S, T) = \frac{A(S \cap T)}{A(T)}$$

(e.g., the fraction of the total "Arizona City" area taken up by the given ZIP code)

$$FRACAREA\_SOURCE(S, T) = \frac{A(S \cap T)}{A(S)}$$

(e.g., the fraction of the given ZIP code taken up by "Arizona City")

For now, we compute an estimated value $\tilde x$ for a particular locale in a particular state by:

$$\tilde x = \frac{\sum_{S} (FRACAREA\_TARGET(S, T) \times x)}{\sum_{S} FRACAREA\_TARGET(S, T))}$$

where $x$ is the value we seek to add to the dataset.

As noted, we also compute weights for census tracts that overlap the source geography. Each source geography gets a list of census tract IDs followed by target and source weights computed as above (i.e., given a tract, $C$, using $FRACAREA\_TARGET(C, S)$ and $FRACAREA\_SOURCE(C, S)$). We would then replace $FRACAREA\_TARGET(...)$ in the estimation for $\tilde x$ with weights computed using these census-to-source-geography crosswalk weights and our desired weighting value (e.g., population).

Also, it is worth noting that NCES actually classifies districts to a locale type according to the locale type that the enrollment-weighted _majority_ (or plurality, if no majority exists) of schools are located in within the district ([see section 4.4](https://files.eric.ed.gov/fulltext/ED577162.pdf)). It is therefore possible that a large number of students might actually live in different locales, even in the same district. 
Ideally each district could be weighted by how urban vs. rural it is, but in the absence of de-anonymized data, it is probably not possible to do this.

See https://fpeckert.me/eglp.pdf for additional information on geographic crosswalks.

### Re-computing Alignment Data

Since the alignment process is computationally intensive and requires a lot of geographic data, re-compute it only when needed.

You will need to download the datasets described below and also install geopandas.

#### Data Sources

##### NCES EDGE Locale Data

Download directly from [here](https://nces.ed.gov/programs/edge/data/EDGE_Locale21_US.zip) and drag all data from the zip into ```\alignment_data\edge_locales```

##### NCES EDGE School Location Data (NOT USED)

Download directly from [here](https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2021.zip) and drag all data from the ```Shapefile_SCH``` folder inside the zip into ```\alignment_data\edge_locations```

##### ZIP Code Tabulation Area Data

Download directly from [here](https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_2022_us_zcta520.zip) and drag all data from the zip into ```\alignment_data\zip_codes```

##### State Area Data

Download directly from [here](https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip) and drag all data from the zip into ```\alignment_data\states```

##### Census Tract Area Data

Download directly from [here](https://www2.census.gov/geo/tiger/TIGER2022/TRACT/) and drag all data into ```\alignment_data\census_tracts```

##### Census Tract Level Population Data (WILL BE USED FOR POPULATION-BASED WEIGHTS)

Download directly from [here](https://data.census.gov/cedsci/table?t=Population%20Total&g=0100000US%241400000&tid=ACSDT5Y2020.B01003) and drag all data from the zip into ```\alignment_data\census_tracts```

