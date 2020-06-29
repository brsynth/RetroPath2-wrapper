#!/bin/sh

source ../../custom/.env

cd docker
PACKAGE=$PACKAGE VERSION=$1 docker-compose build
PACKAGE=$PACKAGE VERSION=$1 docker-compose run --rm publish
