import sys
import json

#TO-DO
def convert(jdata):
    res = []
    return res

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

jdata = json.load(infile)
infile.close()

jdata_new = convert(jdata)
json.dump(jdata_new, outfile, indent=4)

outfile.close()

