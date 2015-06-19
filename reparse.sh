#!/bin/bash

source .env/bin/activate
time python parse.py data/ >data/rawdata.csv 2>data/rawdata.log &
