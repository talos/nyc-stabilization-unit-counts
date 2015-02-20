#!/usr/bin/env python

import sys
import requests
import bs4
import urlparse
import time
import os
import logging

FIND_BBL_URL = 'http://webapps.nyc.gov:8084/CICS/fin1/find001i'
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler(sys.stderr))
SESSION = requests.session()
DOCS_TO_DOWNLOAD = [
    u'Quarterly Statement of Account',  # Amounts paid, stabilized fees, other
                                        # charges, mailing address
    u'Quarterly Property Tax Bill',  # Amounts paid, stabilized fees, other
                                     # charges, mailing address, mortgagee
                                     # payer
    u'SCRIE Statement of Account',  # SCRIE amounts, mailing address
    u'Notice of Property Value',  # Estimated sq. footage, gross income,
                                  # expenses, RoI
    u'Tentative Assessment Roll',  # Real Estate billing name and address
                                   # (mortgagee payer)
]


def handle_double_dot(list_url, href):
    return urlparse.urljoin(list_url, href)


def handle_soalist(list_url, href):
    link_url = urlparse.urljoin(list_url, href)

    link_resp = SESSION.get(link_url, headers={'Referer': list_url})
    link_soup = bs4.BeautifulSoup(link_resp.text)

    statement_href = link_soup.select(
        'a[href^="../../StatementSearch"]')[0].get('href')
    return urlparse.urljoin(list_url, statement_href)


def find_extension(resp):
    """
    Extract whether a requests response is for HTML or PDF.
    """
    content_type = resp.headers['Content-Type']
    if 'html' in content_type:
        return 'html'
    elif 'pdf' in content_type:
        return 'pdf'


def save_file_from_stream(resp, filename):
    """
    Save a file from a streamed response
    """
    chunk_size = 1024
    with open(filename + '.' + find_extension(resp), 'wb') as fd:
        for chunk in resp.iter_content(chunk_size):
            fd.write(chunk)


def strain_soup(list_url, bbl, soup, target, get_statement_url):
    """
    Pull out all PDFs or HTML pages from a NYCServ soup, targetting certain
    links (`target`) and using `get_statement_url` to get the correct href for
    the actual statement.
    """
    for statement in soup.select(target):
        docname = statement.text.strip()
        if docname.split(' - ')[1] not in DOCS_TO_DOWNLOAD:
            LOGGER.info(u'Not worried about doctype "%s" for BBL %s, skipping',
                        docname, bbl)
            continue

        bbldir = os.path.join('data', bbl)
        filenames = ['.'.join(f.split('.')[:-1]) for f in os.listdir(bbldir)]
        if docname in filenames:
            LOGGER.info(u'Already downloaded "%s" for BBL %s, skipping',
                        docname, bbl)
            continue

        statement_url = get_statement_url(list_url, statement.get('href'))
        LOGGER.info(u'Downloading %s: %s', docname, statement_url)

        filename = os.path.join(bbldir, docname)
        resp = SESSION.get(statement_url, headers={'Referer': list_url},
                           stream=True)

        save_file_from_stream(resp, filename)

        time.sleep(1)


def main(houseNumber, street, borough):
    LOGGER.info(u'Pulling down %s %s, %s', houseNumber, street, borough)
    resp = SESSION.post(FIND_BBL_URL, data={
        'FBORO': borough,
        'FSTNAME': street,
        'FHOUSENUM': houseNumber})

    # Extract necessary form content based off of address
    soup = bs4.BeautifulSoup(resp.text)
    list_url = soup.form.get('action').lower()
    inputs = soup.form.findAll('input')
    form = dict([(i.get('name'), i.get('value')) for i in inputs])

    # Get property tax info page
    bbl = '{}-{}-{}'.format(form['q49_boro'],
                            form['q49_block_id'],
                            form['q49_lot'])
    if not os.path.exists(os.path.join('data', bbl)):
        os.makedirs(os.path.join('data', bbl))

    resp = SESSION.post(list_url, data=form)
    soup = bs4.BeautifulSoup(resp.text)

    strain_soup(list_url, bbl, soup, 'a[href^="../../"]', handle_double_dot)
    strain_soup(list_url, bbl, soup, 'a[href^="soalist.jsp"]', handle_soalist)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as infile:
            for line in infile:
                args = line.strip().split('\t')
                main(args[0], args[1], args[2])
    elif len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        sys.stderr.write(u'''

    Should be called with one arg for tab-delimited file, three args for
    housenum/streetname/borough number.

''')
        sys.exit(1)
