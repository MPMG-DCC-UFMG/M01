
import sys
import json

with open(sys.argv[1], encoding="utf-8") as infile:
    data = json.load(infile)

mapping = {}

for dic in data:
    ents = dic["entities"]
    if "relations" in dic:
        rels = dic["relations"]
    else:
        rels = []
    to_sort = []
    for i, ent in enumerate(ents):
        start = ent["start"]
        end = ent["end"]
        label = ent["type"]
        to_sort.append((start, end, label, i))
    sorted_ents = sorted(to_sort)
    new_ents = []
    new_rels = []

    for i, ent in enumerate(sorted_ents):
        start, end, label, idx = ent
        mapping[idx] = i
        new_ents.append({"start": start, "end": end, "type": label})

    for rel in rels:
        h = mapping[rel["head"]]
        t = mapping[rel["tail"]]
        label = rel["type"]
        new_rels.append({"head": h, "tail": t, "type": label})
    dic["entities"] = new_ents
    dic["relations"] = new_rels


with open(sys.argv[2], "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, indent=4)

