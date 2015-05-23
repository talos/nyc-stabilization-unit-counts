-- For Quarterly Tax Bill PDFs
-- SELECT bbl,
--   YEAR(cast("activityThrough" as DATE)),
--   MAX(units)
-- FROM quarterly_tax_bills_pdfs
-- WHERE units > 0
-- GROUP BY
--   bbl,
--   YEAR(cast("activityThrough" as DATE))
-- ORDER BY bbl, "activityThrough";

-- no year function in postgres
CREATE TEMP TABLE t AS 
SELECT bbl,
  date_part('year', cast(activitythrough as DATE)) as year,
  MAX(units::int) as total_units
FROM unitcounts
WHERE units::int > 0
GROUP BY
  bbl,
  year
ORDER BY bbl, year;

-- crosstab query
-- note requires doing `CREATE EXTENSION tablefunc;`
CREATE EXTENSION tablefunc;
DROP TABLE IF EXISTS parsed;
CREATE TABLE parsed AS
SELECT * 
FROM crosstab(
  'SELECT bbl, year, total_units
  FROM t
  ORDER BY 1, 2'
  ,$$VALUES ('2008'::text), ('2009'::text), ('2010'::text), ('2011'::text), ('2012'::text), ('2013'::text), ('2014'::text), ('2015'::text)$$)
AS ct ("bbl" bigint, "2008" int, "2009" int, "2010" int, "2011" int, "2012" int, "2013" int, "2014" int, "2015" int);


/*
-- find out areas that had the most drastic change from 2009 - 2014
-- 2008 and 2015 have too many nulls
select *, "2009" - "2014" as net_change from 
rs_counts_by_year 
where "2009" is not null and "2014" is not null 
order by "2009" - "2014" DESC 
limit 200;

-- find the inverse
select *, "2014" - "2009" as net_change from 
rs_counts_by_year 
where "2009" is not null and "2014" is not null 
  order by "2014" - "2009" DESC 
  limit 200;

-- overall change in RS units: +718
select sum("2009" - "2014") as net_change
from rs_counts_by_year 
where "2009" is not null and "2014" is not null;

-- avg change`
select avg("2009" - "2014") as avg_change
from rs_counts_by_year 
where "2009" is not null and "2014" is not null;

-- create a column to store net change:
alter table rs_counts_by_year add column net_change_09_14 int;
update rs_counts_by_year set net_change = "2009" - "2014";
*/
