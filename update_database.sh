#!/bin/bash

if [ $# -eq 0 ]
then
    echo "Usage: $0 <import year>"
    exit
fi

YEAR=$1
wget http://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A${YEAR}.ZIP -O COTAHIST_A${YEAR}.ZIP &&
./import.py COTAHIST_A${YEAR}.ZIP
