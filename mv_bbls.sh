#!/bin/bash

# Move data in specified folder currently organized as Borough-Block-Lot to
# Borough/Block/Lot

for folder in $1/*-*-*; do
  bbl=$(basename $folder)
  borough=$(echo $bbl | cut -d '-' -f 1)
  block=$(echo $bbl | cut -d '-' -f 2)
  lot=$(echo $bbl | cut -d '-' -f 3)
  outdir=$1/$borough/$block/$lot
  mkdir -p $outdir
  mv $folder/* $outdir/
  rmdir $folder
  #echo $borough
  #echo $block
  #echo $lot
done
