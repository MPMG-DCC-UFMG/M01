#!/bin/sh

prop=train/prop.txt

if [ $# = 1 ]
then
    prop=$1
fi

echo "java -cp \"stanford-ner.jar:lib/*\" -mx16g edu.stanford.nlp.ie.crf.CRFClassifier -prop $prop"

java -cp "stanford-ner.jar:lib/*" -mx16g edu.stanford.nlp.ie.crf.CRFClassifier -prop $prop


