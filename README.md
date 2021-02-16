[![Build Status](https://travis-ci.com/KnutAM/cyclic_after_pdef_R260.svg?branch=main)](https://travis-ci.com/KnutAM/cyclic_after_pdef_R260)
[![Coverage Status](https://coveralls.io/repos/github/KnutAM/cyclic_after_pdef_R260/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/KnutAM/cyclic_after_pdef_R260?branch=main)
[![Documentation Status](https://readthedocs.org/projects/cyclic-after-pdef-r260/badge/?version=latest)](https://cyclic-after-pdef-r260.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Cyclic data analysis
Analysis and plotting of cyclic data after predeformation of R260 rail steel.

## Installation

### Using conda environment(recommended)

For this to work, you need to have conda install (e.g. by downloading anaconda). In order to work with this library, you should then do the following steps in cmd/shell (replace `<my_env>` with the environment name you wish to use.)

1. Create a new environment: `conda create -n <my_env>`  (Only required if you start with a fresh environment, but this is recommended in most cases)
2. Make the folder containing this readme file your current working directory
3. Activate your environment: `conda activate <my_env>`
4. Install pip with conda: `conda install pip`
5. Install this package: `pip install .`

After completing these steps, the modules in `cyclic_data` will be available for importing in python session using the environment `<my_env>`. 

### Install globally using pip (alternative)

In cmd or shell with the current working directory the same as for this readme: 

`pip install .`

## Data availability
Actual data is not part of the repository, but will be made available when the corresponding scientific publication has been peer-reviewed and accepted. 
