#!/bin/bash

# Upload PDFs that have been converted to text to S3, then delete

find data/ -iname *.pdf | while read pdf; do
  filename=$(basename "$pdf" .pdf)
  path=$(dirname "$pdf")
  txtpath="$path/$filename.txt"

  if [ -e "$txtpath" ]; then
    aws s3 cp "$pdf" "s3://taxbills.nyc/$pdf" --acl public-read && rm "$pdf"
  fi
done
