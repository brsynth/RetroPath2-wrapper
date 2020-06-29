#!/bin/bash

python3 ../src/RetroPath2.py \
  -sinkfile in/Galaxy177-Sink_Compounds.csv \
  -sourcefile in/Galaxy160-Source.csv \
  -max_steps 3 \
  -rulesfile in/_exclude_rules.csv \
  -topx 100 \
  -dmin 0 \
  -dmax 1000 \
  -mwmax_source 1000 \
  -mwmax_cof 1000 \
  -timeout 30 \
  -outdir out \
  -is_forward False

  # -rulesfile in/empty_file.csv \
  # -rulesfile in/rules-d2.csv \
  # -rulesfile in/_exclude_rules.csv \
