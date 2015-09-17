#!/bin/bash -e

# Upload PDFs that have been converted to text to S3, then delete

find data/ -iname *.pdf | head -n 100 | while read pdf; do
  #echo "$pdf"
  filename=$(basename "$pdf" .pdf)
  path=$(dirname "$pdf")
  txtpath="$path/$filename.txt"

  if [ -e "$txtpath" ]; then
    aws s3 cp "$pdf" "s3://taxbills.nyc/$pdf" --acl public-read
    rm "$pdf"
  fi
done
