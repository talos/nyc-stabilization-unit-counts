#!
find data/ -name "*.pdf" -exec pdftotext -layout {} \; -print 
find data/ -name "*.txt" -exec grep -H "\\$" {} \; -print |grep -i unpaid|grep -v "\$0.00" >unpaid_trainingdata.txt
find data/ -name "*.txt" -exec grep -Hi "property address" {} \;  >propertyaddress_trainingdata.txt

# ./createcsv.py *_traindata.txt
