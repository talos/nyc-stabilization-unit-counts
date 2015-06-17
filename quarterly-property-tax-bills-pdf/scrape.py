#!/usr/bin/env python

'''
Convert quarterly property tax bill into CSV
'''

import csv
import logging
import os
import subprocess
import sys
#try:
#    import re2 as re
#except ImportError:
import re
import traceback
from dateutil import parser

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stderr))

HEADERS = [
    "bbl",
    "activityThrough",
    "section",
    "key",
    "dueDate",
    "activityDate",
    "value",
    "meta",
    "apts"
]

BILL, STATEMENT = ('Quarterly Property Tax Bill.pdf', 'Quarterly Statement of Account.pdf')
ACTIVITY_THROUGH = {
    BILL: re.compile(r'Activity through (.*)', re.IGNORECASE),
    STATEMENT: re.compile(r'Last Statement Through (.*?)\)', re.IGNORECASE)
}
OWNER_ADDRESS_AREA = re.compile(
    r'Owner name:(.*)Property address:(.*)Borough, block & lot:(.*)'
    r'(Outstanding\s+Charges|Statement\s+Billing\s+Summary)', re.DOTALL + re.IGNORECASE
)

SPLIT_RE = re.compile(r'\s{2,}')
EXEMPTIONS_RE = re.compile(r'(Tax [Bb]efore [Ee]xemptions [Aa]nd [Aa]batements'
                           r'.*?Tax [Bb]efore [Aa]batements)', re.DOTALL)
UNITS_RE = re.compile(r'(\d+ [Uu]nits)')
SECTIONS_RE = re.compile(r'(Charges You Can Pre-pay|'  # prepayment
                         r'Amount Not Due [bB]ut That Can [bB]e Paid Early|'  #prepayment
                         r'Tax Year Charges Remaining|' # prepayment
                         r'Current Amount Due|' # due
                         r'Current Charges|' # due
                         r'Payment Agreement|' # ?
                         r'Previous Balance|' # history
                         r'Previous Charges' # history
                         r')[ \n\r]+Activity Date.*?'
                         r'(Total|Unpaid Balance, [iI]f Any)[\S ]*',
                         re.DOTALL)
RENT_LINE_RE = re.compile(r'\s+')

def parseamount(string):
    """
    Convert string of style -$24,705.75 to float -24705.75
    """
    return float(string.replace(',', '').replace('$', '').replace('*', ''))


def split(string):
    """
    Split a string by any time there are multiple spaces
    """
    return SPLIT_RE.split(string.strip())


def parsedate(string):
    """
    Use dateutil to parse an ambiguous date string into YYYY-MM-DD
    """
    return parser.parse(string).strftime('%Y-%m-%d') #pylint: disable=no-member


def extract(bbl, text): #pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """
    Extract Quarterly Statement of Account data from text

    Yields a dict for each piece of data.
    """

    # Unfortunately, STATEMENT filenames are laid out like BILLs sometimes...
    try:
        activity_through = parsedate(ACTIVITY_THROUGH[BILL].search(text).group(1))
    except AttributeError:
        activity_through = parsedate(ACTIVITY_THROUGH[STATEMENT].search(text).group(1))

    base = {
        'bbl': bbl,
        'activityThrough': activity_through
    }

    owner_address_area = OWNER_ADDRESS_AREA.search(text).groups()
    owner_address_split = [split(x) for x in owner_address_area][:-1]

    owner_name = owner_address_split[0][0]
    data = base.copy()
    data.update({
        'key': 'Owner name',
        'value': owner_name
    })
    yield data

    mailing_address = '\\n'.join(x[1] if len(x) > 1 else '' for x in owner_address_split).strip()
    data = base.copy()
    data.update({
        'key': 'Mailing address',
        'value': mailing_address
    })
    yield data

    # Exemption lines
    matches = EXEMPTIONS_RE.finditer(text)
    for match in matches:
        for i, line in enumerate(match.group().split('\n')):
            if i == 0:
                continue
            cells = split(line)
            splitcell = UNITS_RE.split(cells[0])
            if len(splitcell) > 1:
                cells[0] = splitcell[0].strip()
                cells.insert(1, splitcell[1].strip())

            data = base.copy()
            data['key'] = cells[0]
            data['section'] = 'exemptions'
            if len(cells) == 1:
                continue
            elif len(cells) == 2:
                continue
            else:
                data['value'] = parseamount(cells[-1])

            if len(cells) > 3:
                if cells[1].lower().endswith('units'):
                    data['apts'] = int(cells[1].lower().replace(' units', ''))
                else:
                    data['meta'] = cells[1]

            yield data

            #import pdb
            #pdb.set_trace()

    # All other lines
    matches = SECTIONS_RE.finditer(text)
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

        section = split(lines[0])[0]

        for i, line in enumerate(lines):
            key = None
            meta = None
            stabilization_due_date = None
            activity_date = None
            value = None
            apts = None

            line_unstripped = line
            line = line.strip()
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
                # if len(cells) > 5 and cells[1] != '# Apts':
                #     if cells[0].lower().startswith('activity date'):
                #         continue
                #     due_date = parsedate(cells[1])
                pass # since this is an inaccurate way of establishing a due
                     # date...
            elif i == 2:
                if cells[0].lower().startswith('activity date'):
                    continue

            if line_unstripped.startswith('\f') or \
               line_unstripped.startswith('\v') or \
               cells[0].lower().startswith('pay today') or \
               cells[0].lower().startswith('home banking payment instructions'):
               # or cells[0].lower().startswith('please include this coupon'):
                form_feed = True
                continue

            if line == '':
                continue
            elif 'rent stabilization fee' in cells[0].lower():
                continue
            elif cells[0].startswith('Activity Date'):
                continue
            elif cells[0] == 'Housing-Rent Stabilization':
                rent_line = RENT_LINE_RE.split(line)
                key = ' '.join(rent_line[0:2])
                if len(rent_line) < 4:
                    raise Exception('Unable to parse rent stabilization line')
                elif len(rent_line) == 4:
                    due_date = parsedate(rent_line[2])
                    value = parseamount(rent_line[3])
                elif len(rent_line) == 5:
                    raise Exception('Unable to parse rent stabilization line')
                else:
                    apts = int(rent_line[2])
                    due_date = parsedate(rent_line[3])
                    meta = ' '.join(rent_line[4:len(rent_line)-1])
                    value = parseamount(rent_line[len(rent_line)-1])
            elif len(cells) == 2:
                key = cells[0]
                value = parseamount(cells[1])
            elif len(cells) == 3:
                key = cells[0]
                try:
                    activity_date = parsedate(cells[1])
                except:  #pylint: disable=bare-except
                    meta = cells[1]
                value = parseamount(cells[2])
            elif len(cells) == 4:
                key = cells[0]
                try:
                    activity_date = parsedate(cells[1])
                    meta = cells[2]
                except:  #pylint: disable=bare-except
                    activity_date = parsedate(cells[2])
                    meta = cells[1]
                value = parseamount(cells[3])
            else:
                if 'State law recently changed' in line:
                    continue
                elif 'Due to this change,' in line:
                    continue
                #import pdb
                #pdb.set_trace()

            data = base.copy()
            data.update({
                'key': key,
                'value': value,
                'dueDate': stabilization_due_date or due_date,
                'activityDate': activity_date,
                'meta': meta,
                'apts': apts,
                'section': section
            })
            yield data


def main(root):
    """
    Process a list of filenames with Quarterly Statement of Account data.
    """
    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    for path, _, files in os.walk(root):
        for filename in files:
            if BILL not in filename and STATEMENT not in filename:
                continue

            if 'corrupted' in filename:
                continue

            try:
                bbl = path.split(os.path.sep)[-3:]
                pdf_path = os.path.join(path, filename)
                text_path = pdf_path.replace('.pdf', '.txt')
                if not os.path.exists(text_path):
                    try:
                        subprocess.check_call("pdftotext -layout '{}'".format(
                            pdf_path
                        ), shell=True)
                    except subprocess.CalledProcessError as err:
                        LOGGER.info('Moving & trying to repair %s', pdf_path)
                        subprocess.check_call("mv '{}' '{}'".format(
                            pdf_path, os.path.join(path, 'corrupted_' + filename)
                        ), shell=True)
                        subprocess.check_call("./download.py {}".format(
                            ' '.join(bbl)
                        ), shell=True)

                # date = path.split(os.path.sep)[-1].split(' - ')
                with open(text_path, 'r') as handle:
                    for data in extract(''.join(bbl), handle.read()):
                        writer.writerow(data)
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.warn(traceback.format_exc())
                LOGGER.warn('Could not parse %s, error: %s', os.path.join(path, filename), err)


if __name__ == '__main__':
    main(sys.argv[1])
