# NYC Stabilization Unit Counts

Liberate NYC DOF tax documents to a machine readable format.

## Installation

You'll need the following:

- Linux, BSD, or MacOSX machine
- Python 2.6 or greater (not tested on 3)
- `virtualenv` or `virtualenvwrapper` (in order to install requirements without
  using `sudo`

Within a virtualenv, simply install the requirements:

    pip install -r requirements.txt

## Usage

### To download all documents for a single address:

    python download.py <house no> '<street name with suffix>' <borough number>

Make sure to put the street name in single quotes.

### To download documents for multiple addresses:

1. Create a tab separated file (eg: `addresses.tsv`) containing the house
   number, street name and suffix, and borough number. Separate each address by
   a new line.

2. Then do:

       python download.py addresses.tsv

## Sample

You can see a sample of data being collected [here](http://104.236.234.7/).

These are raw records being pulled from all buildings with ten or more units in
CB 8 (Upper East Side) in Manhattan, CBs 8 & 9 in Brooklyn (Lefferts/Crown
Heights), CB4 in the Bronx (Concourse), CBs 1 & 2 in Queens (Astoria & LIC),
and CB1 in Staten Island (North Shore.)

Folder scheme: Data - > borough (1,2,3,4 or 5) -> block -> bbl

## Scraper

Scraper.js scrapes property tax bill and ouputs a json:
  
  ```
  { 
    activityThrough: null,
    ownerName: '',
    propertyAddress: '',
    bbl: '',
    mailingAddress: '',
    rentStabilized: null,
    units: null,
    annualPropertyTax: null,
    abatements: [],
    billableAssessedValue: null,
    taxRate: null
  }
  ```

Scrape (filepath, callback(taxDoc))

Filepath is the filepath to the tax bill
Callback is called with one argument containing the taxDoc object

## Issues

  * The annualPropertyTax field for November 2012 and 2013's bills scrapes incorrectly
  * There are issues when rent-stabilized units appear more than once such as in 1-01505-0044

## download.js

  Reads a file with a bbl on each line. bbls must be in 10 digit format (such as 1015050044). It runs download.py for each bbl one at a time. You can change the number of concurrent downloads at the risk of overwhelming the sever.

## to do

  - [ ] distributed downloading?
  - [ ] fix scraper issues
  - [ ] scrape property tax bills
  - [ ] connect database

## printout.js

A utility used to help create the scrape.js
