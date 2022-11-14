import os
import sys
import json

res = []
indir = sys.argv[1]
outname = sys.argv[2]

for filename in os.listdir(indir):
    with open(f"{indir}{os.sep}{filename}", encoding="utf-8") as infile:
        data = json.load(infile)
    res += data

with open(outname, "w", encoding="utf-8") as outfile:
    json.dump(res, outfile, indent=4)
