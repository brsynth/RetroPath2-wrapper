#!/bin/bash

source ../extras/.env

PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f check/docker/docker-compose.yml \
    --env-file check/docker/.env \
    build

# Pass the engine to be processed by check, if empty all modes will be processed
if [[ $# -eq 1 ]]; then
  mod=$1
else
  mod='flake bandit'
fi


PACKAGE=$PACKAGE \
HOMEDIR=$HOMEDIR \
docker-compose \
    -f check/docker/docker-compose.yml \
    --env-file check/docker/.env \
  run --rm \
  $mod
