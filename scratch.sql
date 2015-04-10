DROP TABLE IF EXISTS unitcounts_agg;
CREATE TABLE unitcounts_agg AS
SELECT
    bbl,
    date_part('year', "activityThrough") as year,
    MAX(units) as total_units
  FROM unitcounts
  GROUP BY bbl, date_part('year', "activityThrough");

DROP TABLE IF EXISTS unitcounts_agg_delta;
CREATE TABLE unitcounts_agg_delta AS
SELECT
    a.bbl,
    b.year,
    b.total_units - a.total_units delta_units
  FROM unitcounts_agg a
       JOIN unitcounts_agg b
  ON a.bbl = b.bbl AND
     a.year + 1 = b.year;

DROP TABLE IF EXISTS rs_counts_by_year;
CREATE TABLE rs_counts_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    bbl,
    year,
    delta_units
  FROM unitcounts_agg_delta
  ORDER BY 1, 2'
  ,$$VALUES
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2013'::text), ('2014'::text)$$)
AS ct ("bbl" bigint, "2010" int, "2011" int, "2012" int,
       "2013" int, "2014" int);

