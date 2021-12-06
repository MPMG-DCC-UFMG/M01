import sys
import json
import pandas
from inout import load_conll

#infile = open(sys.argv[1], encoding="utf-8")
infilename = sys.argv[1]
outfile =  open(sys.argv[2], "w", encoding="utf-8")

idx = 0
res = []
current_ent = "O"

sents, labels = load_conll(infilename, col=3)

for idx in range(len(sents)):
    sent = sents[idx]
    labs = labels[idx]
    tokens = []
    res_ents = []
    res_rels = []
    j = 0
    current_ent = "O"
    start,end,ent = labs[0]
    tokens.append(sent[start:end])
    while j < len(labs):
        if ent == "O":
            j += 1
            if j >= len(labs):
                break
            start,end,ent = labs[j]
            tokens.append(sent[start:end])
        if ent.startswith("B-"):
            current_ent = ent[2:]
            start_idx = j
            end_idx = start_idx + 1
            j += 1
            if j >= len(labs):
                res_ents.append( {"start": start_idx, "end": end_idx, "type": current_ent} )
                break
            start,end,ent = labs[j]
            tokens.append(sent[start:end])
            while ent.startswith("I-"):
                end_idx += 1
                j += 1
                if j >= len(labs):
                    break
                start,end,ent = labs[j]
                tokens.append(sent[start:end])
            res_ents.append( {"start": start_idx, "end": end_idx, "type": current_ent} )
    if len(res_ents) > -1:
        res.append( {"orig_id": idx, "tokens": tokens, "entities": res_ents} )


json.dump(res, outfile, indent=4)
outfile.close()


