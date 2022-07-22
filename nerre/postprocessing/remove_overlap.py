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

    #Marca os tipos de entidades que se sobrepoem em cada token
    occupied = [set() for i in range(len(tokens))]
    occupied_ids = [{} for i in range(len(tokens))]


    #idx --> [start, end]
    entmap = {}

    freq_start = defaultdict(int)
    freq_end = defaultdict(int)
    ent_idx = 0
    total += len(entities)
    prev_ent = {"start": 0, "end": 0, "type": "", "score": 0}
    for i, ent in enumerate(entities):
        overlap = False
        start = ent["start"]
        end = ent["end"]
        lab = ent["type"]
        score = ent["score"]
        freq_start[start] += 1
        freq_end[end] += 1
        if prev_ent["start"] == start and prev_ent["end"] == end: #Sobreposicao total
            overlap = True
        for j in range(start, end):
            if lab in occupied[j]: #Em sobreposicoes parciais, aceita a sobreposicao se os tipos de entidade forem diferentes
                overlap = True
            occupied[j].add(lab)
            if lab in occupied_ids[j]:
                idx = occupied_ids[j][lab]
            else:
                idx = ent_idx
                occupied_ids[j][lab] = idx
        if idx in entmap:
            s,e,lab,sc = entmap[idx]
            if score > sc:
                entmap[idx] = [start, end, lab, score]
        else:
            entmap[idx] = [start, end, lab, score]
        if not overlap:
            ent_idx += 1
        else:
            overlap_count += 1

        ents2new[i] = idx
        prev_ent = ent


    for idx in range(len(entmap)):
        start, end, label, score = entmap[idx]
        new_entities.append({"start": start, "end": end, "type": label, "score": score})

    new_relations_dic = {}
    for rel in dic["relations"]:
        head = rel["head"]
        tail = rel["tail"]
        label = rel["type"]
        score = rel["score"]
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



