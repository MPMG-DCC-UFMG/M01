from numpy import mean, sum

def ent_tuple(ent):
    return (ent["start"], ent["end"], ent["type"])

def ent_tuple_typeless(ent):
    return (ent["start"], ent["end"])
 

def convert(jdata):
    rels = {"|micro": set()}
    ents = {"|micro": set()}
    for i,dic in enumerate(jdata):
        entities = dic["entities"]
        for ent in entities:
            start = ent["start"]
            end = ent["end"]
            label = ent["type"]
            if label not in ents:
                ents[label] = set()
            cls = (i, ent_tuple(ent))
            ents[label].add(cls)
            ents["|micro"].add(cls)
        if "relations" not in dic:
            continue
        for rel in dic["relations"]:
            head = rel["head"]
            tail = rel["tail"]
            if head > tail:
                aux = head
                head = tail
                tail = aux
            label = rel["type"]
            if label not in rels:
                rels[label] = set()
            cls = (i, ent_tuple_typeless(entities[head]), ent_tuple_typeless(entities[tail]), label)
            rels[label].add(cls)
            rels["|micro"].add(cls)
    return ents,rels

def compl(pred1, pred2, gt, outname):
    gt_ents, gt_rels = convert(gt)
    pred_ents1, pred_rels1 = convert(pred1)
    pred_ents2, pred_rels2 = convert(pred2)
    print("Entities")
    print_compl(pred_ents1, pred_ents2, gt_ents, pred1, pred2, gt, outname)
    #print("Relations")
    #print_metrics(pred_rels, gt_rels)


def get_ent_str(item, jdata):
    i, etuple = item
    start, end, etype = etuple
    tokens = jdata[i]["tokens"]
    return " ".join([etype] + tokens[start:end])


def print_entities(s, filep, jdata):
    for item in s:
        print(get_ent_str(item, jdata), file=filep)


def print_compl(pred1, pred2, gt, jdata1, jdata2, jgt, outname):
    
    outputs = {k : open(outname + "_" + k, "w", encoding="utf-8") for k in "m1 m2 both none".split()}
    truth = gt["|micro"]
    m1 = pred1["|micro"]
    m2 = pred2["|micro"]
    correct_m1 = m1.intersection(truth)
    correct_m2 = m2.intersection(truth)
    m1_only = correct_m1.difference(correct_m2)
    m2_only = correct_m2.difference(correct_m1)
    both = correct_m1.intersection(correct_m2)
    union = correct_m1.union(correct_m2)
    none = truth.difference(union)

    total = len(union) + len(none)

    print("M1 only:", len(m1_only), "(", 100*len(m1_only)/total, "% )")
    print("M2 only:", len(m2_only), "(", 100*len(m2_only)/total, "% )")
    print("both:", len(both), "(", 100*len(both)/total, "% )")
    print("none:", len(none), "(", 100*len(none)/total, "% )")

    print_entities(m1_only, outputs["m1"], jdata1)
    print_entities(m2_only, outputs["m2"], jdata2)
    print_entities(none, outputs["none"], jgt)
    print_entities(both, outputs["both"], jgt)
 
    for filep in outputs.values():
        filep.close()

#Main

import sys
import json

file1 = open(sys.argv[1], encoding="utf-8")
file2 = open(sys.argv[2], encoding="utf-8")
gt_file = open(sys.argv[3], encoding="utf-8")
outname = sys.argv[4] #, "w", encoding="utf-8")

pred1 = json.load(file1)
pred2 = json.load(file2)
gt = json.load(gt_file)

compl(pred1, pred2, gt, outname)








