#!/bin/bash


cd ../rest
./REST-server.sh start redis
cd -

sleep 5

docker run --rm \
  --link retropath2-rest:retropath \
  -v $PWD:/home \
  -w /home \
  --net retropath2 \
python:3 ./files/rest-query.sh


cd ../rest
./REST-server.sh stop
cd -
