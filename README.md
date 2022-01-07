# Retropath2.0 Python wrapper

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/retropath2_wrapper/badges/version.svg)](https://anaconda.org/conda-forge/retropath2_wrapper) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/retropath2_wrapper/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/retropath2_wrapper)

Implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The tool  expects the following files: `rules.csv`, `sink.csv` and `source.csv` and produces results in an output folder.

## Prerequisites

* Python 3
* KNIME (code was tested on 4.5.0 version)

## Install

### Prerequisite

The conda package manager is required. Fresh instructions on how to install conda are [available online](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

The tool tries to install the KNIME Anlytical Platform as well as the RetroPath2.0 node dependancies.

### conda package

Install in the `<my_env>` conda environment:
```shell
conda install -c conda-forge -n <my_env> retropath2_wrapper 
```

## Run

**Disclaimer**: we recommand to provide absolute path to files, problems can arise with relative paths.

### From CLI (Linux, macOS)
```sh
python -m retropath2_wrapper <sink-file> <rules-file> <out-dir> --source_file <source-file>
```

### From Python code

The minimal required arguments are `sink_file`, `source_file`, `rules_file` and `outdir`.
```python
from retropath2_wrapper import retropath2

r_code = retropath2(
    sink_file='/path/to/sink/file',
    source_file='/path/to/source/file',
    rules_file='/path/to/rules/file',
    outdir='/path/to/outdir'
    )
```

Exploration settings have default values and can be tuned:
```python
from retropath2_wrapper import retropath2

r_code = retropath2(
    sink_file='/path/to/sink/file',
    source_file='/path/to/source/file',
    rules_file='/path/to/rules/file',
    outdir='/path/to/outdir',
    max_steps=3,
    topx=100,
    dmin=0,
    dmax=100,
    mwmax_source=1000,
    mwmax_cof=1000,
    )
```

For convenience, the retropath2_wrapper make an attempt to install the KNIME application, and the needed KNIME dependancies. KNIME installation can be skipped by setting  `kexec` to the KNIME executable path, and KNIME dependancies can be skipped using `kpkg_install=False`.

Already installed KNIME app can hence be used that way, eg:
```python
from retropath2_wrapper import retropath2

r_code = retropath2(
    sink_file='/path/to/sink/file',
    source_file='/path/to/source/file',
    rules_file='/path/to/rules/file',
    outdir='/path/to/outdir'
    kexec='/Applications/KNIME 4.3.0.app/Contents/MacOS/knime',
    kpkg_install=False
    )
```

Executions can be timed out using the `timeout` arguments (in minutes).

### Return codes

`retropath2()` function returns one of the following codes:
* 0: `No error`
* 1: `Source has been found in the sink`
* 2: `Cannot find source-in-sink file`
* 3: `Running the RetroPath2.0 Knime program produced an OSError`
* 4: `RetroPath2.0 has found no solution`
* 5: `Time limit reached`


## Tests
Test can be run with the following commands:

### Natively
```sh
conda install -c conda-forge pytest
python -m pytest tests
```

# CI/CD
For further tests and development tools, a CI toolkit is provided in `cicd-toolkit` folder (see [cicd-toolkit/README.md](cicd-toolit/README.md)).


### How to cite RetroPath2.0?
Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
