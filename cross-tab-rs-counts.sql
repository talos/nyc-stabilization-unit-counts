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

--INSERT INTO unitcounts
--SELECT bbl, activitythrough, duedate, right(replace(value, ',', ''), -1)::real, apts, meta
--FROM rawdata
--WHERE key = 'Housing-Rent Stabilization';
--
--DROP TABLE IF EXISTS abatements;
--CREATE TABLE abatements (
--  
--);
--INSERT INTO abatements
--SELECT *
--FROM rawdata
--WHERE key in ('J51 Abatement', 'SCRIE Rent Stabilization Abatement',
--  'Drie Disability Rent Increase Abate', 'Co-op Condo Abatement')

DROP TABLE IF EXISTS registrations;
CREATE TABLE registrations (
  regno TEXT,
  duedate DATE,
  bbls TEXT,
  numbbls INT,
  maxunits INT,
  diffunits INT,
  indhcr SMALLINT,
  PRIMARY KEY (regno, duedate)
);

INSERT INTO registrations
SELECT meta, duedate, STRING_AGG(DISTINCT uc.bbl::text, ', '), COUNT(DISTINCT uc.bbl),
       MAX(units), COUNT(DISTINCT units),
       CASE WHEN max(dh.bbl) IS NOT NULL THEN 1 ELSE 0 END
FROM unitcounts uc
     LEFT JOIN dhcrlist dh ON
        uc.bbl = dh.bbl AND date_part('year', duedate) = dh.year
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
  borough TEXT,
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
SELECT boroughtext, bbl, r.regno, "2007", "2008", "2009", "2010", "2011", "2012",
  "2015", cd, ct2010, cb2010, council, zipcode, address, ownername,
  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, xcoord, ycoord
FROM registrations_by_year rby
     JOIN registrations r ON rby.regno = r.regno
     JOIN nyc_pluto pl ON r.bbls = pl.bbl::text
GROUP BY bbl, r.regno, "2007", "2008", "2009", "2010", "2011", "2012",
  "2015", cd, ct2010, cb2010, council, zipcode, address, ownername,
  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, xcoord, ycoord
;

\copy joined TO '/data/nyc-rent-stabilization-data/joined.csv' WITH CSV DELIMITER ',' HEADER

