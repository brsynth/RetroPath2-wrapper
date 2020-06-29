#!/bin/bash

cd ../docker
docker-compose run --rm -v $PWD/../test:/home/test -w /home/test --entrypoint="" retropath2 \
  sh -c "./run.sh"
cd -
