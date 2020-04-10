# Retropath2.0 wrapper


Implementation of the KNIME retropath2.0 workflow. Takes for input the minimal (dmin) and maximal (dmax) diameter for the reaction rules and the maximal path length (maxSteps). The tool  expects the following files: `rules.csv`, `sink.csv` and `source.csv` and produces results in an output folder.

## Standalone

### Prerequisites

* Python 3

### Quick start
The main code is `src/RetroPath2.py` and can be run as the following:
```
python src/RetroPath2.py \
  -sinkfile <sink_file> \
  -sourcefile <source_file> \
  -max_steps 3 \
  -rulesfile <rules_file> \
  -topx 100 \
  -dmin 0 \
  -dmax 1000 \
  -mwmax_source 1000 \
  -mwmax_cof 1000 \
  -timeout 30 \
  -outdir <outdir_folder> \
  -is_forward False
```


## Docker

RetroPath2 can be run into a docker container.

### Prerequisites

* Docker - [Install](https://docs.docker.com/install/)

### Installation
Before running the container, the image has to be built with:
```
cd docker
docker-compose build
```

### Run
Then, the tool is runnable by:
```
cd docker
./RetroPath2.sh
  -sinkfile <sink_file> \
  -sourcefile <source_file> \
  -max_steps 3 \
  -rulesfile <rules_file> \
  -topx 100 \
  -dmin 0 \
  -dmax 1000 \
  -mwmax_source 1000 \
  -mwmax_cof 1000 \
  -timeout 30 \
  -outdir <outdir_folder> \
  -is_forward False
```

To call the tool with fresh code:
```
docker-compose run --rm -v <absolutepath_to_src>:/home/src retropath2
```

To call the tool from any location:
```
cd docker
docker-compose run --rm \
    -v <path/to/source.csv>:/home/source.csv:ro \
    -v <path/to/sink.csv>:/home/sink.csv:ro \
    -v <path/to/rules.csv>:/home/rules.csv:ro \
    -v <path/to/output_folder>:/home/outdir \
    -w /home \
    retropath2 python src/RetroPath2.py \
        -sinkfile <sink_file> \
        -sourcefile <source_file> \
        -max_steps 3 \
        -rulesfile <rules_file> \
        -topx 100 \
        -dmin 0 \
        -dmax 1000 \
        -mwmax_source 1000 \
        -mwmax_cof 1000 \
        -timeout 30 \
        -outdir <outdir_folder> \
        -is_forward False
```

## Test
All modes can be tested with:
```
cd test
./run[-in-docker].sh
```




### How to cite RetroPath2.0?
Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002
