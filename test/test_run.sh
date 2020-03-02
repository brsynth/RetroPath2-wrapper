#!/bin/bash

docker run -v ${PWD}/inside_run.sh:/home/inside_run.sh -v ${PWD}/tool_RetroPath2.py:/home/tool_RetroPath2.py -v ${PWD}/test_input_sink.dat:/home/test_input_sink.dat -v ${PWD}/test_input_source.dat:/home/test_input_source.dat -v ${PWD}/results/:/home/results/ --rm brsynth/retropath2-standalone /bin/sh /home/inside_run.sh

cp results/test_out_scope.csv .
