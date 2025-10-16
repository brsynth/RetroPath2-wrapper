# Retropath2.0 Python wrapper

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/retropath2_wrapper/badges/version.svg)](https://anaconda.org/conda-forge/retropath2_wrapper) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/retropath2_wrapper/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/retropath2_wrapper)

Implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The tool expects the following files: `rules.csv`, `sink.csv` and `source.csv` and produces results in an output folder.

## Prerequisites

- Python 3
- KNIME (code was tested on `4.6.4`, `4.7.0` versions)

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
    )
```

Already installed KNIME app can hence be used that way, eg:

```python
from retropath2_wrapper import retropath2
from retropath2_wrapper.knime import Knime

knime = Knime(
    kinstall="/path/to/knime/directory",
    workflow="/path/to/workflow",
)
r_code = retropath2(
    sink_file='/path/to/sink/file',
    source_file='/path/to/source/file',
    rules_file='/path/to/rules/file',
    outdir='/path/to/outdir'
    knime=knime,
    )
```

Executions can be timed out using the `timeout` arguments (in minutes).

### Return codes

`retropath2()` function returns one of the following codes:

- 0: No error
- 1: File is not found
- 2: Running the RetroPath2.0 Knime program produced an OSError
- 3: InChI is malformated
- 4: Sink file is malformed
- 5: Knime installation returns an error
- 10: Source has been found in the sink (warning)
- 11: No solution is found (warning)

## Tests

Test can be run with the following commands:

### Natively

```sh
conda install -c conda-forge pytest
python -m pytest tests
```

To run functional tests, the environment variable `RP2_FUNCTIONAL=TRUE` is required.

### Knime dependencies

Available options:

1. You provide a path of the Knime root directory through the argument `--kinstall`. You need to have the following libraries installed: `org.knime.features.chem.types.feature.group`, `org.knime.features.datageneration.feature.group`, `org.knime.features.python.feature.group`, `org.rdkit.knime.feature.feature.group`
2. `retropath2_wrapper` will install Knime for you, at the root of the python package, by downloading the softwares available on Zenodo. You can choose a version among `4.6.4` or `4.7.0`. Optionally, you can locate a path for the installation. If an executable is found in the path, Knime will not be reinstalled.

```bash
python -m retropath2_wrapper.knime online \
    --kinstall "/path/to/knime/root/dir" \
    --kver {4.6.4,4.7.0}
```

Knime software and packages are available at:

- [KNIME](https://www.knime.com/)
- [KNIME v4.6.4 - Zenodo](https://zenodo.org/record/7515771)
- [KNIME v4.7.0 - Zenodo](https://zenodo.org/record/7564938)

All files from these repositories can be downloaded through the `Download all` button:

```bash
python -m retropath2_wrapper.knime local \
    --kinstall "/path/to/knime/root/dir" \
    --zenodo-zip "/path/to/7515771.zip"
```

## Known issues

1. Could not load native RDKit library, libfreetype.so.6: cannot open shared object file
   Some Knime versions (like: 4.3.0) or environments can't load RDKit library.
   You need to append the `$CONDA_PREFIX/lib` path to the `LD_LIBRARY_PATH` variable where the `libfreetype` library is available:

```sh
conda activate <env_name>
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CONDA_PREFIX/lib"
```

## CI/CD

For further tests and development tools, a CI toolkit is provided in `cicd-toolkit` folder (see [cicd-toolkit/README.md](cicd-toolit/README.md)).

### How to cite RetroPath2.0?

Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
