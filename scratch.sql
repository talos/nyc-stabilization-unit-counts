SELECT bbl, unitstotal, unitsres FROM
nyc_pluto pl JOIN registrations reg
ON pl.bbl = reg.dhcrbbl
WHERE ucbbl IS NULL
ORDER BY ucbbl;

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

