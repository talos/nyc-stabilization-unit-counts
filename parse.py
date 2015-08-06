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
    "section",
    "key",
    "dueDate",
    "activityDate",
    "value",
    "meta",
    "apts"
]

BILL_PDF, STATEMENT_PDF, STATEMENT_HTML, NOPV_PDF, NOPV_HTML = (
    'Quarterly Property Tax Bill.pdf', 'Quarterly Statement of Account.pdf',
    'Quarterly Statement of Account.html', 'Notice of Property Value.pdf',
    'Notice of Property Value.html')
ACTIVITY_THROUGH = {
    BILL_PDF: re.compile(r'Activity through (.*)', re.IGNORECASE),
    STATEMENT_PDF: re.compile(r'Last Statement Through (.*?)\)', re.IGNORECASE)
}
OWNER_ADDRESS_AREA = re.compile(
    r'Owner name:(.*)Property address:(.*)Borough, block & lot:(.*)'
    r'(Outstanding\s+Charges|Statement\s+Billing\s+Summary)', re.DOTALL + re.IGNORECASE
)
PROPERTY_TAX_DETAIL_AREA = re.compile(
    'Annual Property Tax Detail.*Annual property tax.*?\n', re.DOTALL)

SPLIT_RE = re.compile(r'\s{2,}')
SPLIT_X_RE = re.compile(r'[\sX$]{2,}')
EXEMPTIONS_RE = re.compile(r'(Tax [Bb]efore [Ee]xemptions [Aa]nd [Aa]batements'
                           r'.*?Tax [Bb]efore [Aa]batements)', re.DOTALL)
UNITS_RE = re.compile(r'(\d+ [Uu]nits)')
SECTIONS_RE = re.compile(r'(Charges You Can Pre-pay|'  # prepayment
                         r'Amount Not Due [bB]ut That Can [bB]e Paid Early|'  #prepayment
                         r'Tax Year Charges Remaining|' # prepayment
                         r'Current Amount Due|' # due
                         r'Current Charges|' # due
                         r'Overpayments/[Cc]redits|' # ?
                         r'Payment Agreement|' # ?
                         r'Previous Balance|' # history
                         r'Previous Charges' # history
                         r')[ \n\r]+Activity Date.*?'
                         r'(Total|Unpaid Balance, [iI]f Any)[\S ]*',
                         re.DOTALL)
RENT_LINE_RE = re.compile(r'\s+')
GROSS_INCOME_RE = re.compile(r'(\s*Gross Income:\s*We estimated gross income at \$(.*)\.|'
                             r'Estimated Gross Income:\s*\$(.*))')
EXPENSES_RE = re.compile(r'(\s*Expenses:\s*We estimated expenses at \$(.*)\.|'
                         r'Estimated Expenses:\s*\$(.*))')

def parseamount(string):
    """
    Convert string of style -$24,705.75 to float -24705.75
    """
    return float(string.replace(',', '').replace('$', '').replace('*', '').replace('X', ''))


def split(string, with_x=False):
    """
    Split a string by any time there are multiple spaces
    """
    if with_x:
        return SPLIT_X_RE.split(string.strip())
    else:
        return SPLIT_RE.split(string.strip())


def parsedate(string):
    """
    Use dateutil to parse an ambiguous date string into YYYY-MM-DD
    """
    return parser.parse(string).strftime('%Y-%m-%d') #pylint: disable=no-member


def extract_statement_pdf(text): #pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """
    Extract Quarterly Statement of Account data from text

    Yields a dict for each piece of data.
    """

    # Unfortunately, STATEMENT filenames are laid out like BILLs sometimes...
    #try:
    #    activity_through = parsedate(ACTIVITY_THROUGH[BILL_PDF].search(text).group(1))
    #except AttributeError:
    #    activity_through = parsedate(ACTIVITY_THROUGH[STATEMENT_PDF].search(text).group(1))

    owner_address_area = OWNER_ADDRESS_AREA.search(text).groups()
    owner_address_split = [split(x) for x in owner_address_area][:-1]

    owner_name = owner_address_split[0][0]
    yield {
        'key': 'Owner name',
        'value': owner_name
    }

    mailing_address = '\\n'.join(x[1] if len(x) > 1 else '' for x in owner_address_split).strip()
    yield {
        'key': 'Mailing address',
        'value': mailing_address
    }

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

            data = {}
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


    # Detail area
    detail_area = PROPERTY_TAX_DETAIL_AREA.search(text)
    if detail_area:
        lines = detail_area.group().split('\n')
        section = 'details'
        abatementsFlag = False
        exemptionsFlag = False
        for i, line in enumerate(lines):
            key = None
            value = None
            meta = None
            apts = None

            if line:
                cells = split(line, with_x=True)

                if not cells[0]:
                    continue
                elif cells[0].startswith('Tax class'):
                    key = u'Tax class'
                    value = cells[0].split(key)[1]
                elif cells[0].startswith('Current tax rate'):
                    key = cells[0]
                    value = cells[1]
                elif cells[0].startswith('Estimated market value'):
                    key = cells[0]
                    value = parseamount(cells[1])
                elif cells[0].startswith('Tax before exemptions and abatements'):
                    section = 'details'
                    key = cells[0]
                    try:
                        meta = parseamount(cells[1])
                    except ValueError:
                        apts = cells[1]
                        meta = parseamount(cells[2])
                    if len(cells) > 2:
                        value = parseamount(cells[-1])
                    else:
                        value = parseamount(split(lines[i + 1])[-1])  
                    exemptionsFlag = True

                elif cells[0].startswith('Tax before abatements'):
                    section = 'details'
                    key = cells[0]
                    try:
                        meta = parseamount(cells[1])
                    except ValueError:
                        apts = cells[1]
                        meta = parseamount(cells[2])

                    value = parseamount(cells[-1])
                    #Still not sure what we are checking for here, but under normal conditions
                    #this line is only 2 cells, and the desired value is cells[-1]
                    #if len(cells) > 2:
                        #value = parseamount(cells[-1])
                    #else:
                        #value = parseamount(split(lines[i + 1])[-1])

                    abatementsFlag = True

                elif cells[0].startswith('Annual property tax'):
                    section = 'details'
                    key = cells[0]
                    value = parseamount(cells[-1])
                elif abatementsFlag:
                    section = 'details-abatements'
                    key = cells[0]
                    if len(cells) > 2:
                        try:
                            meta = parseamount(cells[1])
                        except ValueError:
                            apts = cells[1]
                            meta = parseamount(cells[2])
                    value = parseamount(cells[-1])

                elif exemptionsFlag:
                    section = 'details-exemptions'
                    key = cells[0]
                    if len(cells) > 2:
                        try:
                            meta = parseamount(cells[1])
                        except ValueError:
                            apts = cells[1]
                            meta = parseamount(cells[2])
                    value = parseamount(cells[-1])


                yield {
                    'section': section,
                    'apts': apts,
                    'key': key,
                    'value': value,
                    'meta': meta,
                }

    # All other lines
    matches = SECTIONS_RE.finditer(text)
    for match in matches:
        # todo due_date actually needs to be figured out by determining which
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

            yield {
                'key': key,
                'value': value,
                'dueDate': stabilization_due_date or due_date,
                'activityDate': activity_date,
                'meta': meta,
                'apts': apts,
                'section': section
            }


def _html_owner_name(html):
    '''
    Obtain owner name from soup
    '''
    #elem = soup.find(text=re.compile('Owner Name:'))
    #return [c for c in elem.parent.parent.children][-1].strip()
    match = re.search(r'Owner Name:.*?<img[^>]*>([^<]*)<', html, re.IGNORECASE)
    return match.group(1).strip()


def _html_rent_stabilized(html):
    """
    Extract every rent stabilized line from the soup.
    """
    #els = soup.find_all(text=re.compile('Housing-Rent Stabilization'))
    #import pdb
    #pdb.set_trace()
    for section in re.finditer(r'(Current Amount Due|'
                               r'Amount Not Due [bB]ut That Can be Paid Early|'
                               r'New Charges Due \w+ \d{2}, \d{4}|'
                               r'Remaining Balance/Credits from Your Last Statement|'
                               r'Previous Balance'
                               r')[^_]+?Activity Date.*?'
                               r'_________________', html, re.DOTALL):
        section_type = section.group(1)
        section_text = section.group()
        for match in re.finditer(r'(Housing-Rent Stabilization.*?)<', section_text, re.IGNORECASE):
            housing_rent, stabilization, num_apts, date, id1, id2, payment = \
                    re.split(r'\s+', match.group(1).strip())
            yield {
                'key': ' '.join([housing_rent, stabilization]),
                'section': section_type,
                'apts': num_apts,
                'value': payment,
                'dueDate': parsedate(date),
                'meta': id1 + ' ' + id2
            }

def _html_mailing_address(soup):
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


def extract_statement_html(html):
    """
    Extract Quarterly Statement of Account data from HTML

    Yields a dict for each piece of data.
    """
    #soup = BeautifulSoup(html)

    #activity_through = _html_activity_through(html)

    yield {
        'key': 'Owner name',
        'value': _html_owner_name(html)
    }

    # mailing_address = _html_mailing_address(html)
    # base.update({
    #     'key': 'Mailing address',
    #     'value': mailing_address
    # })
    # yield base

    for rent_stabilized in _html_rent_stabilized(html):
        yield rent_stabilized


def extract_nopv(text):
    """
    Extract notice of property value data.

    Yields a dict for each piece of data.
    """
    income = GROSS_INCOME_RE.search(text)
    if income:
        yield {
            'key': 'gross income',
            'section': 'nopv',
            'value': parseamount(income.group(2) or income.group(3))
        }
    expenses = EXPENSES_RE.search(text)
    if expenses:
        yield {
            'key': 'expenses',
            'section': 'nopv',
            'value': parseamount(expenses.group(2) or income.group(3))
        }


def _convert_to_txt(pdf_path, bbl_array):
    """
    Convert a PDF to text if it hasn't been already.  Returns the path to the
    new text file.

    If it's unable to parse an existing PDF, tries to redownload it using
    bbl_array.
    """
    text_path = pdf_path.replace('.pdf', '.txt')
    if not os.path.exists(text_path):
        try:
            subprocess.check_call("pdftotext -layout '{}'".format(
                pdf_path
            ), shell=True)
        except subprocess.CalledProcessError as err:
            LOGGER.info('Moving & trying to repair %s (%s)', pdf_path, err)
            subprocess.check_call("mv '{}' '{}'".format(
                pdf_path, os.path.join(pdf_path, pdf_path + '_corrupted')
            ), shell=True)
            subprocess.check_call("./download.py {}".format(
                ' '.join(bbl_array)
            ), shell=True)
    return text_path


def main(root): #pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """
    Process a list of filenames with Quarterly Statement of Account data.
    """
    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    for path, _, files in os.walk(root):
        for filename in files:
            LOGGER.warn(filename);
            try:
                if 'corrupted' in filename:
                    continue

                handler = None
                bbl_array = path.split(os.path.sep)[-3:]

                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(path, filename)
                    data_path = _convert_to_txt(pdf_path, bbl_array)
                else:
                    data_path = os.path.join(path, filename)

                if BILL_PDF in filename or STATEMENT_PDF in filename:
                    handler = extract_statement_pdf
                elif NOPV_PDF in filename or NOPV_HTML in filename:
                    handler = extract_nopv
                elif STATEMENT_HTML in filename:
                    handler = extract_statement_html

                if handler:
                    with open(data_path, 'r') as handle:
                        file_data = handle.read()
                    activity_through = parsedate(filename.split(' - ')[0])
                    for data in handler(file_data):
                        base = {
                            'bbl': ''.join(bbl_array),
                            'activityThrough': activity_through
                        }
                        base.update(data)
                        writer.writerow(base)

            except Exception as err:  # pylint: disable=broad-except
                LOGGER.warn(traceback.format_exc())
                LOGGER.warn('Could not parse %s, error: %s', os.path.join(path, filename), err)

if __name__ == '__main__':
    main(sys.argv[1])