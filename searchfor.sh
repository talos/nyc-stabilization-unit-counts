#!
find data/ -name "*.pdf" -exec pdftotext {} \; -print 
find data/ -name "*.txt" -exec grep -H "\\$" {} \; -print |grep -i unpaid|grep -v "\$0.00"
