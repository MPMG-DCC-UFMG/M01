import sys
import json

from preprocessing.json_formater import to_char_level_format

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

jdata = json.load(infile)
infile.close()

jdata_new = to_char_level_format(jdata)

json.dump(jdata_new, outfile, indent=4)

outfile.close()

