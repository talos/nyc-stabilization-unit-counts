/* comparisons of RGB data to our totals. */

/*CREATE VIEW borough_year_summary AS
SELECT ucbbl/1000000000 borough, year, SUM(unitcount) as sum
FROM joined_nocrosstab
GROUP BY ucbbl/1000000000, year
ORDER BY ucbbl/1000000000, year;*/

SELECT
dof.borough, rgb.year,
dof.net as dof_net, rgb.net as rgb_net,
    ((rgb.net - dof.net) * 100.0 / rgb.net)::int net_err,
dof.sub as dof_sub, rgb.total_sub as rgb_sub,
    ((rgb.total_sub - dof.sub) * 100.0 / rgb.total_sub)::int sub_err,
dof.add as dof_add, rgb.total_add as rgb_add,
    ((rgb.total_add - dof.add) * 100.0 / rgb.total_add)::int add_err
FROM
(SELECT a.ucbbl/1000000000 borough, b.year,
       SUM(b.unitcount - a.unitcount) net,
       SUM(CASE WHEN b.unitcount - a.unitcount < 0 THEN b.unitcount - a.unitcount ELSE 0 END) AS sub,
       SUM(CASE WHEN b.unitcount - a.unitcount > 0 THEN b.unitcount - a.unitcount ELSE 0 END) AS "add"
FROM joined_nocrosstab a, joined_nocrosstab b
WHERE a.ucbbl = b.ucbbl
      AND a.year = b.year - interval '1 year'
GROUP BY borough, b.year
ORDER BY borough, b.year) dof, rgb
WHERE rgb.borough = dof.borough AND rgb.year = date_part('year', dof.year)
ORDER BY rgb.borough, rgb.year;


SELECT bbl, unitstotal, unitsres FROM
nyc_pluto pl JOIN registrations reg
ON pl.bbl = reg.dhcrbbl
WHERE ucbbl IS NULL
ORDER BY ucbbl;

select ucbbl,
"2007uc", "2007est",
"2008uc", "2008est",
"2009uc", "2009est",
"2010uc", "2010est",
"2011uc", "2011est",
"2012uc", "2012est",
"2013uc", "2013est",
"2014uc", "2014est"
from joined
order by ucbbl;

SELECT dhcrbbl / 1000000000 as borough, COUNT(distinct dhcrbbl) FROM
registrations reg
WHERE ucbbl IS NULL
GROUP BY borough
ORDER BY borough;

-- dump TSV of manhattan bbls on hcr's list that we didn't scrape as of last
-- import.sh
\copy (select substr(dhcrbbl::text, 0, 2), substr(dhcrbbl::text, 2, 5)::int, substr(dhcrbbl::text, 8, 4)::int, dhcrbbl from registrations where ucbbl is null group by dhcrbbl) to input/dhcrmissingbbls.tsv

\copy ( select distinct borough, block, lot from nyc_pluto where unitstotal >= 6 union select distinct boro_code, block, lot from dhcrlist order by borough, block, lot) to input/allbbls.tsv

select borough, sum("2007uc") "2007",
sum("2008uc") "2008", sum("2009uc") "2009", sum("2010uc") "2010",
sum("2011uc") "2011", sum("2012uc") "2012", sum("2013uc") "2013",
sum("2014uc") "2014"
from joined
group by borough;

copy (select borough,
sum("2008uc") - sum("2007uc") "2008",
sum("2009uc") - sum("2008uc") "2009",
sum("2010uc") - sum("2009uc") "2010",
sum("2011uc") - sum("2010uc") "2011",
sum("2012uc") - sum("2011uc") "2012",
sum("2013uc") - sum("2012uc") "2013",
sum("2014uc") - sum("2013uc") "2014"
from joined
group by borough)
to stdout WITH CSV DELIMITER ',' HEADER;

where
not (
  "2007uc" >= coalesce("2008uc", 0) - 2 AND
  "2008uc" >= coalesce("2009uc", 0) - 2 AND
  "2009uc" >= coalesce("2010uc", 0) - 2 AND
  "2010uc" >= coalesce("2011uc", 0) - 2 AND
  "2011uc" >= coalesce("2012uc", 0) - 2 AND
  "2012uc" >= coalesce("2013uc", 0) - 2 AND
  "2013uc" >= coalesce("2014uc", 0) - 2 
)
group by borough;

select borough, sum("2007uc") "2007",
sum("2008uc") "2008", sum("2009uc") "2009", sum("2010uc") "2010",
sum("2011uc") "2011", sum("2012uc") "2012", sum("2013uc") "2013",
sum("2014uc") "2014"
from joined
where 
 "2009abat" NOT LIKE '%420c' AND "2009abat" NOT LIKE '%421a%' AND
 "2010abat" NOT LIKE '%420c' AND "2010abat" NOT LIKE '%421a%' AND
 "2011abat" NOT LIKE '%420c' AND "2011abat" NOT LIKE '%421a%' AND
 "2012abat" NOT LIKE '%420c' AND "2012abat" NOT LIKE '%421a%' AND
 "2013abat" NOT LIKE '%420c' AND "2013abat" NOT LIKE '%421a%' AND
 "2014abat" NOT LIKE '%420c' AND "2014abat" NOT LIKE '%421a%' AND
 "2007uc" is not null and
 "2008uc" is not null and
 "2009uc" is not null and
 "2010uc" is not null and
 "2011uc" is not null and
 "2012uc" is not null and
 "2013uc" is not null and
 "2014uc" is not null
group by borough;

select borough, sum("2007") "2007",
sum("2008") "2008", sum("2009") "2009", sum("2010") "2010",
sum("2011") "2011", sum("2012") "2012", sum("2015") "2015",
sum("2015") - sum("2007") change,
(sum("2015") - sum("2007") * 1.0) / sum("2007") percent
from joined
--where "2007" is not null and
-- "2008" is not null and
-- "2009" is not null and
-- "2010" is not null and
-- "2011" is not null and
-- "2012" is not null and
-- "2015" is not null
group by borough
order by borough
;

select cd, sum("2007") "2007",
sum("2008") "2008", sum("2009") "2009", sum("2010") "2010",
sum("2011") "2011", sum("2012") "2012", sum("2015") "2015",
sum("2015") - sum("2007") change,
(sum("2015") - sum("2007") * 1.0) / sum("2007") percent
from joined
where
-- "2007" is not null and
-- "2008" is not null and
-- "2009" is not null and
-- "2010" is not null and
-- "2011" is not null and
-- "2012" is not null and
-- "2015" is not null and
  borough = 'MN'
group by cd
order by cd;

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


/* figure out what stabilized bbls we missed */
create table rawdata_bbls as (select bbl, left(bbl::text, 1)::int as borough, substr(bbl::text, 2, 5)::int as block, substr(bbl::text, 7, 4)::int as lot, min(activitythrough) as earliest, max(activitythrough) as last from rawdata
  group by bbl order by bbl);
alter table rawdata_bbls add column oneyear boolean;
update rawdata_bbls set oneyear = (last = '2015-06-05' and earliest = '2015-06-05');
create table rawdata_bbls_stabilized as (select bbl from rawdata where key = 'Housing-Rent Stabilization' group by bbl);
alter table rawdata_bbls add column stabilized boolean default 'f';
update rawdata_bbls a set stabilized = 't' from rawdata_bbls_stabilized b where a.bbl = b.bbl;

copy (select borough,block,lot from rawdata_bbls where oneyear = 't' and stabilized = 't') to '/tmp/missingstabilized.tsv';

/* determine size of issue with non-numeric RS Fee identifiers */
SELECT * FROM unitcounts
WHERE meta !~ '^[\d ]+$'
ORDER BY units DESC;

/* find all properties with 421a or rent stabilization */
SELECT *
INTO rawdata_exempt_stabilized
FROM rawdata
WHERE lower(key) IN (
  'new mult dwellings - 421a',
  'j-51 alteration',
  '421a (25 yr not cap',
  '420c housing',
  '421a (15 yr not cap)',
  'new mult dwellings',
  '421a (10 yr cap)',
  '421a (20 yr not cap'
);
DROP TABLE IF EXISTS exempt_stabilized;
CREATE TABLE exempt_stabilized (
  bbl BIGINT,
  exemptions TEXT,
  registered_stabilized_apts INT,
  pluto_apts INT,
  estimated_gross_income REAL,
  estimated_expenses REAL
);


INSERT INTO exempt_stabilized
SELECT bbl, STRING_AGG(distinct key, ',')
FROM rawdata_exempt_stabilized
WHERE activitythrough = '2015-06-05'
  AND lower(key) IN (
    'new mult dwellings - 421a', '421a (25 yr not cap', '421a (15 yr not cap)', 'new mult dwellings'
    '421a (10 yr cap)', '421a (20 yr not cap'
   )
  AND RIGHT(bbl::text, 4)::INT < 1000
GROUP BY bbl
ORDER BY bbl;

UPDATE exempt_stabilized xs
  SET registered_stabilized_apts = "2014uc"
FROM joined
WHERE joined.ucbbl = xs.bbl AND
  "2014est" = 'N';

UPDATE exempt_stabilized xs
  SET pluto_apts = COALESCE(unitsres, unitstotal)
FROM "contrib/us/ny/nyc".pluto pl
WHERE pl.bbl = xs.bbl;

UPDATE exempt_stabilized xs
  SET estimated_gross_income = value::real
FROM nopv
WHERE nopv.bbl = xs.bbl AND nopv.key = 'gross income';

UPDATE exempt_stabilized xs
  SET estimated_expenses = value::real
FROM nopv
WHERE nopv.bbl = xs.bbl AND nopv.key = 'expenses';

/* show that there are 79018 apts in PLUTO collecting 421a in 2015, of which
 * 51312 are registered stabilized. */
select sum(pluto_apts), sum (registered_stabilized_apts) from exempt_stabilized ;

\copy (select * from exempt_stabilized) TO '/data/nyc-rent-stabilization-data/exempt_stabilized.csv' WITH CSV DELIMITER ',' HEADER

/** see the concentration of different keys **/
select key, count(*) into concentration_keys from rawdata group by key order by count(*);


