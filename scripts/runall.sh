#!/bin/sh

dir=$1
outdir=/datalake/ufmg/m02

#Reproduzir arvore de diretorios

find "$dir" -type d | while read d
do
    outsubdir=`echo "$d" | cut -d "/" -f 1,2,3 --complement`
    echo "$outdir/$outsubdir"
    mkdir -p "$outdir/$outsubdir"

    find "$d" -maxdepth 1 -type f -name "*.pdf" | while read f
    do
       echo "$f"
       filename=`basename "$f" ".pdf"`
       out="$outdir/$outsubdir/$filename"
       echo "pdftotext \"$f\" \"$out.txt\""
       pdftotext "$f" "$out.txt"

       python3 -m preprocessing.text_cleaner "$out.txt" "$out.clean"
       ./run_pipeline.sh "$out.clean" "$out.entidades"
    done



    find "$d" -maxdepth 1 -type f -name "*.PDF" | while read f
    do
       echo "$f"
       filename=`basename "$f" ".PDF"`
       out="$outdir/$outsubdir/$filename"
       echo "pdftotext \"$f\" \"$out.txt\""
       pdftotext "$f" "$out.txt"

       python3 -m preprocessing.text_cleaner "$out.txt" "$out.clean"
       ./run_pipeline.sh "$out.clean" "$out.entidades"
    done


    find "$d" -maxdepth 1 -type f -name "*.html" | while read f
    do
       echo "$f"
       filename=`basename "$f" ".html"`
       out="$outdir/$outsubdir/$filename"

       python3 -m html2text --ignore-links --ignore-images "$f" utf-8 > "$out.txt"
       python3 -m preprocessing.text_cleaner "$out.txt" "$out.clean"

       ./run_pipeline.sh "$out.clean" "$out.entidades"
    done


done

