#!/bin/bash

outdir=$1

if [[ "$outdir" == "" ]]; then
  outdir="out/test"
fi

python3 ../src/RetroPath2.py \
  -sinkfile in/Galaxy177-Sink_Compounds.csv \
  -sourcefile in/Galaxy160-Source.csv \
  -max_steps 3 \
  -rulesfile in/empty_file.csv \
  -topx 100 \
  -dmin 0 \
  -dmax 1000 \
  -mwmax_source 1000 \
  -mwmax_cof 1000 \
  -timeout 30 \
  -outdir $outdir \
  -is_forward False

#mv test_out_scope.csv out/

# -sinkfile test_input_sink.dat \
# -sourcefile test_input_source.dat \
