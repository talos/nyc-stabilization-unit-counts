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
CREATE INDEX key on rawdata (key);
--CREATE INDEX key_activity_due on rawdata (key, "activitythrough", "duedate");
--CREATE INDEX bbl on rawdata (bbl);

DROP TABLE IF EXISTS unitcounts;
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

DROP TABLE IF EXISTS registrations;
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

--SELECT duedate, SUM(maxunits), COUNT(*)
--FROM registrations
--GROUP BY duedate
--ORDER BY duedate;


-- note requires doing `CREATE EXTENSION tablefunc;`
DROP TABLE IF EXISTS registrations_by_year;
CREATE TABLE registrations_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    regno,
    date_part(''year'', duedate),
    maxunits
  FROM registrations
  ORDER BY 1, 2'
  ,$$VALUES
    ('2007'::text), ('2008'::text), ('2009'::text),
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2015'::text)$$)
AS ct ("regno" text, "2007" int, "2008" int, "2009" int,
       "2010" int, "2011" int, "2012" int, "2015" int);

DROP TABLE IF EXISTS joined;
CREATE TABLE joined (
  bbl BIGINT,
  regno TEXT,
  "2007" INT,
  "2008" INT,
  "2009" INT,
  "2010" INT,
  "2011" INT,
  "2012" INT,
  "2015" INT,
  cd INTEGER,
  ct2010 TEXT,
  cb2010 TEXT,
  council INT,
  zipcode INTEGER,
  address TEXT,
  ownername TEXT,
  numbldgs INTEGER,
  numfloors REAL,
  unitsres INTEGER,
  unitstotal INTEGER,
  yearbuilt INTEGER,
  condono INTEGER,
  xcoord INTEGER,
  ycoord INTEGER
);
INSERT INTO joined
SELECT bbl, r.regno, "2007", "2008", "2009", "2010", "2011", "2012",
  "2015", cd, ct2010, cb2010, council, zipcode, address, ownername,
  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, xcoord, ycoord
FROM registrations_by_year rby
     JOIN registrations r ON rby.regno = r.regno
     JOIN nyc_pluto pl ON r.bbls = pl.bbl::text
GROUP BY bbl, r.regno, "2007", "2008", "2009", "2010", "2011", "2012",
  "2015", cd, ct2010, cb2010, council, zipcode, address, ownername,
  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, xcoord, ycoord
;


select zipcode, cd, sum("2007"), sum("2008"), sum("2009"), sum("2010"),
sum("2011"), sum("2012"), sum("2015"),
sum("2015") - sum("2007"),
(sum("2015") - sum("2007") * 1.0) / sum("2007")
from joined
where "2007" is not null and
 "2008" is not null and
 "2009" is not null and
 "2010" is not null and
 "2011" is not null and
 "2012" is not null and
 "2015" is not null
group by zipcode, cd
order by (sum("2015") - sum("2007") * 1.0) / sum("2007")
limit 20;

select bbl, sum("2007") "2007", sum("2008") "2008", sum("2009") "2009",
sum("2010") "2010", sum("2011") "2011", sum("2012") "2012", sum("2015") "2015"
from joined
where zipcode = '10469'
group by bbl
order by bbl;

select regno, bbl, "2007" "2007", "2008" "2008", "2009" "2009",
"2010" "2010", "2011" "2011", "2012" "2012", "2015" "2015"
from joined
where bbl = 2047130001;

select * from unitcounts where meta = '022638600';
