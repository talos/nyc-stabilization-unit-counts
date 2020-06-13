#!/usr/bin/env python

'''
Convert quarterly property tax bill into CSV
'''

import json
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

ROW_BUFFER = 1

BILL_PDF, STATEMENT_PDF, STATEMENT_HTML, NOPV_PDF, NOPV_HTML = (
    'Quarterly Property Tax Bill.txt', 'Quarterly Statement of Account.txt',
    'Quarterly Statement of Account.html', 'Notice of Property Value.txt',
    'Notice of Property Value.html')
ACTIVITY_THROUGH = {
    BILL_PDF: re.compile(r'Activity through (.*)', re.IGNORECASE),
    STATEMENT_PDF: re.compile(r'Last Statement Through (.*?)\)', re.IGNORECASE)
}
OWNER_ADDRESS_AREA = re.compile(
    r'Owner name:(.*)Property address:(.*)Borough, block & lot:(.*)'
    r'(Statement\s+Billing\s+Summary|Statement\s+Details)', re.DOTALL + re.IGNORECASE) #r'(Outstanding\s+Charges|Statement\s+Billing\s+Summary)'
PROPERTY_TAX_DETAIL_AREA = re.compile(
    '(Annual [Pp]roperty [Tt]ax [Dd]etail|How We Calculated Your Property Tax).*'
    '[Aa]nnual [Pp]roperty [Tt]ax.*?\n', re.DOTALL + re.IGNORECASE)

STABILIZED_RE = re.compile(r'(Current Amount Due|'
                           r'Amount Not Due [bB]ut That Can be Paid Early|'
                           r'New Charges Due \w+ \d{2}, \d{4}|'
                           r'Remaining Balance/Credits from Your Last Statement|'
                           r'Previous Balance'
                           r')[^_]+?Activity Date.*?'
                           r'_________________')

SPLIT_RE = re.compile(r'\s{2,}')
SPLIT_X_RE = re.compile(r'[\sX$]{2,}')
UNITS_RE = re.compile(r'(\d+ [Uu]nits)')
SECTIONS_RE = re.compile(r'(Charges You Can Pre-pay|'  # prepayment
                         r'If you want to pay everything .* please pay|'  #prepayment r'Amount Not Due [bB]ut That Can [bB]e Paid Early|'
                         r'If you pay everything .* you would save|'  #prepayment
                         r'Tax Year Charges Remaining|' # prepayment
                         r'Total Amount Due|' # due r'Current Amount Due|'
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

    # Detail area
    detail_area = PROPERTY_TAX_DETAIL_AREA.search(text)
    if detail_area:
        lines = detail_area.group().split('\n')
        section = 'details'
        abatements_flag = False
        exemptions_flag = False
        revocation_flag = False
        for i, line in enumerate(lines):
            key = None
            value = None
            meta = None
            apts = None

            if i == 0:
                continue

            if line:
                cells = split(line, with_x=True)

                if not cells[0]:
                    continue

                cell0 = cells[0].lower()

                if cell0 in ('value', 'tax rate', 'overall'):
                    continue
                elif cell0.startswith('tax class'):
                    key = u'tax class'
                    value = cell0.split(key)[1]
                elif cell0.startswith('current tax rate'):
                    key = cell0
                    value = cells[1]
                elif cell0.startswith('estimated market value'):
                    key = cell0
                    value = parseamount(cells[1])
                elif cell0.startswith('billable assessed value'):
                    key = cell0
                    value = parseamount(cells[1])
                elif cell0.startswith('taxable value'):
                    section = 'details'
                    key = cell0
                    splitcells = cells[1].split(' ',3)
                    meta = parseamount(splitcells[0]) #parseamount(cells[1])
                    value = splitcells[2]
                    exemptions_flag = True
                elif cell0.startswith('tax before exemptions and abatements'):
                    section = 'details'
                    key = cell0
                    meta = parseamount(cells[1])
                    value = parseamount(cells[-1])
                    exemptions_flag = True
                elif cell0.startswith('tax before abatements'):
                    section = 'details'
                    key = cell0
                    meta = parseamount(cells[1])
                    value = parseamount(cells[-1])
                    if value == meta:
                        meta = None
                    abatements_flag = True
                elif cell0 == 'annual property tax':
                    section = 'details'
                    key = cell0
                    value = parseamount(cells[-1])
                elif cell0.startswith('original tax rate'):
                    section = 'details'
                    key = 'original tax rate'
                    meta = cell0.split(key)[1]
                    value = cells[-1]
                elif cell0 == 'new tax rate':
                    section = 'details'
                    key = cell0
                    value = cells[-1]
                elif cell0 == 'revocation':
                    revocation_flag = True
                    continue
                elif cell0.startswith('damp'):
                        section = 'details'
                        key = "Damp / Article XI"
                        value = parseamount(cells[-1])
                elif cell0.startswith('article'):
                    if cells[1]== 'i':
                        section = 'details'
                        key = "Article XI"
                        value = parseamount(cells[-1])
                    else:
                        continue
                elif revocation_flag:
                    section = 'details-revocation'
                    key = cell0
                    value = parseamount(cells[-1])
                elif abatements_flag:
                    section = 'details-abatements'
                    key = cell0
                    if len(cells) > 2:
                        if len(cells[1].lower().split('unit')) > 1:
                            apts = int(cells[1].lower()\
                                       .replace(' units', '').replace(' unit', ''))
                            meta = parseamount(cells[2])
                        elif cells[1].endswith('%'):
                            meta = parseamount(cells[2])
                        else:
                            meta = parseamount(cells[1])

                    value = parseamount(cells[-1])
                elif exemptions_flag:
                    section = 'details-exemptions'
                    key = cell0
                    if len(cells) > 2:
                        if len(cells[1].lower().split('unit')) > 1:
                            apts = int(cells[1].lower()\
                                       .replace(' units', '').replace(' unit', ''))
                            meta = parseamount(cells[2])
                        elif cells[1].endswith('%'):
                            meta = parseamount(cells[2])
                        else:
                            meta = parseamount(cells[1])

                    value = parseamount(cells[-1])
                elif len(cells) == 1:
                    continue
                else:
                    key = cell0
                    value = parseamount(cells[-1])

                for unit in (' units', ' unit'):
                    if key.lower().endswith(unit):
                        key = key.lower().replace(unit, '')
                        apts = int(key.split(' ')[-1])
                        key = ' '.join(key.split(' ')[0:-1])

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
            due_date = None
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
            elif cells[0].lower().startswith('rent stabilization'):
                #print(cells[0].lower())
                if 'rent stabilization fee- chg' in cells[0].lower():
                    rent_line = RENT_LINE_RE.split(line) #line
                    #print(rent_line, len(rent_line))
                    key = ' '.join(rent_line[0:3])[:-1]
                    if len(rent_line) < 7:
                        raise Exception('Unable to parse rent stabilization line')
                    elif len(rent_line) == 7:
                        apts = int(rent_line[4]) #int(rent_line[2])
                        due_date = parsedate(rent_line[5]) #parsedate(rent_line[3])
                        value = parseamount(rent_line[-1]) #parseamount(rent_line[len(rent_line)-1])
                    else:
                        apts = int(rent_line[4]) #int(rent_line[2])
                        due_date = parsedate(rent_line[5]) #parsedate(rent_line[3])
                        meta = rent_line[6] #meta = ' '.join(rent_line[4:len(rent_line)-1])
                        value = parseamount(rent_line[7]) #parseamount(rent_line[len(rent_line)-1])
                else:
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
                if key.find('Tax')>0 or key.find('Fee')>0 or key.find('Chg')>0:
                    due_date = activity_date
                    activity_date=None
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
    for section in STABILIZED_RE.finditer(html, re.DOTALL):
        section_type = section.group(1)
        section_text = section.group()
        for match in re.finditer(r'((Housing-Rent Stabilization)|(Rent Stabilization Fee- Chg).*?)<', section_text, re.IGNORECASE):
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
            'value': parseamount(expenses.group(2) or expenses.group(3))
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
        if os.stat(pdf_path).st_size == 0:
            LOGGER.info('Deleting %s as it is empty', pdf_path)
            os.remove(pdf_path)
            return None
        try:
            subprocess.check_call("pdftotext -layout '{}'".format(
                pdf_path
            ), shell=True)
            LOGGER.info('Converted %s to text', pdf_path)
        except subprocess.CalledProcessError as err:
            #LOGGER.info('Skipping %s (%s) as it is corrupted', pdf_path, err)
            #return None
            LOGGER.info('Moving & trying to repair %s (%s)', pdf_path, err)
            cmd = "mv '{}' '{}'".format(
                pdf_path, pdf_path + '_corrupted'
            )
            subprocess.check_call(cmd, shell=True)
            return None
            #subprocess.check_call("./download.py {}".format(
            #    ' '.join(bbl_array)
            #), shell=True)
    return text_path


def main(root): #pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """
    Process a list of filenames with Quarterly Statement of Account data.
    """
    writer = csv.DictWriter(sys.stdout, HEADERS)
    writer.writeheader()
    dirs_processed = 0
    rows_to_write = []
    for path, _, files in os.walk(root):
        bbl_json = []
        for filename in files:
            try:
                if 'corrupted' in filename:
                    continue

                if 'data.json' in filename:
                    continue

                handler = None
                bbl_array = path.split(os.path.sep)[-3:]

                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(path, filename)
                    data_path = _convert_to_txt(pdf_path, bbl_array)
                    if data_path is None:
                        continue
                else:
                    data_path = os.path.join(path, filename)

                if BILL_PDF in data_path or STATEMENT_PDF in data_path:
                    handler = extract_statement_pdf
                elif NOPV_PDF in data_path or NOPV_HTML in data_path:
                    handler = extract_nopv
                elif STATEMENT_HTML in data_path:
                    handler = extract_statement_html
                else:
                    continue

                with open(data_path, 'r') as handle:
                    file_data = handle.read()
                activity_through = parsedate(filename.split(' - ')[0])
                for data in handler(file_data):
                    data['bbl'] = ''.join(bbl_array)
                    data['activityThrough'] = activity_through
                    #writer.writerow(base)
                    rows_to_write.append(data)
                    bbl_json.append(data)

            except Exception as err:  # pylint: disable=broad-except
                LOGGER.warn(traceback.format_exc())
                LOGGER.warn('Could not parse %s, error: %s', os.path.join(path, filename), err)
        with open(os.path.join(path, 'data.json'), 'w') as json_outfile:
            # TODO something is wrong here, for BBL http://taxbills.nyc/1/00274/0004/data.json an erroneous 243609 is appearing for nopv "gross income"/"expenses" instead of a much smaller number
            json.dump(bbl_json, json_outfile)
        dirs_processed += 1

        if len(rows_to_write) >= ROW_BUFFER:
            writer.writerows(rows_to_write)
            rows_to_write = []

        if dirs_processed % 1000 == 0:
            LOGGER.info('Dirs processed: %s', dirs_processed)

    writer.writerows(rows_to_write)


if __name__ == '__main__':
    main(sys.argv[1])
