# Retropath2.0 Python wrapper

[![Anaconda-Server Badge](https://anaconda.org/brsynth/retropath2_wrapper/badges/latest_release_date.svg)](https://anaconda.org/brsynth/retropath2_wrapper) [![Anaconda-Server Badge](https://anaconda.org/brsynth/retropath2_wrapper/badges/version.svg)](https://anaconda.org/brsynth/retropath2_wrapper)

Implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The tool  expects the following files: `rules.csv`, `sink.csv` and `source.csv` and produces results in an output folder.

## Prerequisites

* Python 3
* KNIME (code was tested on 4.3.0 version)

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
**From CLI**
```sh
python -m retropath2_wrapper <sinkfile> <sourcefile> <rulesfile> <outdir>
```
**From Python code**
```python
from retropath2_wrapper import retropath2, build_args_parser

parser = build_args_parser()
args   = parser.parse_args()

r_code = retropath2(
    args.sinkfile, args.sourcefile, args.rulesfile,
    args.outdir,
    args.kexec, not args.skip_kpkg_install, args.kver,
    args.kwf,
    args.max_steps, args.topx, args.dmin, args.dmax, args.mwmax_source, args.mwmax_cof,
    args.timeout,
    args.forward)
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
