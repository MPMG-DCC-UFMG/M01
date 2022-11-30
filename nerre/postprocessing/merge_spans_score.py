import sys
import json
from collections import defaultdict

total = 0
overlap_count = 0

def merge_spans_doc(dic):
    global total
    global overlap_count
    ents2new = {}
    new_entities = []
    entities = dic["entities"]
    if len(entities) == 0:
        return dic

    tokens = dic["tokens"]
    occupied = [False for i in range(len(tokens))]

    #idx --> [start, end]
    entmap = {}

    freq_start = defaultdict(int)
    freq_end = defaultdict(int)
    ent_idx = -1
    total += len(entities)
    for i, ent in enumerate(entities):
        overlap = False
        start = ent["start"]
        end = ent["end"]
        label = ent["type"]
        if "score" in ent:
            score = ent["score"]
        else:
            score = end - start
        freq_start[start] += 1
        freq_end[end] += 1
        for j in range(start, end):
            if occupied[j]:
                overlap = True
            occupied[j] = True
        if not overlap:
            ent_idx += 1
        else:
            overlap_count += 1
        if ent_idx in entmap:
            s,e,lab,sc = entmap[ent_idx]
            if score > sc:
                entmap[ent_idx] = [start, end, label, score]
        else:
            entmap[ent_idx] = [start, end, label, score]
        ents2new[i] = ent_idx


    for idx in range(len(entmap)):
        start, end, label, score = entmap[idx]
        new_entities.append({"start": start, "end": end, "type": label, "score": score})

    new_relations_dic = {}
    for rel in dic["relations"]:
        head = rel["head"]
        tail = rel["tail"]
        label = rel["type"]
        if "score" in rel:
            score = rel["score"]
        else:
            score = 1
        pair = ents2new[head],ents2new[tail]
        new_relations_dic[pair] = (label, score)
    new_relations = []
    for pair, lab_sc in new_relations_dic.items():
        if pair[0] != pair[1]:
            new_relations.append({"head": pair[0], "tail":pair[1], "type":lab_sc[0], "score":lab_sc[1]})
    return {"tokens": dic["tokens"], "entities": new_entities, "relations": new_relations}

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

    print("overlap_count:", overlap_count, "/", total, "=", overlap_count/total)



