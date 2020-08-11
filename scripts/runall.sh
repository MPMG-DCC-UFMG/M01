#!/bin/sh

dir=$1
outdir=/datalake/ufmg/m02

#Reproduzir arvore de diretorios

for d in `find "$dir" -type d`
do
    outsubdir=`echo "$d" | cut -d "/" -f 1,2,3 --complement`
    mkdir -p "$outdir/$outsubdir"

    for f in `find "$d" -type f -name "*.pdf"`
    do
       echo "$f"
       filename=`basename "$f" ".pdf"`
       out="$outdir/$outsubdir/$filename"
       echo "pdftotext \"$f\" \"$out.txt\""
       pdftotext "$f" "$out.txt"

       python3 -m preprocessing.text_cleaner "$out.txt" "$out.clean"
       ./run_pipeline.sh "$out.clean" "$out.entidades"
    done
done

