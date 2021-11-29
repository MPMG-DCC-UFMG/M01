import sys
import json


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


def merge_jsons(jdata1, jdata2):
    new_jdata = []
    for i, dic1 in enumerate(jdata1):
        eid = 0
        dic2 = jdata2[i]
        tokens = dic1["tokens"]
        ents = {}
        rels = {}
        for ent in dic2["entities"] + dic1["entities"]:
            if "score" in ent:
                sc = ent["score"]
            else:
                sc = 0.9 #default value
            span = (ent["start"], ent["end"])
            ents[span] = (ent["type"], sc)

        entmap = {}
        new_entities = []
        for span, type_sc in sorted(ents.items()):
            entmap[span] = eid
            eid += 1
            new_entities.append({"start": span[0], "end": span[1], "type": type_sc[0], "score": type_sc[1]})
        
        process_relations(dic2["relations"], dic2["entities"], rels)
        process_relations(dic1["relations"], dic1["entities"], rels)
        new_relations = []
        for span, type_sc in sorted(rels.items()):
            h = entmap[span[0]]
            t = entmap[span[1]]
            new_relations.append({"head": h, "tail": t, "type": type_sc[0], "score": type_sc[1]})
        new_jdata.append( {"tokens": tokens, "entities": new_entities, "relations": new_relations} )
    return new_jdata




#Main


infile1 = open(sys.argv[1], encoding="utf-8")
infile2 = open(sys.argv[2], encoding="utf-8")

outfile = open(sys.argv[3], "w", encoding="utf-8")

jdata1 = json.load(infile1)
jdata2 = json.load(infile2)

infile1.close()
infile2.close()

res = merge_jsons(jdata1, jdata2)

json.dump(res, outfile, indent=4)
outfile.close()












