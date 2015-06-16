#!/usr/bin/env python

'''
Directly download tax bills from BBL and billing date
'''

import logging
import os
import sys
import time
from dateutil import parser
from download import save_file_from_stream, SESSION


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stderr))

def main(period, borough, block, lot, *_):
    '''
    Download a single tax bill
    '''
    block = str(block).zfill(5)
    lot = str(lot).zfill(4)
    bbl = ''.join([borough, block, lot])
    bbldir = os.path.join('data', borough, block, lot)
    try:
        os.makedirs(bbldir)
    except: #pylint: disable=bare-except
        pass
    docname = parser.parse(period).strftime(  #pylint: disable=no-member
        '%B %d, %Y - Quarterly Property Tax Bill.pdf')

    filenames = ['.'.join(f.split('.')[:-1]) or f
                 for f in os.listdir(bbldir)]
    if docname in filenames:
        LOGGER.info(u'Already downloaded "%s" for BBL %s, skipping',
                    docname, bbl)
        return

    url = 'http://nycprop.nyc.gov/nycproperty/StatementSearch?' + \
            'bbl={bbl}&stmtDate={period}&stmtType=SOA'.format(period=period, bbl=bbl)
    resp = SESSION.get(url, stream=True)
    filename = os.path.join(bbldir, docname)
    LOGGER.info('Saving %s for %s', filename, bbl)
    save_file_from_stream(resp, filename)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        with open(sys.argv[2]) as infile:
            for line in infile:
                main(sys.argv[1], *line.strip().split('\t'))
                time.sleep(1)
    else:
        sys.stderr.write(u'''

python download_direct.py 'period of tax bill' /path/to/bbls.tsv

''')
        sys.exit(1)
