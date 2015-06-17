#!/bin/bash -e

source .env/bin/activate
python download.py input/unitsres6_9.txt >out.log 2>&1 &
