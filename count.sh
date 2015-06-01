#!/bin/bash -e

COUNT=$(find /data/*/*/* -type d | wc -l)
echo "$(date +'%F %T')	$COUNT"
