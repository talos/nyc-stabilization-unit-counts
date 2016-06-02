#!
sudo apt-get install python-dev python-pip python-virtualenv \
                         build-essential libxml2-dev libxslt1-dev xpdf
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt

# python download.py <house no> '<street name with suffix>' <borough number>
python download.py : 49 'W. 119TH ST' 1

python parse.py testdata  |tee testoutput.csv
