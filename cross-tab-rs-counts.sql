UPDATE rawdata SET key = LOWER(key);
CREATE INDEX key on rawdata (key);
--CREATE INDEX key_activity_due on rawdata (key, "activitythrough", "duedate");
--CREATE INDEX bbl on rawdata (bbl);

DROP TABLE IF EXISTS unitcounts;
CREATE TABLE unitcounts (
  bbl BIGINT,
  activitythrough DATE,
  duedate DATE,
  year INT,
  amount MONEY,
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
  value::money, apts::int, meta
FROM rawdata
WHERE key = 'housing-rent stabilization';

UPDATE unitcounts
SET units = (amount / 10)::numeric
WHERE meta !~ '^[\d ]+$';

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
    WHEN 'scrie rent stabilization abatement' THEN 'scrie'
    WHEN 'j51 abatement' THEN 'j51'
    WHEN 'coop condo abatement' THEN 'coco'
    WHEN 'basic star - school tax relief' THEN 'star'
    WHEN 'basic star - school tax relief' THEN 'star'
    WHEN 'drie disability rent increase abate' THEN 'drie'
    WHEN 'senior citizens homeowners’ exemption' THEN 'sche'
    WHEN 'j-51 exemption' THEN 'j51'
    WHEN 'veteran exemption' THEN 'vet'
    WHEN 'co-op condo abatement' THEN 'coco'
    WHEN 'enhanced star - school tax relief' THEN 'estar'
    WHEN 'co-op condo abatement 2013/14*' THEN 'coco'
    WHEN 'new mult dwellings - 421a' THEN '421a'
    WHEN 'j-51 alteration' THEN 'j51'
    WHEN '421a (25 yr not cap' THEN '421a'
    WHEN '420c housing' THEN '420c'
    WHEN '421a (15 yr not cap)' THEN '421a'
    WHEN 'new mult dwellings' THEN '421a'
    WHEN '421a (10 yr cap)' THEN '421a'
    WHEN '421a (20 yr not cap' THEN '421a'
  END as abatement,
  COUNT(*) as cnt
FROM rawdata
WHERE key in (
  'scrie rent stabilization abatement',
  'j51 abatement',
  'coop condo abatement',
  'basic star - school tax relief',
  'basic star - school tax relief',
  'drie disability rent increase abate',
  'senior citizens homeowners’ exemption',
  'j-51 exemption',
  'veteran exemption',
  'co-op condo abatement',
  'enhanced star - school tax relief',
  'co-op condo abatement 2013/14*',
  'new mult dwellings - 421a',
  'j-51 alteration',
  '421a (25 yr not cap',
  '420c housing',
  '421a (15 yr not cap)',
  'new mult dwellings',
  '421a (10 yr cap)',
  '421a (20 yr not cap'
)
GROUP BY abatement, bbl, activitythrough
;

DROP TABLE IF EXISTS owners;
CREATE UNLOGGED TABLE owners AS
SELECT bbl, DATE_PART('year', activitythrough)::INT AS year, MAX(value) AS owner
FROM rawdata
WHERE key = 'owner name'
GROUP BY bbl, DATE_PART('year', activitythrough);
CREATE UNIQUE INDEX owners_uk on owners (bbl, year);

DROP TABLE IF EXISTS addresses;
CREATE UNLOGGED TABLE addresses AS
SELECT bbl, DATE_PART('year', activitythrough)::INT AS year, MAX(value) AS address
FROM rawdata
WHERE key =  'mailing address'
GROUP BY bbl, DATE_PART('year', activitythrough)::INT;
CREATE UNIQUE INDEX "addresses_uk" on addresses (bbl, year);

DROP TABLE IF EXISTS owner_addresses;
CREATE TABLE owner_addresses AS
SELECT o.bbl, o.year, o.owner, a.address
FROM owners o, addresses a
WHERE o.bbl = a.bbl AND o.year = a.year;

DROP TABLE owners;
DROP TABLE addresses;

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
CREATE EXTENSION tablefunc;
DROP TABLE IF EXISTS registrations_by_year;
CREATE TABLE registrations_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    ucbbl,
    ucyear,
    SUM(maxunits)
  FROM registrations
  WHERE regno IS NOT NULL
  GROUP BY ucbbl, ucyear
  ORDER BY 1, 2, 3'
  ,$$VALUES
    ('2007'::text), ('2008'::text), ('2009'::text),
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2013'::text), ('2014'::text)$$)
AS ct ("ucbbl" BIGINT, "2007" int, "2008" int, "2009" int,
       "2010" int, "2011" int, "2012" int, "2013" int, "2014" int);

DROP TABLE IF EXISTS indhcr_by_year;
CREATE TABLE indhcr_by_year AS
SELECT *
FROM crosstab(
  'SELECT
    dhcrbbl,
    dhcryear,
    MAX(indhcr)
  FROM registrations
  GROUP BY dhcrbbl, dhcryear
  ORDER BY 1, 2'
  ,$$VALUES
    ('2007'::text), ('2008'::text), ('2009'::text),
    ('2010'::text), ('2011'::text), ('2012'::text),
    ('2013'::text), ('2014'::text)$$)
AS ct ("dhcrbbl" BIGINT, "2007" text, "2008" text, "2009" text,
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
  "2007uc" INT, "2007est" TEXT, "2007dhcr" TEXT, "2007abat" TEXT,
  "2008uc" INT, "2008est" TEXT, "2008dhcr" TEXT, "2008abat" TEXT,
  "2009uc" INT, "2009est" TEXT, "2009dhcr" TEXT, "2009abat" TEXT,
  "2010uc" INT, "2010est" TEXT, "2010dhcr" TEXT, "2010abat" TEXT,
  "2011uc" INT, "2011est" TEXT, "2011dhcr" TEXT, "2011abat" TEXT,
  "2012uc" INT, "2012est" TEXT, "2012dhcr" TEXT, "2012abat" TEXT,
  "2013uc" INT, "2013est" TEXT, "2013dhcr" TEXT, "2013abat" TEXT,
  "2014uc" INT, "2014est" TEXT, "2014dhcr" TEXT, "2014abat" TEXT,
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
  lon REAL,
  lat REAL
);
INSERT INTO joined
SELECT boroughtext, ucbbl,
rby."2007", 'N', indy."2007", aby."2007",
rby."2008", 'N', indy."2008", aby."2008",
rby."2009", 'N', indy."2009", aby."2009",
rby."2010", 'N', indy."2010", aby."2010",
rby."2011", 'N', indy."2011", aby."2011",
rby."2012", 'N', indy."2012", aby."2012",
rby."2013", 'N', indy."2013", aby."2013",
rby."2014", 'N', indy."2014", aby."2014",
cd, ct2010, cb2010, council, zipcode, address, ownername,
  numbldgs, numfloors, unitsres, unitstotal, yearbuilt, condono, ST_X(geom), ST_Y(geom)
FROM registrations_by_year rby
     LEFT JOIN abatements_by_year aby ON rby.ucbbl = aby.bbl
     LEFT JOIN indhcr_by_year indy ON rby.ucbbl = indy.dhcrbbl
     LEFT JOIN "contrib/us/ny/nyc".pluto pl ON rby.ucbbl = pl.bbl
ORDER BY rby.ucbbl
;

/* TODO below -- very liberal with 07/08 fillins because we lack abatement
 * info. */
/* backfill from beginning to end. */
UPDATE joined SET "2008uc" = "2007uc", "2008est" = 'Y' WHERE "2008uc" IS NULL AND "2007uc" IS NOT NULL;
UPDATE joined SET "2009uc" = "2009uc", "2009est" = 'Y' WHERE "2009uc" IS NULL AND "2008uc" IS NOT NULL AND ("2009abat" = "2009abat" OR "2009abat" LIKE '%SCRIE%' OR "2009abat" LIKE '%DRIE%' OR "2009dhcr" = 'Y');
UPDATE joined SET "2010uc" = "2009uc", "2010est" = 'Y' WHERE "2010uc" IS NULL AND "2009uc" IS NOT NULL AND ("2009abat" = "2010abat" OR "2010abat" LIKE '%SCRIE%' OR "2010abat" LIKE '%DRIE%' OR "2010dhcr" = 'Y');
UPDATE joined SET "2011uc" = "2010uc", "2011est" = 'Y' WHERE "2011uc" IS NULL AND "2010uc" IS NOT NULL AND ("2010abat" = "2011abat" OR "2011abat" LIKE '%SCRIE%' OR "2011abat" LIKE '%DRIE%' OR "2011dhcr" = 'Y');
UPDATE joined SET "2012uc" = "2011uc", "2012est" = 'Y' WHERE "2012uc" IS NULL AND "2011uc" IS NOT NULL AND ("2011abat" = "2012abat" OR "2012abat" LIKE '%SCRIE%' OR "2012abat" LIKE '%DRIE%' OR "2012dhcr" = 'Y');
UPDATE joined SET "2013uc" = "2012uc", "2013est" = 'Y' WHERE "2013uc" IS NULL AND "2012uc" IS NOT NULL AND ("2012abat" = "2013abat" OR "2013abat" LIKE '%SCRIE%' OR "2013abat" LIKE '%DRIE%' OR "2013dhcr" = 'Y');
UPDATE joined SET "2014uc" = "2013uc", "2014est" = 'Y' WHERE "2014uc" IS NULL AND "2013uc" IS NOT NULL AND ("2013abat" = "2014abat" OR "2014abat" LIKE '%SCRIE%' OR "2014abat" LIKE '%DRIE%' OR "2014dhcr" = 'Y');

/* backfill from end to beginning, if abatements are unchanged. */
UPDATE joined SET "2013uc" = "2014uc", "2013est" = 'Y' WHERE "2013uc" IS NULL AND "2014uc" IS NOT NULL AND ("2013abat" = "2014abat" OR "2013abat" LIKE '%SCRIE%' OR "2013abat" LIKE '%DRIE%' OR "2013dhcr" = 'Y');
UPDATE joined SET "2012uc" = "2013uc", "2012est" = 'Y' WHERE "2012uc" IS NULL AND "2013uc" IS NOT NULL AND ("2012abat" = "2013abat" OR "2012abat" LIKE '%SCRIE%' OR "2012abat" LIKE '%DRIE%' OR "2012dhcr" = 'Y');
UPDATE joined SET "2011uc" = "2012uc", "2011est" = 'Y' WHERE "2011uc" IS NULL AND "2012uc" IS NOT NULL AND ("2011abat" = "2012abat" OR "2011abat" LIKE '%SCRIE%' OR "2011abat" LIKE '%DRIE%' OR "2011dhcr" = 'Y');
UPDATE joined SET "2010uc" = "2011uc", "2010est" = 'Y' WHERE "2010uc" IS NULL AND "2011uc" IS NOT NULL AND ("2010abat" = "2011abat" OR "2010abat" LIKE '%SCRIE%' OR "2010abat" LIKE '%DRIE%' OR "2010dhcr" = 'Y');
UPDATE joined SET "2009uc" = "2010uc", "2009est" = 'Y' WHERE "2009uc" IS NULL AND "2010uc" IS NOT NULL AND ("2009abat" = "2010abat" OR "2009abat" LIKE '%SCRIE%' OR "2009abat" LIKE '%DRIE%' OR "2009dhcr" = 'Y');
UPDATE joined SET "2008uc" = "2009uc", "2008est" = 'Y' WHERE "2008uc" IS NULL AND "2009uc" IS NOT NULL;
UPDATE joined SET "2007uc" = "2008uc", "2007est" = 'Y' WHERE "2007uc" IS NULL AND "2008uc" IS NOT NULL;

DROP TABLE IF EXISTS joined_nocrosstab;
CREATE TABLE joined_nocrosstab (
  ucbbl BIGINT,
  year DATE,
  unitcount INT,
  estimate TEXT,
  indhcr TEXT,
  abatements TEXT,
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
  lon REAL,
  lat REAL
);

INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2007-01-01', "2007uc", "2007est", "2007dhcr", "2007abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2008-01-01', "2008uc", "2008est", "2008dhcr", "2008abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2009-01-01', "2009uc", "2009est", "2009dhcr", "2009abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2010-01-01', "2010uc", "2010est", "2010dhcr", "2010abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2011-01-01', "2011uc", "2011est", "2011dhcr", "2011abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2012-01-01', "2012uc", "2012est", "2012dhcr", "2012abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2013-01-01', "2013uc", "2013est", "2013dhcr", "2013abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;
INSERT INTO joined_nocrosstab
  SELECT ucbbl, '2014-01-01', "2014uc", "2014est", "2014dhcr", "2014abat", cd, ct2010,
  cb2010, council, zipcode, address, ownername, numbldgs, numfloors, unitsres,
  unitstotal, yearbuilt, condono, lon, lat FROM joined;

DROP TABLE IF EXISTS changes_summary;
CREATE TABLE changes_summary (
  ucbbl BIGINT,
  unitstotal INTEGER,
  unitsstab2007 INTEGER,
  unitsstab2014 INTEGER,
  diff INT,
  percentchange TEXT,
  j51 text,
  "421a" text,
  scrie text,
  drie text,
  "420c" text,
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
  unitstotalpluto INTEGER,
  yearbuilt INTEGER,
  condono INTEGER,
  lon REAL,
  lat REAL
);

INSERT INTO changes_summary
SELECT
  ucbbl,
  MAX(GREATEST(unitsres, unitstotal, unitcount, 1)) AS unitstotal,
  MAX(CASE year WHEN '2007-01-01' THEN unitcount ELSE 0 END) AS unitsstab2007,
  MAX(CASE year WHEN '2014-01-01' THEN unitcount ELSE 0 END) AS unitsstab2014,
  MAX(CASE year WHEN '2014-01-01' THEN unitcount ELSE 0 END) -
  MAX(CASE year WHEN '2007-01-01' THEN unitcount ELSE 0 END) AS diff,
  TO_CHAR((MAX(CASE year WHEN '2014-01-01' THEN unitcount ELSE 0 END) -
  MAX(CASE year WHEN '2007-01-01' THEN unitcount ELSE 0 END))::real / MAX(
    GREATEST(unitsres, unitstotal, unitcount, 1)) * 100, '999D99')::real AS percentchange,
  MIN(CASE WHEN abatements ILIKE '%j51%' THEN DATE_PART('year', year) ELSE NULL END)::text || ' - ' ||
    MAX(CASE WHEN abatements ILIKE '%j51%' THEN DATE_PART('year', year) ELSE NULL END)::text AS "j51" ,
  MIN(CASE WHEN abatements ILIKE '%421a%' THEN DATE_PART('year', year) ELSE NULL END)::text || ' - ' ||
    MAX(CASE WHEN abatements ILIKE '%421a%' THEN DATE_PART('year', year) ELSE NULL END)::text AS "421a" ,
  MIN(CASE WHEN abatements ILIKE '%scrie%' THEN DATE_PART('year', year) ELSE NULL END)::text || ' - ' ||
    MAX(CASE WHEN abatements ILIKE '%scrie%' THEN DATE_PART('year', year) ELSE NULL END)::text AS "scrie" ,
  MIN(CASE WHEN abatements ILIKE '%drie%' THEN DATE_PART('year', year) ELSE NULL END)::text || ' - ' ||
    MAX(CASE WHEN abatements ILIKE '%drie%' THEN DATE_PART('year', year) ELSE NULL END)::text AS "drie" ,
  MIN(CASE WHEN abatements ILIKE '%420c%' THEN DATE_PART('year', year) ELSE NULL END)::text || ' - ' ||
    MAX(CASE WHEN abatements ILIKE '%420c%' THEN DATE_PART('year', year) ELSE NULL END)::text AS "420c" ,
  MAX(cd), MAX(ct2010), MAX(cb2010), MAX(council), MAX(zipcode), MAX(address), MAX(ownername),
  MAX(numbldgs), MAX(numfloors), MAX(unitsres), MAX(unitstotal), MAX(yearbuilt), MAX(condono), MAX(lon), MAX(lat)
FROM joined_nocrosstab
GROUP BY ucbbl;

DROP TABLE IF EXISTS rgb_comparison;
CREATE TABLE rgb_comparison AS
SELECT
  DATE_PART('year', latter.year) AS year,
  former.ucbbl/1000000000 AS borough,
  SUM(latter.unitcount - former.unitcount) AS dof_diff,
  0 AS rgb_diff,
  0 AS diff_diff,
  SUM(CASE WHEN former.unitcount > latter.unitcount THEN latter.unitcount - former.unitcount ELSE 0 END) AS dof_loss,
  0 AS rgb_loss,
  0 AS diff_loss,
  SUM(CASE WHEN former.unitcount < latter.unitcount THEN latter.unitcount - former.unitcount ELSE 0 END) AS dof_gain,
  0 AS rgb_gain,
  0 AS diff_gain
FROM joined_nocrosstab former, joined_nocrosstab latter
  WHERE former.ucbbl = latter.ucbbl AND
        former.year = latter.year - '1 year'::interval
GROUP BY former.ucbbl/1000000000, latter.year
ORDER BY former.ucbbl/1000000000, latter.year;

UPDATE rgb_comparison comp
SET rgb_diff = rgb.net,
    rgb_loss = rgb.total_sub,
    rgb_gain = rgb.total_add,
    diff_diff = dof_diff - rgb.net,
    diff_loss = dof_loss - rgb.total_sub,
    diff_gain = dof_gain - rgb.total_add
FROM rgb WHERE comp.year = rgb.year
     AND comp.borough = rgb.borough;

SELECT * FROM rgb_comparison order by borough, year;
SELECT borough,
  sum(dof_diff) as dof_diff,
  sum(rgb_diff) as rgb_diff,
  sum(diff_diff) as diff_diff,
  sum(dof_loss) as dof_loss,
  sum(rgb_loss) as rgb_loss,
  sum(diff_loss) as diff_loss,
  sum(dof_gain) as dof_gain,
  sum(rgb_gain) as rgb_gain,
  sum(diff_gain) as diff_gain
FROM rgb_comparison
GROUP BY borough
ORDER BY borough;

CREATE TABLE nopv AS
SELECT bbl, activityThrough, key, value
FROM rawdata
WHERE section = 'nopv'
ORDER BY bbl, activityThrough;

\copy joined TO '/data/nyc-rent-stabilization-data/joined.csv' WITH CSV DELIMITER ',' HEADER
\copy joined_nocrosstab TO '/data/nyc-rent-stabilization-data/joined-nocrosstab.csv' WITH CSV DELIMITER ',' HEADER
\copy changes_summary TO '/data/nyc-rent-stabilization-data/changes-summary.csv' WITH CSV DELIMITER ',' HEADER

\copy (select cd, sum("2007uc") as start, sum("2014uc") as end, 1 - (sum("2014uc")::real/sum("2007uc")) as change from joined group by cd order by cd) TO '/data/nyc-rent-stabilization-data/cds.csv' WITH CSV DELIMITER ',' HEADER
\copy (select ucbbl/1000000000, sum("2007uc") as start, sum("2014uc") as end, 1 - (sum("2014uc")::real/sum("2007uc")) as change from joined group by ucbbl/1000000000 order by ucbbl/1000000000) TO '/data/nyc-rent-stabilization-data/boroughs.csv' WITH CSV DELIMITER ',' HEADER
\copy (select *, 1.0 - ("2014uc"::real/"2007uc") as droppercent from joined where "2007uc" is not null and "2008uc" is not null and "2009uc" is not null and "2010uc" is not null and "2011uc" is not null and "2012uc" is not null and "2013uc" is not null and "2014uc" is not null and "2007uc" > 9 and "2014uc"::real/"2007uc" < 0.5) TO '/data/nyc-rent-stabilization-data/hqdrops.csv' WITH CSV DELIMITER ',' HEADER
\copy (select * from nopv) TO '/data/nyc-rent-stabilization-data/nopv.csv' WITH CSV DELIMITER ',' HEADER
