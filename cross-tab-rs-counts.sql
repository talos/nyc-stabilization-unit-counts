CREATE INDEX key on rawdata (key);
--CREATE INDEX key_activity_due on rawdata (key, "activitythrough", "duedate");
--CREATE INDEX bbl on rawdata (bbl);

DROP TABLE IF EXISTS unitcounts;
CREATE TABLE unitcounts (
  bbl BIGINT,
  activitythrough DATE,
  duedate DATE,
  year INT,
  amount REAL,
  units INT,
  meta TEXT
);

INSERT INTO unitcounts
SELECT bbl,
  activitythrough,
  duedate,
  CASE
    WHEN duedate > '2012-04-01' THEN date_part('year', duedate) - 2
    ELSE date_part('year', duedate)
  END as year,
  right(replace(value, ',', ''), -1)::real, apts, meta
FROM rawdata
WHERE key = 'Housing-Rent Stabilization';

DROP TABLE IF EXISTS abatements;
CREATE TABLE abatements (
  bbl BIGINT,
  activitythrough DATE,
  abatement TEXT,
  cnt INT,
  PRIMARY KEY (bbl, activitythrough, abatement)
);
INSERT INTO abatements
SELECT bbl, activitythrough,
  CASE key
    WHEN 'SCRIE Rent Stabilization Abatement' THEN 'scrie'
    WHEN 'J51 Abatement' THEN 'j51'
    WHEN 'Coop Condo Abatement' THEN 'coco'
    WHEN 'Basic Star - School Tax Relief' THEN 'star'
    WHEN 'Basic STAR - School Tax Relief' THEN 'star'
    WHEN 'Drie Disability Rent Increase Abate' THEN 'drie'
    WHEN 'Senior Citizens Homeowners’ Exemption' THEN 'sche'
    WHEN 'J-51 Exemption' THEN 'j51'
    WHEN 'Veteran Exemption' THEN 'vet'
    WHEN 'Co-op Condo Abatement' THEN 'coco'
    WHEN 'Enhanced STAR - School Tax Relief' THEN 'estar'
    WHEN 'Co-op Condo Abatement 2013/14*' THEN 'coco'
    WHEN 'New Mult Dwellings - 421a' THEN '421a'
    WHEN 'J-51 Alteration' THEN 'j51'
    WHEN '421a (25 Yr Not Cap' THEN '421a'
    WHEN '420C Housing' THEN '420c'
    WHEN '421a (15 Yr Not Cap)' THEN '421a'
    WHEN 'New Mult Dwellings' THEN '421a'
  END as abatement,
  COUNT(*) as cnt
FROM rawdata
WHERE key in (
  'SCRIE Rent Stabilization Abatement',
  'J51 Abatement',
  'Coop Condo Abatement',
  'Basic Star - School Tax Relief',
  'Basic STAR - School Tax Relief',
  'Drie Disability Rent Increase Abate',
  'Senior Citizens Homeowners’ Exemption',
  'J-51 Exemption',
  'Veteran Exemption',
  'Co-op Condo Abatement',
  'Enhanced STAR - School Tax Relief',
  'Co-op Condo Abatement 2013/14*',
  'New Mult Dwellings - 421a',
  'J-51 Alteration',
  '421a (25 Yr Not Cap',
  '420C Housing',
  '421a (15 Yr Not Cap)',
  'New Mult Dwellings'
)
GROUP BY abatement, bbl, activitythrough
;

DROP TABLE IF EXISTS registrations;
CREATE TABLE registrations (
  regno TEXT,
  duedate DATE,
  ucyear INT,
  dhcryear INT,
  ucbbl BIGINT,
  dhcrbbl BIGINT,
  maxunits INT,
  diffunits INT,
  indhcr TEXT
);
INSERT INTO registrations
SELECT meta, duedate, MAX(uc.year), MAX(dh.year), uc.bbl, dh.bbl,
       MAX(units),
       COUNT(DISTINCT units),
       CASE
         WHEN MAX(uc.year) NOT IN (SELECT DISTINCT year FROM dhcrlist) THEN '?'
         WHEN MAX(dh.bbl) IS NOT NULL THEN 'Y'
         ELSE 'N'
       END as indhcr
FROM unitcounts uc FULL JOIN dhcrlist dh
ON
  (uc.bbl = dh.bbl AND uc.year = dh.year) --OR dh.bbl IS NULL OR uc.bbl IS NULL
GROUP BY meta, duedate, uc.bbl, dh.bbl
ORDER BY meta, duedate, uc.bbl, dh.bbl;
CREATE UNIQUE INDEX bbl_duedate ON registrations (ucbbl, dhcrbbl, regno, duedate);

-- note requires doing `CREATE EXTENSION tablefunc;`
DROP TABLE IF EXISTS registrations_by_year;
CREATE TABLE registrations_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    regno,
    ucbbl,
    ucyear,
    maxunits
  FROM registrations
  WHERE regno IS NOT NULL
  ORDER BY 1, 2, 3'
  ,$$VALUES
    ('2007'::text), ('2008'::text), ('2009'::text),
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2013'::text), ('2014'::text)$$)
AS ct ("regno" text, "ucbbl" BIGINT, "2007" int, "2008" int, "2009" int,
       "2010" int, "2011" int, "2012" int, "2013" int, "2014" int);

DROP TABLE IF EXISTS indhcr_by_year;
CREATE TABLE indhcr_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    regno,
    ucyear,
    indhcr
  FROM registrations
  WHERE regno IS NOT NULL
  ORDER BY 1, 2'
  ,$$VALUES
    ('2007'::text), ('2008'::text), ('2009'::text),
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2013'::text), ('2014'::text)$$)
AS ct ("regno" text, "2007" text, "2008" text, "2009" text,
       "2010" text, "2011" text, "2012" text, "2013" text, "2014" text);

DROP TABLE IF EXISTS abatements_by_year;
CREATE TABLE abatements_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    bbl,
    date_part(''year'', activitythrough) as year,
    string_agg(distinct abatement, '','')
  FROM abatements
  GROUP BY bbl, year
  ORDER BY 1, 2'
  ,$$VALUES
    ('2007'::text), ('2008'::text), ('2009'::text),
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2013'::text), ('2014'::text), ('2015'::text)$$)
AS ct ("bbl" bigint, "2007" text, "2008" text, "2009" text,
       "2010" text, "2011" text, "2012" text, "2013" text,
       "2014" text, "2015" text);



DROP TABLE IF EXISTS joined;
CREATE TABLE joined (
  borough TEXT,
  ucbbl BIGINT,
  regno TEXT,
  "2007uc" INT, "2007dhcr" TEXT, "2007abat" TEXT,
  "2008uc" INT, "2008dhcr" TEXT, "2008abat" TEXT,
  "2009uc" INT, "2009dhcr" TEXT, "2009abat" TEXT,
  "2010uc" INT, "2010dhcr" TEXT, "2010abat" TEXT,
  "2011uc" INT, "2011dhcr" TEXT, "2011abat" TEXT,
  "2012uc" INT, "2012dhcr" TEXT, "2012abat" TEXT,
  "2013uc" INT, "2013dhcr" TEXT, "2013abat" TEXT,
  "2014uc" INT, "2014dhcr" TEXT, "2014abat" TEXT,
  --"2015uc" INT, "2015dhcr" TEXT, "2015abat" TEXT,
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
SELECT boroughtext, ucbbl, rby.regno,
rby."2007", indy."2007", aby."2007",
rby."2008", indy."2008", aby."2008",
rby."2009", indy."2009", aby."2009",
rby."2010", indy."2010", aby."2010",
rby."2011", indy."2011", aby."2011",
rby."2012", indy."2012", aby."2012",
rby."2013", indy."2013", aby."2013",
rby."2014", indy."2014", aby."2014",
cd, ct2010, cb2010, council, zipcode, address, ownername,
  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, xcoord, ycoord
FROM registrations_by_year rby
     LEFT JOIN abatements_by_year aby ON rby.ucbbl = aby.bbl
     LEFT JOIN indhcr_by_year indy ON rby.regno = indy.regno
     LEFT JOIN nyc_pluto pl ON rby.ucbbl = pl.bbl
ORDER BY rby.ucbbl
;
--GROUP BY bbl, r.regno, "2007", "2008", "2009", "2010", "2011", "2012",
--  "2015", cd, ct2010, cb2010, council, zipcode, address, ownername,
--  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, xcoord, ycoord

\copy joined TO '/data/nyc-rent-stabilization-data/joined.csv' WITH CSV DELIMITER ',' HEADER

