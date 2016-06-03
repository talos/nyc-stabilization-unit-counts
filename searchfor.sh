#!
find data/ -name "*.pdf" -exec pdftotext -layout {} \; -print 
find data/ -name "*.txt" -exec grep -H "\\$" {} \; -print |grep -i unpaid|grep -v "\$0.00" >unpaid_trainingdata.txt
find data/ -name "*.txt" -exec grep -Hi "property address" {} \;  >propertyaddress_trainingdata.txt

# sed -r "s/(.*)[$](.*)/\2 , http://taxbills.nyc/\1/" unpaid_trainingdata.txt |sed "s/:/,/" | sort -rn | tee unpaid_sorted.csv
sed "s/:/,/" unpaid_trainingdata.txt | sed -r "s?(.*)[$](.*)?\2 , http://taxbills.nyc/\1?" | sort -rn | tee unpaid_sorted.csv

# ./createcsv.py *_traindata.txt
