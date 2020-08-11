#!/bin/sh

dir=$1

for f in `find "$dir" -type f -name "*.entidades.json"`
do
    echo "$f"
    python3 -m data_extraction.licitacao "$f" "$f.attribs"
done



for f in `find "$dir" -type f -name "*.attribs"`
do
    cat "$f"
done > licitacoes.csv



