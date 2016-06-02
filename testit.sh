#!
find testdata -name "*.txt" -exec rm {} \; -print
# python parse.py testdata 2>&1 |tee testoutput_`date +%Y-%m-%d-%s`.csv
# python parse_ralph.py testdata 2>&1 |tee testoutput_`date +%Y-%m-%d-%s`.csv
python parse_unpaid.py testdata 2>&1 |tee testoutput_`date +%Y-%m-%d-%s`.csv
