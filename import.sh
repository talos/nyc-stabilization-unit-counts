#!/bin/bash -e

export PGPASSWORD=docker4data
export PGUSER=postgres
export PGHOST=localhost
export PGPORT=54321
export PGDATABASE=postgres

# git clone https://github.com/clhenrick/dhcr-rent-stabilized-data.git
pushd ../dhcr-rent-stabilized-data
pgloader pgloader.load
popd

psql -f cross-tab-rs-counts.sql
