#!/bin/sh

dir=/data/users/fmuniz/editais

for f in $dir/*/*/*/*/*.entidades.json $dir/*/*/*/*.entidades.json
do
    #if [ ! -s "$f" ]
    #then	
        echo "$f"
        python3 -m data_extraction.licitacao "$f" "$f.attribs"
    #fi
done

for f in $dir/*/*/*/*/*json.attribs $dir/*/*/*/*json.attribs
do
    cat "$f"
done > licitacoes.csv



