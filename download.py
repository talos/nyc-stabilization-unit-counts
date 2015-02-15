#!/usr/bin/env python

import sys
import requests
import bs4
import urlparse
import time
import os


FIND_BBL_URL = 'http://webapps.nyc.gov:8084/CICS/fin1/find001i'


def main(houseNumber, street, borough):
  sys.stderr.write(u'{0} {1}, {2}\n'.format(houseNumber, street, borough))
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
  if not os.path.exists(bbl):
    os.mkdir(bbl)
  resp = session.post(list_url, data=form)

  soup = bs4.BeautifulSoup(resp.text)

  for statement in soup.select('a[href^="../../"]'):
    link_text = statement.text.strip()
    href = statement.get('href')
    statement_url = urlparse.urljoin(list_url, href)
    sys.stderr.write(u'{0}: {1}\n'.format(link_text, statement_url))

    filename = os.path.join(bbl, link_text)
    if os.path.exists(filename):
      continue

    resp = session.get(statement_url, stream=True)

    chunk_size = 1024
    with open(filename, 'wb') as fd:
      for chunk in resp.iter_content(chunk_size):
        fd.write(chunk)

    time.sleep(1)


if __name__ == '__main__':
  main(sys.argv[1], sys.argv[2], sys.argv[3])
