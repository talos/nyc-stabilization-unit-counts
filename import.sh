#!/bin/bash -e

# createdb stabilization 2>/dev/null || :

export PGPASSWORD=docker4data
export PGUSER=postgres
export PGHOST=localhost
export PGPORT=54321
export PGDATABASE=postgres

# need to have pgloader installed
pgloader pgloader.load

psql -f cross-tab-rs-counts.sql
