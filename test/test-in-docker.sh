#!/bin/bash

source ../custom/.env

cd docker
PACKAGE=$PACKAGE docker-compose build
PACKAGE=$PACKAGE docker-compose run --rm test
