Scraper to extract text data from Quarterly Property Tax Bills.

### Installation

You will need to have installed [xpdf][] on your system.

  [xpdf]: http://www.foolabs.com/xpdf/download.html

You will also need node and npm.  Then, in this directory:

    npm install

### Use as script

Can be used with single file:

    node run.js /path/to/nopv.pdf > outputfile.csv

Can also be used with a directory full of files:

    node run.js /path/to/input/ > outpufile.csv

A CSV is written to stdout, with errors written to stderr.

### Use as library

You can also use the scraper directly in a node script.

    scraper = require('./scrape.js')
    scraper('path/to/file.pdf', callback(data));
