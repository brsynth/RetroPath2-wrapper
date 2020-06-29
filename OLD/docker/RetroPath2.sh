#!/bin/bash

docker-compose run --rm -v $PWD:$PWD -w $PWD retropath2 python /home/src/RetroPath2.py $@
