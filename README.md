# NYC Stabilization Unit Counts

Liberate NYC DOF tax documents to a machine readable format.

See why [here](http://blog.johnkrauss.com/betanyc-stabilization-presentation/#0).

Grab the latest parsed data [here](http://taxbills.nyc/joined.csv).

__Parsed data__ is licensed [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/)
![CC BY-SA](https://licensebuttons.net/l/by-sa/3.0/88x31.png).  See
[DATALICENSE-CC-BY-SA.html](http://taxbills.nyc/DATALICENSE-CC-BY-SA.html) for details.

You are free to:

* Share — copy and redistribute the material in any medium or format
* Adapt — remix, transform, and build upon the material for any purpose, even
  commercially.

The licensor cannot revoke these freedoms as long as you follow the license
terms.

Under the following terms:

* Attribution — You must give appropriate credit, provide a link to the
  license, and indicate if changes were made. You may do so in any reasonable
  manner, but not in any way that suggests the licensor endorses you or your
  use.

* ShareAlike — If you remix, transform, or build upon the material, you must
  distribute your contributions under the same license as the original.

* No additional restrictions — You may not apply legal terms or technological
  measures that legally restrict others from doing anything the license
  permits.

## Installation

You'll need the following:

- Linux, BSD, or MacOSX machine
- Python 2.6 or greater (not tested on 3)
- `virtualenv` or `virtualenvwrapper` (in order to install requirements without
  using `sudo`

The following requirements (on Debian):

    sudo apt-get install python-dev python-pip python-virtualenv \
                         build-essential libxml2-dev libxslt1-dev xpdf

Or on Mac (with Homebrew):

    brew install python pyenv-virtualenv libxml2 xpdf

Then create a virtualenv and install the requirements in it:

    virtualenv .env
    source .env/bin/activate
    pip install -r requirements.txt

## Developer Usage

### To download all documents for a single address:

    python download.py <house no> '<street name with suffix>' <borough number>

Make sure to put the street name in single quotes.

### To download documents for multiple addresses:

1. Create a tab separated file (eg: `addresses.tsv`) containing the house
   number, street name and suffix, and borough number. Separate each address by
   a new line.

2. Then do (running the download in the background):

    python download.py /path/to/addresses.tsv >/path/to/log.txt 2>&1 &

### To parse the raw data into a CSV

You'll probably want to background this too, as it takes a while.  The text PDF
bills are turned into txt files using `pdftotext`.

    python parse.py /path/to/input >/path/to/output.csv 2>/path/to/log.txt &

The structure of the CSV is as follows, including types:

| bbl    | activityThrough | section | key  | dueDate | activityDate | value | meta | apts |
| ------ | --------------- | ------- | ---- | ------- | ------------ | ----- | ---- | ---- |
| BIGINT | DATE            | TEXT    | TEXT | DATE    | DATE         | TEXT  | TEXT | INT  |

Since so much disparate information is recorded in tax bills, this raw output
is something like a key-value store, with additional metadata to identify what
building and tax period the data applies to.

* __bbl__: Lot identifier.
* __activityThrough__: Date of the tax bill.
* __section__: The section of the bill in which the charge appeared.  For
  example, `Previous Balance`, `Tax Year Charges Remaining`, `Current Charges`,
  etc.
* __key__: The type of data on this line.  For example, `Owner name`,
  `Housing-Rent stabilization`, `Health-Extermination`, etc.
* __dueDate__: If this is a charge, when it is due.  Not very accurate except
  for the rent stabilization lines.
* __activityDate__: If this is a payment, when it was made.  Not very accurate.
* __value__: The value of the line.  If the `key` was `Owner name` this would
  be their actual name; if it was `Health-Extermination` it would be the charge
  for the extermination, etc.
* __meta__: Additional metadata recorded on the line.  For rent stabilization,
  this is the registration number.  For some payments it is the bank that
  actually made the payment.
* __apts__: Only for rent stabiliztion lines, this is the stabilized unit
  count.

### To import the CSV into postgres

*In progress*

There are a few complicated dependencies here, including
[pgloader](http://pgloader.io), and a few external tables (PLUTO and the DHCR
stabilization building list history.)

    ./import.sh

## Data Usage

You can see all data [here](http://www.taxbills.nyc/).

Downloading is complete.  This means all 6+ unit buildings, in addition to all
buildings on DHCR's stabilized buildings list, are available and parsed.

Folder scheme for bills: `data/<borough>/<block>/<lot>/`

All PDFs are converted to their textual representations in the same folder.

### A [crosstab CSV with unit counts and abatements 2007-2014](http://taxbills.nyc/joined.csv)

Probably the most useful file for journalists or data-minded community advocates.
This file has a row for every possibly stabilized building in New York.  There
could  be stabilized buildings not on the list, but it is unlikely.  Any
building with 6 or more units as well as any building that was ever on HCR's
own list of stabilized buildings was scraped.  Buildings are aggregated by BBL.

- __borough__: Borough of this lot.
- __ucbbl__: The BBL.
- __2007uc__: The unit count in 2007.  This is based off of the rent
  stabilization surcharge dated "4/1/2007", which appears in tax bills
  starting 2008.  The parser sums these counts when a single tax bill
  includes multiple buildings, but is careful not to double-count if previous
  years' surcharges reappear.
- __2007est__: Whether or not this is an estimated unit count.  As
  registration is voluntary, it is common for a building to miss a year, or
  even several.  In such cases, an estimate is made using the previous year's
  count *if* a Disability Rent Increase Exemption (DRIE) or Senior Citizen
  Rent Increase Excemption (SCRIE) appears on the tax bill, *or* if the same
  abatements (for example, a 421a abatement) are collected as the prior year,
  *or* if the building appeared on HCR's rent stabilized buildings list that
  year.
- __2007dhcr__: Whether the building appeared on DHCR's list that year.
  Blank if DHCR did not publish a list for that year.
- __2007abat__: A list of all abatements and exemptions claimed on that
  year's tax bill.  This includes 421a, J51, 420C (LIHTC), SCRIE, DRIE, and
  several others.
- *These columns repeat for every year up to and including 2014*
- __cd__: The community district, from PLUTO.  All remaining columns are from
  PLUTO.
- __ct2010__: Census tract in 2010 census.
- __cb2010__: Census block in 2010 census.
- __council__: The city council district.
- __zipcode__: The zip code.
- __address__: An address for the lot, although it could have several.
- __ownername__: The name of the lot's owner.  Oftentimes just an LLC.
- __numbldgs__: The number of buildings on the lot.
- __numfloors__: The approximate number of floors on the lot's buildings.
- __unitsres__: An approximate number of residential units in the lot's
  buildings.
- __unitstotal__: An approximate number of residential & commercial units in
  the lot's buildings.
- __yearbuilt__: An approximate year built, not particularly accurate.
  Especially poor quality in older buildings.
- __condono__: The condo number, which links together different lots into a
  single condo development.
- __lon__: The lot's centerpoint longitude.
- __lat__: The lot's centerpoint latitude.

### A CSV as above but with [a separate row for each year](http://taxbills.nyc/joined-nocrosstab.csv)

The columns are the same as before, except instead of having separate columns
for each year of observation, there is a separate row.

This would be more useful for making a time-based map or doing statistical
analysis where the year column can be fed in as a proper dimension.

### A [summary of building changes](http://taxbills.nyc/joined-nocrosstab.csv) over the seven-year span.

This is the table that underlies the map.

- __ucbbl__: The BBL.
- __diff__: The number of stabilized units gained or lost between 2007 and
  2014.
- __percentchange__: The percentage increase or loss.  The denominator for
  this calculation is the greatest of `unitsres`, `unitstotal`, or the
  greatest number of stabilized units reported on a tax bill.
- __j51__: Start and end year of any J51 abatement.  Earliest start possible
  is 2009.
- __j51__: Start and end year of any 421-a abatement.  Earliest start possible
  is 2009.
- __j51__: Start and end year of any SCRIE abatement.  Earliest start possible
  is 2009.
- __j51__: Start and end year of any DRIE abatement.  Earliest start possible
  is 2009.
- __j51__: Start and end year of any 420C abatement.  Earliest start possible
  is 2009.
- *All remaining columns are from PLUTO as above.*

### Borough/CD summary tables

These are simple breakdowns of changes over the seven-year period by
[borough](http://taxbills.nyc/boroughs.csv) and
[community district](http://taxbills.nyc/cds.csv).
