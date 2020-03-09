#!/bin/bash

python3 files/tool_RetroPath2.py \
  -sinkfile input/Galaxy177-Sink_Compounds.csv \
  -sourcefile input/Galaxy160-Source.csv \
  -max_steps 3 \
  -rulesfile input/_exclude_rules.csv \
  -topx 100 \
  -dmin 0 \
  -dmax 1000 \
  -mwmax_source 1000 \
  -mwmax_cof 1000 \
  -timeout 30 \
  -scope_csv test_out_scope.csv \
  -is_forward False

mv test_out_scope.csv results/

# -sinkfile test_input_sink.dat \
# -sourcefile test_input_source.dat \
