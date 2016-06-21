#!
# find taxbills/ -name "*.txt" -exec grep -H "\\$" {} \; -print |egrep -i 'unpaid|outstanding charges'|grep -v "\$0.00" >unpaid_trainingdata.txt.taxbills
# find taxbills/ -name "*.txt" -exec grep -Hi "property address" {} \;  >propertyaddress_trainingdata.txt.taxbills

sed "s/:/\t/" unpaid_trainingdata.txt.taxbills |sed "s/data\///" | sed -r "s?(.*)[$](.*)?\2 \t http://taxbills.nyc/\1?" | sort -rn | tee unpaid_sorted.tsv
grep 2016 unpaid_sorted.tsv  |sed "s?\(/[0-9][0-9][0-9][0-9]/\).*?\1?" |sort -u |sort -rn |sed 's/^/"/' | sed 's/\t/",/' |tee unpaid_sorted_with_link.csv
echo amount,bbl,link1,link2,link3 >unpaid_report.csv
sed "s?\(.*\),.*\([0-9]/.*/[0-9][0-9][0-9][0-9]/\).*?\1,\2,_SSS_:\2 _XXX_:\2 _YYY_:\2?" unpaid_sorted_with_link.csv  |sed  "s?/??g" | sed "s?_SSS_:?http://nycprop.nyc.gov/nycproperty/StatementSearch\?stmtDate=20160603\&stmtType=SOA\&bbl=?" | sed "s?_XXX_:?,https://city.tidalforce.org/#\!/item/?" |sed "s?_YYY_:?,https://taxhistory.brooklyncoop.org/view1/?" >> unpaid_report.csv
### 
### # add address sed "s?\(.*\),.*\([0-9]/.*/[0-9][0-9][0-9][0-9]/\).*?grep '\2' *prop*train*.txt?" unpaid_sorted_with_link.csv |bash |grep 2016
### # add https://city.tidalforce.org/#!/item/1017180119 and https://taxhistory.brooklyncoop.org/view1/1017180119
### # http://nycprop.nyc.gov/nycproperty/StatementSearch?bbl=1013770064&stmtDate=20160603&stmtType=SOA
### 
echo bbl,address >property_mapping.csv
sed "s?\(.*\)\([0-9]/.*/[0-9][0-9][0-9][0-9]/\).*:\(.*\)?\2 \3?" propertyaddress_trainingdata.txt.taxbills  |sed "s/  */ /g" |sort -u |sed "s?/??g" |sed "s/ /,/" |grep PROPERTY |iconv -f latin1 -t ascii//TRANSLIT --unicode-subst=ERROR1 --byte-subst=ERROR2   --widechar-subst=ERROR3 >> property_mapping.csv



### find data/ -name "*.pdf" -exec pdftotext -layout {} \; -print 
### find data/ -name "*.txt" -exec grep -H "\\$" {} \; -print |egrep -i 'unpaid|outstanding charges'|grep -v "\$0.00" >unpaid_trainingdata.txt
### find data/ -name "*.txt" -exec grep -Hi "property address" {} \;  >propertyaddress_trainingdata.txt
### 
### # sed -r "s/(.*)[$](.*)/\2 , http://taxbills.nyc/\1/" unpaid_trainingdata.txt |sed "s/:/,/" | sort -rn | tee unpaid_sorted.csv
### sed "s/:/\t/" unpaid_trainingdata.txt |sed "s/data\///" | sed -r "s?(.*)[$](.*)?\2 \t http://taxbills.nyc/\1?" | sort -rn | tee unpaid_sorted.tsv
### grep 2016 unpaid_sorted.tsv  |sed "s?\(/[0-9][0-9][0-9][0-9]/\).*?\1?" |sort -u |sort -rn |sed 's/^/"/' | sed 's/\t/",/' |tee unpaid_sorted_with_link.csv
### 
### # sed 's?(/[0-9][0-9][0-9][0-9]/).*?\1?' unpaid_sorted_with_link.csv |tee x.csv
### echo amount,bbl,link1,link2,link3 >unpaid_report.csv
### sed "s?\(.*\),.*\([0-9]/.*/[0-9][0-9][0-9][0-9]/\).*?\1,\2,_SSS_:\2 _XXX_:\2 _YYY_:\2?" unpaid_sorted_with_link.csv  |sed  "s?/??g" | sed "s?_SSS_:?http://nycprop.nyc.gov/nycproperty/StatementSearch\?stmtDate=20160603\&stmtType=SOA\&bbl=?" | sed "s?_XXX_:?,https://city.tidalforce.org/#\!/item/?" |sed "s?_YYY_:?,https://taxhistory.brooklyncoop.org/view1/?" >> unpaid_report.csv
### 
### # add address sed "s?\(.*\),.*\([0-9]/.*/[0-9][0-9][0-9][0-9]/\).*?grep '\2' *prop*train*.txt?" unpaid_sorted_with_link.csv |bash |grep 2016
### # add https://city.tidalforce.org/#!/item/1017180119 and https://taxhistory.brooklyncoop.org/view1/1017180119
### # http://nycprop.nyc.gov/nycproperty/StatementSearch?bbl=1013770064&stmtDate=20160603&stmtType=SOA
### 
### # ./createcsv.py *_traindata.txt
### echo bbl,address >property_mapping.csv
### sed "s?\(.*\)\([0-9]/.*/[0-9][0-9][0-9][0-9]/\).*:\(.*\)?\2 \3?" propertyaddress_trainingdata.txt  |sed "s/  */ /g" |sort -u |sed "s?/??g" |sed "s/ /,/" |grep PROPERTY |iconv -f latin1 -t ascii//TRANSLIT --unicode-subst=ERROR1 --byte-subst=ERROR2   --widechar-subst=ERROR3 >> property_mapping.csv
### 
