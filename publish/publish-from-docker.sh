#!/bin/sh


function publish {
  cd $1
  $0
  cd -
}

if [ $# -eq 0 ]
then
  for manager in pypi conda
  do
    publish $manager
  done
else
  publish $1
fi
