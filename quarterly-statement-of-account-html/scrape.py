#!/usr/bin/env python

'''
Convert quarterly statement of account html into CSV
'''

import sys
import logging
import csv
import os
import re
import traceback
from dateutil import parser
#from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stderr))

HEADERS = [
    "bbl",
    "activityThrough",
    "key",
    "dueDate",
    "activityDate",
    "value",
    "meta"
]


def _mailing_address(soup):
    '''
    Address to which tax bills are mailed to.
    '''
    mailing_address = soup.find(text=re.compile('Mailing Address:'))
    table = mailing_address.parent.parent.parent.parent.parent
    out = []
    for i, row in enumerate(table.select('tr')):
        if i == 0:
            continue
        cells = row.select('td')
        if len(cells) == 2:
            out.append(cells[1].text)
    return '\n'.join(out).strip()


def parsedate(string):
    """
    Use dateutil to parse an ambiguous date string into YYYY-MM-DD
    """
    return parser.parse(string).strftime('%Y-%m-%d') #pylint: disable=no-member


def _owner_name(html):
    '''
    Obtain owner name from soup
    '''
    #elem = soup.find(text=re.compile('Owner Name:'))
    #return [c for c in elem.parent.parent.children][-1].strip()
    match = re.search(r'Owner Name:.*?<img[^>]*>([^<]*)<', html, re.IGNORECASE)
    return match.group(1).strip()


def _activity_through(html):
    '''
    Obtain activity through name from html
    '''
    match = re.search(r'Last Statement through\s+([^)]+)', html)
    return parsedate(match.group(1))


def _rent_stabilized(html):
    """
    Extract every rent stabilized line from the soup.
    """
    #els = soup.find_all(text=re.compile('Housing-Rent Stabilization'))
    for match in re.finditer(r'(Housing-Rent Stabilization.*?)<', html, re.IGNORECASE):
        housing_rent, stabilization, num_apts, date, id1, id2, _ = \
                re.split(r'\s+', match.group(1).strip())
        yield {
            'key': ' '.join([housing_rent, stabilization]),
            'value': num_apts,
            'dueDate': parsedate(date),
            'meta': id1 + ' ' + id2
        }

def extract(html, bbl):
    """
    Extract Quarterly Statement of Account data from HTML

    Yields a dict for each piece of data.
    """
    #soup = BeautifulSoup(html)

    activity_through = _activity_through(html)

    base = {
        'bbl': bbl,
        'activityThrough': activity_through
    }

    owner_name = _owner_name(html)
    base.update({
        'key': 'Owner name',
        'value': owner_name
    })
    yield base

    # mailing_address = _mailing_address(html)
    # base.update({
    #     'key': 'Mailing address',
    #     'value': mailing_address
    # })
    # yield base

    for rent_stabilized in _rent_stabilized(html):
        base.update(rent_stabilized)
        yield base


def main(root):
    """
    Process a list of filenames with Quarterly Statement of Account data.
    """
    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    for path, _, files in os.walk(root):
        for filename in files:
            if 'Quarterly Statement of Account.html' in filename:
                try:
                    bbl = ''.join(path.split(os.path.sep)[-3:])
                    with open(os.path.join(path, filename), 'r') as handle:
                        for data in extract(handle.read(), bbl):
                            writer.writerow(data)
                except Exception as err:  # pylint: disable=broad-except
                    LOGGER.warn(traceback.format_exc())
                    LOGGER.warn('Could not parse %s, error: %s', os.path.join(path, filename), err)


if __name__ == '__main__':
    main(sys.argv[1])
