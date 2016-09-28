#!/usr/bin/env python

'''
Directly download tax bills from BBL and billing date
'''

import logging
import os
import sys
import time
import requests
import subprocess
from dateutil import parser
from download import save_file_from_stream, SESSION, find_extension


HANDLER = logging.StreamHandler(sys.stderr)
HANDLER.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(HANDLER)

PERIODS = [
    #'20120817 - Quarterly Property Tax Bill.pdf',
    'February 19, 2016 - Quarterly Property Tax Bill.pdf',
    'January 15, 2016 - Notice of Property Value.pdf',
    'January 15, 2016 - Tentative Assessment Roll.html',
    'June 3, 2016 - Quarterly Property Tax Bill.pdf',
    'August 22, 2008 - Quarterly Statement of Account.html',
    'August 22, 2014 - Quarterly Property Tax Bill.pdf',
    'August 23, 2013 - Quarterly Property Tax Bill.pdf',
    'August 26, 2011 - Quarterly Statement of Account.pdf',
    'August 27, 2010 - Quarterly Statement of Account.pdf',
    'August 28, 2009 - Quarterly Statement of Account.pdf',
    'December 19, 2008 - Quarterly Statement of Account.html',
    'February 18, 2011 - Quarterly Statement of Account.pdf',
    'February 20, 2009 - Quarterly Statement of Account.html',
    'February 20, 2015 - Quarterly Property Tax Bill.pdf',
    'February 21, 2014 - Quarterly Property Tax Bill.pdf',
    'February 22, 2013 - Quarterly Property Tax Bill.pdf',
    'February 24, 2012 - Quarterly Statement of Account.pdf',
    'February 26, 2010 - Quarterly Statement of Account.pdf',
    'January 15, 2005 - Notice of Property Value.html',
    'January 15, 2006 - Notice of Property Value.html',
    'January 15, 2007 - Notice of Property Value.html',
    'January 15, 2008 - Notice of Property Value.html',
    'January 15, 2009 - Notice of Property Value.html',
    'January 15, 2010 - Notice of Property Value.pdf',
    'January 15, 2010 - Tentative Assessment Roll.html',
    'January 15, 2011 - Notice of Property Value.pdf',
    'January 15, 2011 - Tentative Assessment Roll.html',
    'January 15, 2012 - Notice of Property Value.pdf',
    'January 15, 2012 - Tentative Assessment Roll.html',
    'January 15, 2013 - Notice of Property Value.pdf',
    'January 15, 2013 - Tentative Assessment Roll.html',
    'January 15, 2014 - Notice of Property Value.pdf',
    'January 15, 2014 - Tentative Assessment Roll.html',
    'January 15, 2015 - Notice of Property Value.pdf',
    'January 15, 2015 - Tentative Assessment Roll.html',
    'June 10, 2011 - Quarterly Statement of Account.pdf',
    'June 11, 2010 - Quarterly Statement of Account.pdf',
    'June 13, 2008 - Quarterly Statement of Account.html',
    'June 5, 2015 - Quarterly Property Tax Bill.pdf',
    'June 6, 2009 - Quarterly Statement of Account.pdf',
    'June 6, 2014 - Quarterly Property Tax Bill.pdf',
    'June 7, 2013 - Quarterly Property Tax Bill.pdf',
    'June 8, 2012 - Quarterly Property Tax Bill.pdf',
    'November 18, 2011 - Quarterly Statement of Account.pdf',
    'November 19, 2010 - Quarterly Statement of Account.pdf',
    'November 20, 2009 - Quarterly Statement of Account.pdf',
    'November 21, 2014 - Quarterly Property Tax Bill.pdf',
    'November 22, 2013 - Quarterly Property Tax Bill.pdf',
    'November 30, 2012 - Quarterly Property Tax Bill.pdf',
]

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
        '%B %-d, %Y - Quarterly Property Tax Bill')

    filenames = os.listdir(bbldir)
    nostatement_fname = 'nostatement.' + period + '.txt'
    if docname + '.pdf' in filenames:
        LOGGER.info(u'Already downloaded "%s" for BBL %s, skipping',
                    docname, bbl)
        return
    elif nostatement_fname in filenames:
        LOGGER.info(u'There is no "%s" for BBL %s, skipping', docname, bbl)
        return

    url = 'http://nycprop.nyc.gov/nycproperty/StatementSearch?' + \
            'bbl={bbl}&stmtDate={period}&stmtType=SOA'.format(period=period, bbl=bbl)
    resp = requests.get(url, stream=True)
    extension = find_extension(resp)

    if resp.url == u'http://nycprop.nyc.gov/nycproperty/nynav/jsp/StatementNotFound.jsp':
        LOGGER.warn('No statement for %s', url)
        subprocess.check_call('touch "{}/{}" &'.format(bbldir, nostatement_fname), shell=True)
        return

    if extension != 'pdf':
        LOGGER.warn('Cannot download %s, has wrong extension: %s', url, extension)
        raise requests.exceptions.ConnectionError()

    filename = os.path.join(bbldir, docname)
    LOGGER.info('Saving %s for %s', filename, bbl)
    save_file_from_stream(resp, filename)
    time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        with open(sys.argv[2]) as infile:
            for line in infile:
                wait = 10
                while True:
                    bbl_ = line.strip().split('\t')
                    try:
                        main(sys.argv[1], *bbl_)
                        break
                    except requests.exceptions.ConnectionError as err:
                        LOGGER.warn(u'ConnectionError on %s: %s, waiting %s seconds',
                                    bbl_, err, wait)
                        time.sleep(wait)
                        wait *= 2
    else:
        sys.stderr.write(u'''
Usage:

   python download_direct.py ['period of tax bill'] /path/to/bbls.tsv

If period is not specified, then all periods will be downloaded.

''')
        sys.exit(1)
