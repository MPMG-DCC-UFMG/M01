#!/bin/sh

dir=/data/users/fmuniz/editais

for f in $dir/*/*/*/*/*.txt $dir/*/*/*/*.txt
do
    #if [ ! -s "$f" ]
    #then	
        echo "$f"
        python3 -m preprocessing.text_cleaner "$f" "$f.clean"
	./run_pipeline.sh "$f.clean" "$f.entidades"
    #fi
done


