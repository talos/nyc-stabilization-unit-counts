# Get BBLs from DOF's assessment roll.

YEAR=19
AVROLL="avroll_$YEAR"

wget "https://www1.nyc.gov/assets/finance/downloads/tar/$AVROLL.zip" -O data/$AVROLL.zip
unzip data/$AVROLL.zip -d data/
mdb-export -H data/$AVROLL.mdb avroll > data/$AVROLL.csv
cut -d , -f 1 data/$AVROLL.csv | tr -d '"' > "data/bbls_$YEAR.csv"
