#!/bin/sh

java -cp "stanford-ner.jar:lib/*" -mx16g edu.stanford.nlp.ie.crf.CRFClassifier -prop train/prop.txt
