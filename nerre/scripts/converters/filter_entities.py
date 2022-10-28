import sys
import json

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)

allowed = ["PRODUTO_OU_SERVICO"]

for item in data:
    new_ents = []
    ents = item["entities"]
    for ent in ents:
        if ent["type"] in allowed:
            new_ents.append(ent)
    item["entities"] = new_ents

print("len(data):", len(data))
json.dump(data, outfile, indent=4)

