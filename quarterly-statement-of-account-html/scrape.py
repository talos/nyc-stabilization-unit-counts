#!/usr/bin/env python

import sys
import logging
import csv
import os
import re
from dateutil import parser
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stderr))

HEADERS = [
    "bbl",
    "activityThrough",
    "rentStabilized",
    "units",
    "ownerName",
    "propertyAddress",
    "mailingAddress",
    "annualPropertyTax",
    "abatements",
    "billableAssessedValue",
    "taxRate"
]


def property_address(soup):
    el = soup.find(text=re.compile('Owner Name:'))
    return [c for c in el.parent.parent.children][-1].strip()


def owner_name(soup):
    el = soup.find(text=re.compile('Owner Name:'))
    return [c for c in el.parent.parent.children][-1].strip()


def activity_through(soup):
    el = soup.find(text=re.compile('Reflects Account Activity from'))
    match = re.search(r'Statement through\s+([^)]+)', unicode(el))
    return parser.parse(match.group(1)).strftime('%Y-%m-%d')


def rent_stabilized(soup):
    el = soup.find(text=re.compile('Housing-Rent Stabilization'))
    match = re.search(r'Housing-Rent Stabilization\s+(\d+)', unicode(el))
    if not match:
        return 0
    else:
        return int(match.group(1))


def extract(data):
    """
    Extract Quarterly Statement of Account data from data
    """
    soup = BeautifulSoup(data)
    soup.find(text=re.compile('Housing-Rent Stabilization'))

    stabilized_units = rent_stabilized(soup)
    data = {
        "rentStabilized": stabilized_units > 0,
        "units": stabilized_units,
        "activityThrough": activity_through(soup),
        "ownerName": owner_name(soup),
        # "propertyAddress": property_address(soup), ## TODO
        # "mailingAddress": mailing_address(soup), ## TODO
        # "abatements": abatements(soup), ## TODO
        # "billableAssessedValue": billable_assessed_value(soup), ## TODO
        # "taxRate": tax_rate(soup) ## TODO
    }

    return data


def main(paths):
    """
    Process a list of filenames with Quarterly Statement of Account data.
    """
    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    for path in paths:
        bbl = path.split(os.path.sep)[-4:-1]
        # date = path.split(os.path.sep)[-1].split(' - ')
        with open(path, 'r') as f:
            data = extract(f.read())
        data.update({
            # 'date': date,
            'bbl': ''.join(bbl)
        })
        writer.writerow(data)


if __name__ == '__main__':
    main(sys.argv[1:])
