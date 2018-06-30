#!/usr/bin/env python

'''
Directly download tax bills from BBL and billing date
'''

import logging
import os
import sys
import time
import subprocess
from subprocess import CalledProcessError
from dateutil import parser
from download import save_file_from_stream, SESSION, find_extension


HANDLER = logging.StreamHandler(sys.stderr)
HANDLER.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(HANDLER)

PERIODS = {
    #'20120817 - Quarterly Property Tax Bill.pdf',
    ('20180601', 'SOA'): 'June 1, 2018 - Quarterly Property Tax Bill.pdf',
    ('20180223', 'SOA'): 'February 23, 2018 - Quarterly Property Tax Bill.pdf',
    ('20180115', 'NOPV'): 'January 15, 2018 - Notice of Property Value.pdf',
    ('20171117', 'SOA'):  'November 17, 2017 - Quarterly Property Tax Bill.pdf',
    ('20170825', 'SOA'):  'August 25, 2017 - Quarterly Property Tax Bill.pdf',
    ('20170602', 'SOA'): 'June 2, 2017 - Quarterly Property Tax Bill.pdf',
    ('20170224', 'SOA'): 'February 24, 2017 - Quarterly Property Tax Bill.pdf',
    ('20161118', 'SOA'): 'November 18, 2016 - Quarterly Property Tax Bill.pdf',
    ('20160826', 'SOA'): 'August 26, 2016 - Quarterly Property Tax Bill.pdf',
    ('20160219', 'SOA'): 'February 19, 2016 - Quarterly Property Tax Bill.pdf',
    ('20160115', 'NOPV'): 'January 15, 2016 - Notice of Property Value.pdf',
    ('20160115', 'TAR'): 'January 15, 2016 - Tentative Assessment Roll.html',
    ('20160603', 'SOA'): 'June 3, 2016 - Quarterly Property Tax Bill.pdf',
    ('20080822', 'SOA'): 'August 22, 2008 - Quarterly Statement of Account.html',
    ('20140822', 'SOA'): 'August 22, 2014 - Quarterly Property Tax Bill.pdf',
    ('20130823', 'SOA'): 'August 23, 2013 - Quarterly Property Tax Bill.pdf',
    ('20110826', 'SOA'): 'August 26, 2011 - Quarterly Statement of Account.pdf',
    ('20100827', 'SOA'): 'August 27, 2010 - Quarterly Statement of Account.pdf',
    ('20090828', 'SOA'): 'August 28, 2009 - Quarterly Statement of Account.pdf',
    ('20081219', 'SOA'): 'December 19, 2008 - Quarterly Statement of Account.html',
    ('20110218', 'SOA'): 'February 18, 2011 - Quarterly Statement of Account.pdf',
    ('20090220', 'SOA'): 'February 20, 2009 - Quarterly Statement of Account.html',
    ('20150220', 'SOA'): 'February 20, 2015 - Quarterly Property Tax Bill.pdf',
    ('20140221', 'SOA'): 'February 21, 2014 - Quarterly Property Tax Bill.pdf',
    ('20130222', 'SOA'): 'February 22, 2013 - Quarterly Property Tax Bill.pdf',
    ('20120224', 'SOA'): 'February 24, 2012 - Quarterly Statement of Account.pdf',
    ('20100226', 'SOA'): 'February 26, 2010 - Quarterly Statement of Account.pdf',
    ('20050115', 'NOPV'): 'January 15, 2005 - Notice of Property Value.html',
    ('20060115', 'NOPV'): 'January 15, 2006 - Notice of Property Value.html',
    ('20070115', 'NOPV'): 'January 15, 2007 - Notice of Property Value.html',
    ('20080115', 'NOPV'): 'January 15, 2008 - Notice of Property Value.html',
    ('20090115', 'NOPV'): 'January 15, 2009 - Notice of Property Value.html',
    ('20100115', 'NOPV'): 'January 15, 2010 - Notice of Property Value.pdf',
    ('20100115', 'TAR'): 'January 15, 2010 - Tentative Assessment Roll.html',
    ('20110115', 'NOPV'): 'January 15, 2011 - Notice of Property Value.pdf',
    ('20110115', 'TAR'): 'January 15, 2011 - Tentative Assessment Roll.html',
    ('20120115', 'NOPV'): 'January 15, 2012 - Notice of Property Value.pdf',
    ('20120115', 'TAR'): 'January 15, 2012 - Tentative Assessment Roll.html',
    ('20130115', 'NOPV'): 'January 15, 2013 - Notice of Property Value.pdf',
    ('20130115', 'TAR'): 'January 15, 2013 - Tentative Assessment Roll.html',
    ('20140115', 'NOPV'): 'January 15, 2014 - Notice of Property Value.pdf',
    ('20140115', 'TAR'): 'January 15, 2014 - Tentative Assessment Roll.html',
    ('20150115', 'NOPV'): 'January 15, 2015 - Notice of Property Value.pdf',
    ('20150115', 'TAR'): 'January 15, 2015 - Tentative Assessment Roll.html',
    ('20110610', 'SOA'): 'June 10, 2011 - Quarterly Statement of Account.pdf',
    ('20100611', 'SOA'): 'June 11, 2010 - Quarterly Statement of Account.pdf',
    ('20080613', 'SOA'): 'June 13, 2008 - Quarterly Statement of Account.html',
    ('20150605', 'SOA'): 'June 5, 2015 - Quarterly Property Tax Bill.pdf',
    ('20090606', 'SOA'): 'June 6, 2009 - Quarterly Statement of Account.pdf',
    ('20140606', 'SOA'): 'June 6, 2014 - Quarterly Property Tax Bill.pdf',
    ('20130607', 'SOA'): 'June 7, 2013 - Quarterly Property Tax Bill.pdf',
    ('20120608', 'SOA'): 'June 8, 2012 - Quarterly Property Tax Bill.pdf',
    ('20111118', 'SOA'): 'November 18, 2011 - Quarterly Statement of Account.pdf',
    ('20101119', 'SOA'): 'November 19, 2010 - Quarterly Statement of Account.pdf',
    ('20091120', 'SOA'): 'November 20, 2009 - Quarterly Statement of Account.pdf',
    ('20141121', 'SOA'): 'November 21, 2014 - Quarterly Property Tax Bill.pdf',
    ('20131122', 'SOA'): 'November 22, 2013 - Quarterly Property Tax Bill.pdf',
    ('20121130', 'SOA'): 'November 30, 2012 - Quarterly Property Tax Bill.pdf',
}

BOROUGHS = {
    'MN': '1',
    'BX': '2',
    'BK': '3',
    'QN': '4',
    'SI': '5',
}

def main(period, doc_type, borough, block, lot, *_):
    '''
    Download a single tax bill
    '''
    if borough in BOROUGHS:
        borough = BOROUGHS[borough]
    block = str(block).zfill(5)
    lot = str(lot).zfill(4)
    bbl = ''.join([borough, block, lot])
    bbldir = os.path.join('data', borough, block, lot)
    try:
        os.makedirs(bbldir)
    except: #pylint: disable=bare-except
        pass
    #docname = parser.parse(period).strftime(  #pylint: disable=no-member
    #    '%B %-d, %Y - Quarterly Property Tax Bill')
    docname = PERIODS[(period, doc_type)]

    filenames = os.listdir(bbldir)
    nostatement_fname = 'nostatement.' + period + '.txt'
    if (docname in filenames) or (docname.replace('.pdf', '.txt') in filenames):
        LOGGER.info(u'Already downloaded "%s" for BBL %s, skipping',
                    docname, bbl)
        return
    elif docname + '.pdf' in filenames:
        subprocess.check_call('mv "{bbldir}/{docname}.pdf" "{bbldir}/{docname}"'.format(
            bbldir=bbldir, docname=docname), shell=True)
        LOGGER.info(u'Already downloaded "%s" for BBL %s, skipping (fixed path)',
                    docname, bbl)
        return
    elif nostatement_fname in filenames:
        LOGGER.info(u'There is no "%s" for BBL %s, skipping', docname, bbl)
        return

    url = 'http://nycprop.nyc.gov/nycproperty/StatementSearch?' + \
            'bbl={bbl}&stmtDate={period}&stmtType={doc_type}'.format(
                period=period, bbl=bbl, doc_type=doc_type)

    filename = os.path.join(bbldir, docname)
    LOGGER.info('Saving %s for %s', filename, bbl)
    subprocess.check_call('wget --max-redirect=0 -O "{filename}" "{url}" '
                          ' || (rm "{filename}" && touch "{nofilemarker}")'.format(
                              filename=filename,
                              url=url,
                              nofilemarker=os.path.join(bbldir, nostatement_fname)
                          ), shell=True)
    #time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        with open(sys.argv[3]) as infile:
            for line in infile:
                bbl_ = line.strip().split('\t')
                main(sys.argv[1], sys.argv[2], *bbl_)
    elif len(sys.argv) == 3:
        for line in sys.stdin:
            bbl_ = line.strip().split('\t')
            main(sys.argv[1], sys.argv[2], *bbl_)
    else:
        sys.stderr.write(u'''
Usage:

   python download_direct.py ['period of tax bill'] [SOA|NOPV|TAR] /path/to/bbls.tsv

or

   cat /path/to/bbls.tsv | python download_direct.py ['period of tax bill'] [SOA|NOPV|TAR]

''')
        sys.exit(1)
