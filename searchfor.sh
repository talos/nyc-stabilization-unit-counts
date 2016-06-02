#!
find data/ -name "*.txt" -exec grep -H "\\$" {} \; -print |grep -i unpaid
