from preprocessing.json_formater import to_iob
import sys
import json

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

jdata = json.load(infile)
infile.close()

to_iob(jdata, outfile)
outfile.close()



