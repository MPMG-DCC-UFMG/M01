import sys
import json
from collections import defaultdict

def merge_spans_doc(dic):
    ents2new = {}
    new_entities = []
    entities = dic["entities"]
    if len(entities) == 0:
        return dic
    tokens = dic["tokens"]
    #idx --> [start, end]
    entmap = {}

    ent_list = [(ent["start"], ent["end"], i) for (i, ent) in enumerate(entities)]
    ent_list = sorted(ent_list)

    previous_start = -1
    previous_end = -1
    for (start, end, i) in ent_list:
        ent = entities[i]
        lab = ent["type"]
        if (start, end) != (previous_start, previous_end):
            new_entities.append({"start": start, "end": end, "type": lab})
        previous_start = start
        previous_end = end

    return {"tokens": tokens, "entities": new_entities, "relations": []}

def merge_spans(jdata):
    res = []
    for dic in jdata:
        res.append(merge_spans_doc(dic))
    return res


if __name__ == '__main__':
    #Test

    #jdata=[{"tokens": ["O", "Nobre", "Rato", "roeu", "a", "roupa", "do", "rei", "de", "Roma"],
    #        "entities": [{"start":1, "end":2, "type":"PER"}, {"start":1, "end":3, "type":"PER"}, {"start":2, "end":3, "type":"PER"}, {"start":2, "end":3, "type":"PER"}, {"start":2, "end":3, "type":"PER"}, {"start":9, "end":10, "type":"LOC"}],
    #        "relations": [{"head": 0, "tail":3, "type":"lives_in"}, {"head": 1, "tail":3, "type":"lives_in"}, {"head": 2, "tail":3, "type":"lives_in"}]
    #       }
    #      ]

    total = 0
    overlap_count = 0
    infile = open(sys.argv[1], encoding="utf-8")
    outfile = open(sys.argv[2], "w", encoding="utf-8")
    jdata = json.load(infile)
    infile.close()

    res = merge_spans(jdata)

    json.dump(res, outfile, indent=4)
    outfile.close()



