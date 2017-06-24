#!/bin/bash -e

source .env/bin/activate
#python download.py input/allbbls3a.tsv >allbbls3a.log 2>&1 &
#python download.py input/allbbls3b.tsv >allbbls3b.log 2>&1 &
#python download.py input/allbbls3c.tsv >allbbls3c.log 2>&1 &
#python download.py input/allbbls3d.tsv >allbbls3d.log 2>&1 &
#python download_direct.py 20150605 input/pluto14v2noCondos.csv >pluto14v2noCondos.log 2>&1 &
#python download.py input/condobbls.csv >condobbls.log 2>&1 &
#python download.py input/pluto14v2noCondos.csv >pluto14v2noCondos.log 2>&1 &


#cat input/BX09v1.txt  | cut -d , -f 1-3 | tr -d ' ' | tr -d '"' | tr ',' '\t' | python download_direct.py 20090606 SOA > logs/20090606-bx-pluto.log 2>&1 &
#cat input/BK09v1.txt  | cut -d , -f 1-3 | tr -d ' ' | tr -d '"' | tr ',' '\t' | python download_direct.py 20090606 SOA > logs/20090606-bk-pluto.log 2>&1 &
#cat input/MN09v1.txt  | cut -d , -f 1-3 | tr -d ' ' | tr -d '"' | tr ',' '\t' | python download_direct.py 20090606 SOA > logs/20090606-mn-pluto.log 2>&1 &
#cat input/QN09v1.txt  | cut -d , -f 1-3 | tr -d ' ' | tr -d '"' | tr ',' '\t' | python download_direct.py 20090606 SOA > logs/20090606-qn-pluto.log 2>&1 &
#cat input/SI09v1.txt  | cut -d , -f 1-3 | tr -d ' ' | tr -d '"' | tr ',' '\t' | python download_direct.py 20090606 SOA > logs/20090606-si-pluto.log 2>&1 &



sort input/pluto14v2noCondos.bak.csv | sed -n 1,150000p | python download_direct.py 20170602 SOA > logs/20170624-000.log 2>&1 &
sort input/pluto14v2noCondos.bak.csv | sed -n 150001,300000p | python download_direct.py 20170602 SOA > logs/20170624-150.log 2>&1 &
sort input/pluto14v2noCondos.bak.csv | sed -n 300001,450000p | python download_direct.py 20170602 SOA > logs/20170624-300.log 2>&1 &
sort input/pluto14v2noCondos.bak.csv | sed -n 450001,600000p | python download_direct.py 20170602 SOA > logs/20170624-450.log 2>&1 &
sort input/pluto14v2noCondos.bak.csv | sed -n 600001,750000p | python download_direct.py 20170602 SOA > logs/20170624-600.log 2>&1 &
sort input/pluto14v2noCondos.bak.csv | sed -n 750001,900000p | python download_direct.py 20170602 SOA > logs/20170624-750.log 2>&1 &
