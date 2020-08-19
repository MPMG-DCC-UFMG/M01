#!/bin/sh

dir=$1
out=$2

find "$dir" -type f -name "*.entidades.json" | while read f
do
    echo "$f"
    python3 -m data_extraction.licitacao "$f" "$f.attribs"
done



find "$dir" -type f -name "*.attribs" | while read f
do
    cat "$f"
done > $out

