# NYC Stabilization Unit Counts
Liberate NYC DOF tax documents to a machine readable format.

## Dependencies
- Python 2.6 or greater
- libmagic file type identification library

If on Mac OS X install Python and Libmagic via homebrew:

```
brew install python libmagic
```


The following python libraries:

- BeautifulSoup4
- requests
- lxml
- python-magic
- re

Use `pip install <library name>` to install python libraries.


## Usage
###To download all documents for a single address:
```
python download.py <house no> <street name with suffix> <borough number>
```

### To download documents for multiple addresses:  

1. Create a tab seperated file (eg: `addresses.tsv`) containing the house number, street name and suffix, and borough number. Separate each address by a new line.

2. Then do:

```
python download.py addresses.tsv
```

## To Do
- [ ] Scrape PDFs and HTML files after downloading them.
- [ ] Host scraped data online