import json
import sys
import random

random.seed(42)


def complementarity_score(data, candidates, covered_rel_types):
    scores = []
    for i in candidates:
        dic = data[i]
        if len(dic["tokens"]) > 120:
            scores.append((0, i))
            continue
        relations = dic["relations"]
        item_types = set([rel["type"] for rel in relations])
        diff = item_types - covered_rel_types
        scores.append((len(diff), i))
    return scores

def rank(data):
    selected = []
    candidates = set(list(range(len(data))))
    covered_rel_types = set()
    for i in range(len(data)):
        scores = complementarity_score(data, candidates, covered_rel_types)
        s = max(scores)[1]
        selected.append(s)
        candidates.remove(s)
        covered_rel_types.update([rel["type"] for rel in data[s]["relations"]])
    return selected



infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

data = json.load(infile)
infile.close()

random.shuffle(data)

selected = rank(data)

res = [data[s] for s in selected]

json.dump(res, outfile, indent=4)

