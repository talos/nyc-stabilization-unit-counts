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

1. Create a tab seperated file (eg: `addresses.tsv`) containing the house
   number, street name and suffix, and borough number. Separate each address by
   a new line.

2. Then do:

       python download.py addresses.tsv

## To Do

- [ ] Scrape PDF and HTML files after downloading them.
- [ ] Host scraped data online
