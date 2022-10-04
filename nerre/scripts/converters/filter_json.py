import sys
import json

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)
res = []

for item in data:
    tokens = item["tokens"]
#    print(len(tokens))
    if len(tokens) > 120:
        continue
    res.append( item )

print("%%filtered:", len(res) / len(data))
json.dump(res, outfile, indent=4)

