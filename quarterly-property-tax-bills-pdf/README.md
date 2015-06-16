Scraper to extract text data from Quarterly Property Tax Bills.

### Installation

You will need to have installed [xpdf][] on your system.

  [xpdf]: http://www.foolabs.com/xpdf/download.html

You will need Python 2.7, but without any special requirements.

### Use as script

Must be used with a directory full of files:

    python scrape.py /path/to/input/ > outpufile.csv

A CSV is written to stdout, with errors written to stderr.
