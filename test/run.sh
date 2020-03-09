#!/bin/bash

python3 tool_RetroPath2.py \
  -sinkfile Galaxy160-[Source].csv \
  -sourcefile Galaxy177-[Sink_Compounds].csv \
  -max_steps 3 \
  -rulesfile rules.csv \
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
