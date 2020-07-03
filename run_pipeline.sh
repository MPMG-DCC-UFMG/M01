#!/bin/sh

corenlp_model=models/lener_model.ser.gz

if [ $# != 2 ]
then
    echo "usage: $0 <input text file> <output file path>"
    exit
fi


infile=$1
outfile=$2


#CoreNLP NER
echo "Running CoreNLP NER..."
./text_corenlp.sh "$infile" "$corenlp_model" "$outfile.corenlp.conll"

#Acrescenta regex-based NER ao resultado do CoreNLP
echo "Adding regex-based named entities..."
python3 -m rule_based_ner "$outfile.corenlp.conll" "$outfile"

