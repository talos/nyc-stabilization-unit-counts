#!/usr/bin/env python

'''
Convert quarterly statement of account html into CSV
'''

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
    "key",
    "date",
    "value"
]

#OWNER_NAME = 'owner_name'
#PROPERTY_ADDRESS = 'property_address'
#MAILING_ADDRESS = 'mailing_address'
#PREVIOUS_BALANCE = 'summary_previous_balance'
#AMOUNT_PAID = 'summary_amount_paid'
#UNPAID_BALANCE = 'summary_unpaid_blanace'
#CURRENT_AMOUNT_DUE = 'summary_current_amount_due'
#TOTAL_AMOUNT_DUE = 'summary_total_amount_due'
#
#PREVIOUS_BALANCE_TAX = 'details_previous_balance_tax'
#PREVIOUS_BALANCE_PAYMENT = 'details_previous_balance_payment'
#PREVIOUS_BALANCE_UNPAID = 'details_previous_balance_unpaid'
#
#CURRENT_AMOUNT_TAX = 'details_current_amount_tax'
#CURRENT_AMOUNT_PAYMENT = 'details_current_amount_payment'
#CURRENT_AMOUNT_DUE = 'details_current_amount_due'
#
#TAX_CLASS = 'tax_class'
#TAX_RATE = 'tax_rate'


#HEADERS = [
#    "bbl",
#    "activityThrough",
#    "rentStabilized",
#    "units",
#    "ownerName",
#    "propertyAddress",
#    "mailingAddress",
#    "annualPropertyTax",
#    "abatements",
#    "billableAssessedValue",
#    "taxRate"
#]


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


def _owner_name(soup):
    el = soup.find(text=re.compile('Owner Name:'))
    return [c for c in el.parent.parent.children][-1].strip()


def _activity_through(soup):
    el = soup.find(text=re.compile('Reflects Account Activity from'))
    match = re.search(r'Statement through\s+([^)]+)', unicode(el))
    return parser.parse(match.group(1)).strftime('%Y-%m-%d')


def _rent_stabilized(soup):
    """
    Extract every rent stabilized line from the soup.
    """
    els = soup.find_all(text=re.compile('Housing-Rent Stabilization'))
    lines = []
    for el in els:
        housing_rent, stabilization, num_apts, date, id1, id2, amount = re.split(r'\s+', unicode(el).strip())
        lines.append([housing_rent + ' ' + stabilization, int(num_apts),
                      parser.parse(date).strftime('%Y-%m-%d'), id1 + ' ' + id2,
                      float(amount.replace('$', ''))])
    return lines


        #match = re.search(r'Housing-Rent Stabilization\s+(\d+)', unicode(el))
        #if not match:
        #    return 0
        #else:
        #    return int(match.group(1))


def extract(html):
    """
    Extract Quarterly Statement of Account data from HTML

    Yields a dict for each piece of data.
    """
    soup = BeautifulSoup(html)
    soup.find(text=re.compile('Housing-Rent Stabilization'))

    activity_through = _activity_through(soup)
    owner_name = _owner_name(soup)
    mailing_address = _mailing_address(soup)
    rent_stabilized = _rent_stabilized(soup)

    import pdb
    pdb.set_trace()

    #stabilized_units = rent_stabilized(soup)
    #data = {
    #    "rentStabilized": stabilized_units > 0,
    #    "units": stabilized_units,
    #    "activityThrough": ),
    #    "ownerName": owner_name(soup),
    #    # "propertyAddress": property_address(soup), ## TODO
    #    # "mailingAddress": mailing_address(soup), ## TODO
    #    # "abatements": abatements(soup), ## TODO
    #    # "billableAssessedValue": billable_assessed_value(soup), ## TODO
    #    # "taxRate": tax_rate(soup) ## TODO
    #}
    #
    #return data


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
                    bbl = path.split(os.path.sep)[-3:]
                    # date = path.split(os.path.sep)[-1].split(' - ')
                    with open(os.path.join(path, filename), 'r') as handle:
                        data = extract(handle.read())
                    data.update({
                        # 'date': date,
                        'bbl': ''.join(bbl)
                    })
                    writer.writerow(data)
                except Exception as err:  # pylint: disable=broad-except
                    LOGGER.warn('Could not parse %s, error: %s', os.path.join(path, filename), err)


if __name__ == '__main__':
    main(sys.argv[1])
