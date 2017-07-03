#!/bin/bash

source .env/bin/activate

export PGPASSWORD=docker4data
export PGUSER=postgres
export PGHOST=localhost
export PGPORT=54321
export PGDATABASE=postgres

psql -c 'drop table if exists rgb cascade;'
psql -c 'create table rgb (
         source VARCHAR,
         borough SMALLINT,
         year INT,
         add_421a INT,
         add_421g INT,
         add_420c INT,
         add_j51 INT,
         add_ML_buyout INT,
         add_loft INT,
         add_former_control REAL,
         sub_high_rent_income INT,
         sub_high_rent_vacancy INT,
         sub_coop_condo_conversion INT,
         sub_421a_expiration INT,
         sub_j51_expiration INT,
         sub_substantial_rehab INT,
         sub_commercial_prof_conversion INT,
         sub_other INT,
         total_sub INT,
         total_add REAL,
         inflated VARCHAR,
         net REAL
        );'
time cat data/rgb.csv | psql -c "COPY rgb FROM stdin WITH CSV HEADER NULL '' QUOTE'\"';"

time python parse.py data/ > data/rawdata.csv 2>data/rawdata.log # | psql -c "COPY rawdata FROM stdin WITH CSV HEADER NULL '' QUOTE '\"';"

psql -c 'drop table if exists rawdata cascade;'
psql -c 'create table rawdata (
         bbl bigint,
         activityThrough DATE,
         section TEXT,
         key TEXT,
         dueDate DATE,
         activityDate DATE,
         value TEXT,
         meta TEXT,
         apts TEXT
        );'
time psql -c "\\copy rawdata FROM 'data/rawdata.csv' WITH CSV HEADER NULL '' QUOTE '\"';"

