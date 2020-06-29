# RetroRules

Retrieve the reaction rules from [RetroRules](https://retrorules.org/)

## Input

* **rule_type**: (string) Valid options: retro, forward, all. Return the rules that are in reverse, forward or both direction
* **out_folder**: (string) Specify the path where output files will be written
* **diameters**: (integer list): Valid options: 2, 4, 6, 8, 10, 12, 14, 16. The diameter of the rules to return

## Ouput

* **output**: (string): Path of the output file. Either a compressed TAR (containing a CSV) or CSV list of reaction rules that are in a RetroPath2.0 friendly format


## Install
### From pip
```sh
[sudo] python -m pip install retrorules
```
### From Conda
```sh
[sudo] conda install -c synbiocad retrorules
```


## Use
### Run from CLI
```sh
cd custom/src
python main.py \
  --rule_type {all,retro,forward} \
  --output <folder> \
  [--diameters {2,4,6,8,10,12,14,16}]
```

### Run in Docker
Local Docker images are built automatically if they do not exist yet. To (re-)build an image, please run the following:
```sh
cd <section_folder>/docker
PACKAGE=<YOUR_PACKAGE_NAME> docker-compose build
```
where `section_folder` can be `run`, `test` or `publish`.

Then, to instantiate the image into a container:
```sh
cd run
./run-in-docker.sh
```
where `output_folder` has to be an absolute path.

### Function call from Python code
```python
from retrorules import rules

outfile = rules(rule_type, out_folder, diameters)
```

If parameters from CLI have to be parsed, the function `build_parser` is available:
```python
from retrorules import build_parser

parser = buildparser()
params = parser.parse_args()
```

## Test
```sh
cd test
./test-in-docker.sh
```


## Publish
NOTE: to publish, credentials stored in secret files are needed.

### PyPi
To publish the package in PyPi:
```sh
cd publish/pypi
./publish-from-docker.sh
```

### Conda
To publish the package in Anaconda:
```sh
cd publish/pypi
./publish-from-docker.sh [PACKAGE_VERSION]
```


## Authors

* **Thomas Duigou**
* Melchior du Lac
* Joan Hérisson

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### How to cite RetroRules?
Please cite:

Duigou, Thomas, et al. "RetroRules: a database of reaction rules for engineering biology." Nucleic acids research 47.D1 (2019): D1229-D1235.
