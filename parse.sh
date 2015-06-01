#!/bin/bash -e

source .env/bin/activate

pushd quarterly-property-tax-bills-pdf
nodejs run.js ../data/ > ../data/pdf-tax-bills.tmp.csv 2>../data/pdf-tax-bills.log &
popd

pushd quarterly-statement-of-account-html
python scrape.py ../data/ > ../data/html-statement-of-account.tmp.csv 2>../data/html-statement-of-account.log &
popd

wait
mv data/html-statement-of-account.tmp.csv data/html-statement-of-account.csv
mv data/pdf-tax-bills.tmp.csv data/pdf-tax-bills.csv
