#!/bin/bash


source ../custom/.env
cd docker

if [[ $@ == *"--help"* ]]; then
  PACKAGE=$PACKAGE docker-compose run --rm run sh -c "python main.py --help"
  exit 0
fi

# while read -r -p "Sink file: " && [[ $REPLY != q ]]; do
#   case $REPLY in
#     "") ;;
#     *)
#       sinkfile=$REPLY
#       break;;
#   esac
# done
#
# while read -r -p "Source file: " && [[ $REPLY != q ]]; do
#   case $REPLY in
#     "") ;;
#     *)
#       sourcefile=$REPLY
#       break;;
#   esac
# done
#
# shopt -s extglob
# while read -r -p "Max steps [default=3]: " && [[ $REPLY != q ]]; do
#   case $REPLY in
#     "")
#       max_steps=3
#       break;;
#     +([1-9]))
#       max_steps=$REPLY
#       break;;
#     *) ;;
#   esac
# done
#
# while read -r -p "Rules file: " && [[ $REPLY != q ]]; do
#   case $REPLY in
#     "") ;;
#     *)
#       rulesfile=$REPLY
#       break;;
#   esac
# done
#
#
# while read -r -p "Output folder (relative) [default=./out]: " && [[ $REPLY != q ]]; do
#   case $REPLY in
#     "")
#       output_folder="$PWD/out"
#       break;;
#     ?*)
#       output_folder="$PWD/$REPLY"
#       break;;
#   esac
# done


#PACKAGE=$PACKAGE docker-compose build
PACKAGE=$PACKAGE docker-compose run --rm -v $PWD:$PWD -v $PWD/../../OLD:$PWD/../../OLD:ro -v $5:/out run sh -c "python main.py -sinkfile $1 -sourcefile $2 -max_steps $3 -rulesfile $4 -outdir $5"
