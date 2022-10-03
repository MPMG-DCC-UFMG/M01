import sys
import json

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)
res = []

max_size = 150

for item in data:
    tokens = item["tokens"]
    ents = item["entities"]
    rels = item["relations"]

    new_tokens = tokens[:max_size]
    new_ents = []
    new_rels = []
    to_exclude = set()
    for i, ent in enumerate(ents):
        start = ent["start"]
        if start < max_size:
            new_ents.append(ent)
        else:
            to_exclude.add(i)
    for rel in rels:
        head = rel["head"]
        tail = rel["tail"]
        if not (head in to_exclude or tail in to_exclude):
            new_rels.append(rel)
    res.append({"tokens": new_tokens, "entities": new_ents, "relations": new_rels})

print("%%filtered:", len(res) / len(data))
json.dump(res, outfile, indent=4)

