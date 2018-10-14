#!/bin/bash

# Upload PDFs that have been converted to text to S3, then delete

find data/ -iname "*.pdf" | while read pdf; do
  filename=$(basename "$pdf" .pdf)
  path=$(dirname "$pdf")
  txtpath="$path/$filename.txt"

  if [ -e "$txtpath" ]; then
    echo "copy and delete $pdf"
    aws s3 cp "$pdf" "s3://taxbills.nyc/$pdf" --acl public-read && rm "$pdf"
  fi
done

find data/ -iname "*.txt" | while read txt; do
  filename=$(basename "$txt" .txt)
  path=$(dirname "$txt")

  echo "copy $txt"
  aws s3 cp "$txt" "s3://taxbills.nyc/$txt" --acl public-read
done

find data/ -iname "*.html" | while read html; do
  filename=$(basename "$html" .html)
  path=$(dirname "$html")

  echo "copy $html"
  aws s3 cp "$html" "s3://taxbills.nyc/$html" --acl public-read
done
