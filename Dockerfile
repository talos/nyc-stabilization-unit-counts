FROM python:2.7

WORKDIR nyc-stabilization-unit-counts

RUN apt-get update
RUN apt-get install -yq libxml2-dev libxslt1-dev xpdf postgresql-client

RUN pwd

COPY ./requirements.txt .
RUN pip install -r requirements.txt
