#!/bin/sh

infile=$1
model=$2
out=$3

java -cp stanford-ner.jar edu.stanford.nlp.ie.demo.NERDemo $model $infile > $out

