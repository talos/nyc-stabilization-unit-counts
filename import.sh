#!/bin/bash -e

export PGPASSWORD=docker4data
export PGUSER=postgres
export PGHOST=localhost
export PGPORT=54321
export PGDATABASE=postgres

psql -f cross-tab-rs-counts.sql
