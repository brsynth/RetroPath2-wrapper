#!/bin/bash

source ../../custom/.env

docker save brsynth/$PACKAGE > $PACKAGE.tar

cd docker
PACKAGE=$PACKAGE docker-compose run --rm build
cd -

rm $PACKAGE.tar
