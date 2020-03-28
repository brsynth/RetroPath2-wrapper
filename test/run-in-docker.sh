#!/bin/bash

cd ../docker
docker-compose run --rm -v $PWD/../test:/home/test -w /home/test --entrypoint="" retropath2 \
  sh -c "./run.sh out/test-in-docker"
cd -


# docker run \
#   -v $PWD/..:/home \
#   -w /home/test \
#   --rm brsynth/retropath2 \
# /bin/sh test-standalone.sh

#cp results/test_out_scope.csv .


# docker run \
#   -v ${PWD}/run.sh:/home/run.sh \
#   -v ${PWD}/tool_RetroPath2.py:/home/tool_RetroPath2.py \
#   -v ${PWD}/test_input_sink.dat:/home/test_input_sink.dat \
#   -v ${PWD}/test_input_source.dat:/home/test_input_source.dat \
#   -v ${PWD}/results/:/home/results/ \
#   --rm brsynth/retropath2 \
# /bin/sh /home/run.sh
