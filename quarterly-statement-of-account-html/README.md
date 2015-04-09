Scraper to extract text data from Quarterly Statement of Account HTML

### Installation

You will need to make sure to have installed all of `requirements.txt` in the
root directory.

    pip install requirements.txt

This is best done in a `virtualenv`.

### Usage

Output is written as a CSV to stdout.  Input can be any number of HTML files.

    python scrape.py /path/to/statement.html > outputfile.csv

Or

    python scrape.py /path/to/statements/*Quarterly\ Statement\ of\
Account.html > outputfile.csv
