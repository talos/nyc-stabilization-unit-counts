Scraper to extract text data from NoPV (Notice of Property Value) PDFs.

### Installation

    npm install

### Use

Can be used with single file:

    node scrape.js /path/to/nopv.pdf > outputfile.csv

Can also be used with multiple files:

    node scrape.js /path/to/input/*.pdf > outpufile.csv

A CSV is written to stdout, with errors written to stderr.
