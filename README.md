# NYC Stabilization Unit Counts

Liberate NYC DOF tax documents to a machine readable format.

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

## Usage

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

## Sample

You can see a sample of data being collected [here](http://www.taxbills.nyc/).

Downloading is currently in progress.  Almost all of Manhattan 6+ unit
buildings have been downloaded, along with everything in Manhattan ever on the
DHCR rent stabilization list.  Outside of Manhattan, all 10+ unit buildings
have been downloaded.

Folder scheme: `data/<borough>/<block>/<lot>/`
