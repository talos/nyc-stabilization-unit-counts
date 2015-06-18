#!/bin/bash

source .env/bin/activate
time python parse.py data/ >data/pdf-tax-bills.csv 2>data/pdf-tax-bills.log &
time python quarterly-statement-of-account-html/scrape.py data/ >data/html-statement-of-account.csv 2>data/html-statement-of-account.log  &
