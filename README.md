[![Build Status](https://travis-ci.com/KnutAM/cyclic_after_pdef_R260.svg?branch=main&kill_cache=1)](https://travis-ci.com/KnutAM/cyclic_after_pdef_R260)
[![Coverage Status](https://coveralls.io/repos/github/KnutAM/cyclic_after_pdef_R260/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/KnutAM/cyclic_after_pdef_R260?branch=main)
[![Documentation Status](https://readthedocs.org/projects/cyclic-after-pdef-r260/badge/?version=latest&kill_cache=1)](https://cyclic-after-pdef-r260.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Cyclic data analysis
Analysis and plotting of cyclic data biaxial (axial and torsional) mechanical testing data

## Installation

To clone (download) the repository using git

`git clone git@github.com:KnutAM/cyclic_after_pdef_R260.git`

Update the repository with `git pull` from inside the repository 

### Using conda environment(recommended)

For this to work, you need to have conda install (e.g. by downloading anaconda). In order to work with this library, you should then do the following steps in cmd/shell (replace `<my_env>` with the environment name you wish to use.)

1. Create a new environment: `conda create -n <my_env>`  (Only required if you start with a fresh environment, but this is recommended in most cases)
2. Make the folder containing this readme file your current working directory
3. Activate your environment: `conda activate <my_env>`
4. Install pip with conda: `conda install pip`
5. Install this package: `pip install .`

After completing these steps, the modules in `cyclic_data` will be available for importing in python session using the environment `<my_env>`. 

**Update package**: If new updates (obtained via `git pull`) are to be included, run `pip install .` from the same directory as this file, while having `<my_env>` as your active conda environment. 

### Install globally using pip (alternative)

In cmd or shell with the current working directory the same as for this readme: `pip install .`

**Update package**: The same procedure is used to update if updates via `git pull` have been obtained. 

## Data availability
Actual data is not part of the repository, but will be made available when the corresponding scientific publication has been peer-reviewed and accepted. 

## Running tests

The tests can be run from the top level directory by just running

``pytest`` 

However, to get the test coverage, run

``coverage run --source=cyclic_data -m pytest``

``coverage report``

