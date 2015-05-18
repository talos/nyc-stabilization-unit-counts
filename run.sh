#!/bin/bash -e

# 1-01244-0030
source .env/bin/activate
python download.py input/tenplusunits-after-1-01244-0030.csv >out.log 2>&1 &
