#!/bin/bash -e

# 1-01244-0030
source .env/bin/activate
python download.py input/unitsres6_9.txt >out.log 2>&1 &
