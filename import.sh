#!/bin/bash -e

createdb stabilization 2>/dev/null || :

# need to have pgloader installed
pgloader pgloader.load

psql -d stabilization -f cross-tab-rs-counts.sql
