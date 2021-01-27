# Retropath2.0 Python wrapper

[![Anaconda-Server Badge](https://anaconda.org/brsynth/retropath2_wrapper/badges/latest_release_date.svg)](https://anaconda.org/brsynth/retropath2_wrapper) [![Anaconda-Server Badge](https://anaconda.org/brsynth/retropath2_wrapper/badges/version.svg)](https://anaconda.org/brsynth/retropath2_wrapper)

Implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The tool  expects the following files: `rules.csv`, `sink.csv` and `source.csv` and produces results in an output folder.

## Input

Required:
* **sink_file**: (string) Path to the collection of chemical species to finish metabolic route exploration
* **source_file**: (string) Path to the target compound desired to be synthesised
* **rules_file**: (string) Path to the reaction rules

Optional:
* **--outdir**: (string, default='out') Path to the folder where result files are written
* **--knime_exec**: (integer, default=9999) Path to Knime exec file
* **--max_steps** : (integer, default='3') Maximal number of steps
* **--topx** : (integer, default: 100) For each iteration, number of rules
* **--dmin** : (integer, default: 0)
* **--dmax** : (integer, default: 1000)
* **--mwmax_source** : (integer, default: 1000)
* **--mwmax_cof** : (integer, default: 1000)
* **--timeout** : (integer, default: 30) Timeout in minutes
* **--is_forward** : (bool, default: False) Forward or reverse synthesis


## Prerequisites

* Python 3
* KNIME (code was tested on 3.6.2 version)

## Install

### Prerequisite

The conda package manager is required. Fresh instructions on how to install conda are [available online](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).
The KNIME is installed 

### conda environment

In case a new conda environment `<my_env>` need to be set up, first start with:
```shell
conda create -n my_env python=3
```

### conda package

Install in the `<my_env>` conda environment:
```shell
conda install -c brsynth -c conda-forge -n <my_env> retropath2_wrapper 
```

## Run

### retropath2_wrapper process
**From Python code**
```python
from retropath2 import run, build_args_parser

parser = build_args_parser()
args  = parser.parse_args()

run(args.sinkfile,
    args.sourcefile,
    args.rulesfile)
```
**From CLI**
```sh
python -m retropath2 sinkfile.csv sourcefile.csv rulesfile.csv
```

## Tests
Test can be run with the following commands:

### Natively
```bash
cd tests
pytest -v
```

# CI/CD
For further tests and development tools, a CI toolkit is provided in `ci` folder (see [ci/README.md](ci/README.md)).


### How to cite RetroPath2.0?
Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
