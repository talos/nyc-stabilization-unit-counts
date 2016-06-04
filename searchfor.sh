#!
find data/ -name "*.pdf" -exec pdftotext -layout {} \; -print 
find data/ -name "*.txt" -exec grep -H "\\$" {} \; -print |egrep -i 'unpaid|outstanding charges'|grep -v "\$0.00" >unpaid_trainingdata.txt
find data/ -name "*.txt" -exec grep -Hi "property address" {} \;  >propertyaddress_trainingdata.txt

# sed -r "s/(.*)[$](.*)/\2 , http://taxbills.nyc/\1/" unpaid_trainingdata.txt |sed "s/:/,/" | sort -rn | tee unpaid_sorted.csv
sed "s/:/\t/" unpaid_trainingdata.txt |sed "s/data\///" | sed -r "s?(.*)[$](.*)?\2 \t http://taxbills.nyc/\1?" | sort -rn | tee unpaid_sorted.tsv
grep 2016 unpaid_sorted.tsv  |sed "s?\(/[0-9][0-9][0-9][0-9]/\).*?\1?" |sed 's/^/"/' | sed 's/\t/",/' |tee unpaid_sorted_with_link.csv
# add https://city.tidalforce.org/#!/item/1017180119 and https://taxhistory.brooklyncoop.org/view1/1017180119

# ./createcsv.py *_traindata.txt
