#!/usr/bin/env python

'''
Convert quarterly property tax bill into CSV
'''

import csv
import logging
import os
import subprocess
import sys
import re
import traceback
from dateutil import parser

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

def parseamount(string):
    """
    Convert string of style -$24,705.75 to float -24705.75
    """
    return float(string.replace(',', '').replace('$', ''))


def split(string):
    """
    Split a string by any time there are multiple spaces
    """
    return re.split(r'\s{2,}', string.strip())


def parsedate(string):
    """
    Use dateutil to parse an ambiguous date string into YYYY-MM-DD
    """
    return parser.parse(string).strftime('%Y-%m-%d') #pylint: disable=no-member


def extract(bbl, text):
    """
    Extract Quarterly Statement of Account data from text

    Yields a dict for each piece of data.
    """
    activity_through = parsedate(re.search(r'Activity through (.*)', text).group(1))
    base = {
        'bbl': bbl,
        'activityThrough': activity_through
    }

    owner_address_area = re.search(
        r'Owner name:(.*)Property address:(.*)Borough, block & lot:(.*)'
        r'(Outstanding Charges|Statement Billing Summary)',
        text, re.DOTALL).groups()
    owner_address_split = [split(x) for x in owner_address_area][:-1]

    #if len(owner_address_split) == 4 and len(owner_address_split[3]) == 2:
    #    owner_name = u'\n'.join([owner_address_split[0][0],
    #                             owner_address_split[1][0]])
    #else:

    owner_name = owner_address_split[0][0]
    base.update({
        'key': 'Owner name',
        'value': owner_name
    })
    yield base

    mailing_address = u'\n'.join(x[1] if len(x) > 1 else '' for x in owner_address_split).strip()
    base.update({
        'key': 'Mailing address',
        'value': mailing_address
    })

    yield base

    matches = re.finditer(r'(Charges You Can Pre-pay|Tax Year Charges Remaining|Current Charges).*?Total[\S ]*',
                              text, re.DOTALL)
    for match in matches:
        # TODO due_date actually needs to be figured out by determining which
        # column the line is in.

        # Everything has a due date.  Only certain things (payments, additional
        # charges) have activity dates.
        due_date = None
        form_feed = False  # used when there's a page gap in the middle of match

        lines = match.group().split('\n')
        if len(lines) == 1:
            continue

        for i, line in enumerate(lines):
            key = None
            meta = None
            stabilization_due_date = None
            activity_date = None
            value = None

            cells = split(line)

            # Handle case when there's a pagebreak (and thus a bunch of repeat
            # header stuff) in the middle of a data section
            if form_feed == True:
                if cells[-1] == 'Amount':
                    form_feed = False
                continue

            if i == 0:
                continue
            elif i == 1:
                # Sometimes the first line in this section is the stabilized
                # area, so there's no overriding due_date
                if cells[1] != '# Apts':
                    due_date = parsedate(cells[1])

            if line.startswith('\f') or cells[0].startswith('Pay today') or cells[0].startswith('Home banking payment instructions'):
                form_feed = True
                continue

            if line == '':
                continue
            elif u'Rent Stabilization fee' in cells[0]:
                continue
            elif cells[0] == 'Housing-Rent Stabilization':
                key = cells[0]
                value = int(cells[1])
                stabilization_due_date = parsedate(cells[2].split()[0])
                meta = ' '.join(cells[2].split()[1:])
            elif len(cells) == 2:
                key = cells[0]
                value = parseamount(cells[1])
            elif len(cells) == 3:
                key = cells[0]
                activity_date = parsedate(cells[1])
                value = parseamount(cells[2])
            elif len(cells) == 4:
                key = cells[0]
                activity_date = parsedate(cells[1])
                meta = cells[2]
                value = parseamount(cells[3])
            else:
                if 'State law recently changed' in line:
                    continue
                elif 'Due to this change,' in line:
                    continue
                #import pdb
                #pdb.set_trace()

            base.update({
                'key': key,
                'value': value,
                'dueDate': stabilization_due_date or due_date,
                'activityDate': activity_date,
                'value': value,
                'meta': meta
            })
            yield base


def main(root):
    """
    Process a list of filenames with Quarterly Statement of Account data.
    """
    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    for path, _, files in os.walk(root):
        for filename in files:
            if 'Quarterly Property Tax Bill.pdf' in filename:
                try:
                    bbl = path.split(os.path.sep)[-3:]
                    pdf_path = os.path.join(path, filename)
                    text_path = pdf_path.replace('.pdf', '.txt')
                    if not os.path.exists(text_path):
                        subprocess.check_call("pdftotext -layout '{}'".format(
                            pdf_path
                        ), shell=True)

                    # date = path.split(os.path.sep)[-1].split(' - ')
                    with open(text_path, 'r') as handle:
                        for data in extract(''.join(bbl), handle.read()):
                            writer.writerow(data)
                except Exception as err:  # pylint: disable=broad-except
                    #import pdb
                    #pdb.set_trace()
                    LOGGER.warn(traceback.format_exc())
                    LOGGER.warn('Could not parse %s, error: %s', os.path.join(path, filename), err)


if __name__ == '__main__':
    main(sys.argv[1])
