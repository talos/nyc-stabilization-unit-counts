-- DROP TABLE IF EXISTS unitcounts_agg;
-- CREATE TABLE unitcounts_agg AS
-- SELECT
--     bbl,
--     date_part('year', "activityThrough") as year,
--     MAX(units) as total_units
--   FROM unitcounts
--   GROUP BY bbl, date_part('year', "activityThrough");
-- 
-- DROP TABLE IF EXISTS unitcounts_agg_delta;
-- CREATE TABLE unitcounts_agg_delta AS
-- SELECT
--     a.bbl,
--     b.year,
--     b.total_units - a.total_units delta_units
--   FROM unitcounts_agg a
--        JOIN unitcounts_agg b
--   ON a.bbl = b.bbl AND
--      a.year + 1 = b.year;
-- 
-- DROP TABLE IF EXISTS rs_counts_by_year;
-- CREATE TABLE rs_counts_by_year AS
-- SELECT *
-- FROM crosstab(
--   'SELECT
--     bbl,
--     year,
--     delta_units
--   FROM unitcounts_agg_delta
--   ORDER BY 1, 2'
--   ,$$VALUES
--     ('2010'::text), ('2011'::text), ('2012'::text),
--     ('2013'::text), ('2014'::text)$$)
-- AS ct ("bbl" bigint, "2010" int, "2011" int, "2012" int,
--        "2013" int, "2014" int);
-- 

CREATE INDEX key on rawdata (key);
--CREATE INDEX key_activity_due on rawdata (key, "activitythrough", "duedate");
--CREATE INDEX bbl on rawdata (bbl);

CREATE TABLE unitcounts (
  bbl BIGINT,
  activitythrough DATE,
  duedate DATE,
  amount REAL,
  units INT,
  meta TEXT
);

INSERT INTO unitcounts
SELECT bbl, activitythrough, duedate, right(replace(value, ',', ''), -1)::real, apts, meta
FROM rawdata
WHERE key = 'Housing-Rent Stabilization';

CREATE TABLE registrations (
  regno TEXT,
  duedate DATE,
  bbls TEXT,
  numbbls INT,
  maxunits INT,
  diffunits INT,
  PRIMARY KEY (regno, duedate)
);

INSERT INTO registrations
SELECT meta, duedate, STRING_AGG(DISTINCT bbl::text, ', '), COUNT(DISTINCT bbl),
       MAX(units), COUNT(DISTINCT units)
FROM unitcounts
WHERE meta IS NOT NULL
GROUP BY meta, duedate
ORDER BY meta, duedate;

SELECT duedate, SUM(maxunits), COUNT(*)
FROM registrations
GROUP BY duedate
ORDER BY duedate;

--CREATE TEMP TABLE t AS 
--SELECT bbl,
--  activitythrough,
--  duedate,
--  MAX(value::int) as units
--FROM unitcounts
--WHERE units::int > 0
--GROUP BY
--  bbl,
--  year
--ORDER BY bbl, year;
--

-- INSERT INTO rawdata_dedup
-- SELECT distinct bbl, activitythrough, key, duedate, activitydate, value, meta
-- FROM rawdata;
-- ALTER TABLE rawdata_dedup RENAME TO rawdata;
