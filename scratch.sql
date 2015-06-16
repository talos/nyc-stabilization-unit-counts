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


select sum("2007"), sum("2008"), sum("2009"), sum("2010"),
sum("2011"), sum("2012"), sum("2015"),
sum("2015") - sum("2007"),
(sum("2015") - sum("2007") * 1.0) / sum("2007")
from joined
where
--where "2007" is not null and
-- "2008" is not null and
-- "2009" is not null and
-- "2010" is not null and
-- "2011" is not null and
-- "2012" is not null and
-- "2015" is not null and
  yearbuilt > 1948
;
 

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

