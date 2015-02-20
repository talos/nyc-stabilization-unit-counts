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


def handle_double_dot(session, link_text, list_url, href):
  return urlparse.urljoin(list_url, href)


def handle_soalist(session, link_text, list_url, href):
  link_url = urlparse.urljoin(list_url, href)

  link_resp = session.get(link_url, headers={'Referer': list_url})
  link_soup = bs4.BeautifulSoup(link_resp.text)

  statement_href = link_soup.select('a[href^="../../StatementSearch"]')[0].get('href')
  return urlparse.urljoin(list_url, statement_href)


def strain_soup(list_url, bbl, session, soup, target, get_statement_url):
  '''
  iterate over html based on an href value
  '''
  for statement in soup.select(target):
    link_text = statement.text.strip()
    href = statement.get('href')
    bbldir = os.path.join('data', bbl)

    if link_text in os.listdir(bbldir):
      LOGGER.info(u'Already downloaded "{}" for BBL {}, skipping'.format(
        link_text, bbl))
      continue

    statement_url = get_statement_url(session, link_text, list_url, href)
    LOGGER.info(u'Downloading {0}: {1}'.format(link_text, statement_url))

    filename = os.path.join(bbldir, link_text)
    resp = session.get(statement_url, headers={'Referer': list_url}, stream=True)
    content_type = resp.headers['Content-Type']

    if 'html' in content_type:
      extension = 'html'
    elif 'pdf' in content_type:
      extension = 'pdf'

    chunk_size = 1024
    with open(filename + '.' + extension, 'wb') as fd:
      for chunk in resp.iter_content(chunk_size):
        fd.write(chunk)

    time.sleep(1)


def main(houseNumber, street, borough):
  LOGGER.info(u'Pulling down {0} {1}, {2}'.format(houseNumber, street, borough))
  session = requests.session()
  resp = session.post(FIND_BBL_URL, data={
    'FBORO':borough,
    'FSTNAME':street,
    'FHOUSENUM':houseNumber})

  # Extract necessary form content based off of address
  soup = bs4.BeautifulSoup(resp.text)
  list_url = soup.form.get('action').lower()
  inputs = soup.form.findAll('input')
  form = dict([(input.get('name'), input.get('value')) for input in inputs])

  # Get property tax info page
  bbl = '{}-{}-{}'.format(form['q49_boro'],
                          form['q49_block_id'],
                          form['q49_lot'])
  if not os.path.exists(os.path.join('data', bbl)):
    os.makedirs(os.path.join('data', bbl))

  resp = session.post(list_url, data=form)
  soup = bs4.BeautifulSoup(resp.text)

  strain_soup(list_url, bbl, session, soup, 'a[href^="../../"]', handle_double_dot)
  strain_soup(list_url, bbl, session, soup, 'a[href^="soalist.jsp"]', handle_soalist)

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
