import sys
import json
from operator import itemgetter

def process_relations(relations, entities, res):
    for rel in relations:
        if "score" in rel:
            sc = rel["score"]
        else:
            sc = 0.9 #default value
        head = rel["head"]
        tail = rel["tail"]
        span_h = (entities[head]["start"], entities[head]["end"])
        span_t = (entities[tail]["start"], entities[tail]["end"])
        res[ (span_h, span_t) ] = (rel["type"], sc)


def merge_jsons(jdatas):
    new_jdata = []
    ents = {}
    rels = {}
    joined_data = {}
    for jdata in jdatas:
        for i, dic in enumerate(jdata):
            if i not in joined_data:
                joined_data[i] = {"tokens": dic["tokens"], "annotations": []}
            joined_data[i]["annotations"].append({"entities": dic["entities"], "relations": dic["relations"]})
    for i, dic in joined_data.items():
        tokens = dic["tokens"]
        annotations = dic["annotations"]
        ent2scores = {}
        rel2scores = {}
        ent_idx = -1
        new_entmap = {}
        new_entmap_reverse = {}
        for annot in annotations:
            entmap = {}
            for eid, ent in enumerate(annot["entities"]):
                entmap[eid] = (ent["start"], ent["end"], ent["type"])
                if "score" in ent:
                    sc = ent["score"]
                else:
                    sc = 1 #default value
                etuple = (ent["start"], ent["end"], ent["type"])
                if etuple not in ent2scores:
                    ent_idx += 1
                    new_entmap[ent_idx] = etuple
                    new_entmap_reverse[etuple] = ent_idx
                    ent2scores[etuple] = 0 #voting score
                ent2scores[etuple] += sc
            if "relations" not in dic:
                continue
            for rel in dic["relations"]:
                if "score" in rel:
                    sc = rel["score"]
                else:
                    sc = 1 #default value
                rtuple = (entmap[rel["head"]], entmap[rel["tail"]], rel["type"])
                if rtuple not in rel2scores:
                    rel2score[rtuple] = 0 #voting score
                rel2score[rtuple] += sc
        new_entities = [None for j in range(len(new_entmap))]
        idmap = {}
        sorted_entities = sorted(new_entmap.items(), key=itemgetter(1))
        for k, entry in enumerate(sorted_entities):
            old_id = entry[0]
            idmap[old_id] = k

        for ent_idx, etuple in new_entmap.items():
            k = idmap[ent_idx]
            new_entities[k] = {"start": etuple[0], "end": etuple[1], "type": etuple[2], "score": ent2scores[etuple]}

        new_relations = []
        for rtuple, sc in rel2scores.items():
            h = new_entmap_reverse[rtuple[0]]
            t = new_entmap_reverse[rtuple[1]]
            new_relations.append({"head": idmap[h], "tail": idmap[t], "type": rtuple[2], "score": sc})

        new_jdata.append( {"tokens": tokens, "entities": new_entities, "relations": new_relations} )
    return new_jdata




#Main


outfile = open(sys.argv[1], "w", encoding="utf-8")
infiles = [open(x, encoding="utf-8") for x in sys.argv[2:]]
jdatas = [ json.load(infile) for infile in infiles ]

for infile in infiles:
    infile.close()

res = merge_jsons(jdatas)

json.dump(res, outfile, indent=4)
outfile.close()












