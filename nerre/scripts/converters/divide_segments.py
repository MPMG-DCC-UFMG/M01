import json
import sys

infile = open(sys.argv[1], encoding="utf-8")
outdir = sys.argv[2]

jdata = json.load(infile)
infile.close()

for i, dic in enumerate(jdata["sentences"]):
    outfile = open(f"{outdir}/{i}.json", "w", encoding="utf-8")
    json.dump(dic, outfile, indent=4)
    outfile.close()



