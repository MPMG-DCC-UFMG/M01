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

def evaluate(pred, gt):
    gt_ents, gt_rels = convert(gt)
    pred_ents, pred_rels = convert(pred)
    print("Entities")
    print_metrics(pred_ents, gt_ents)
    print("Relations")
    print_metrics(pred_rels, gt_rels)


def print_metrics(pred, gt):
    total = 0
    precs = []
    recs = []
    f1s = []

    for label,s in sorted(gt.items()):
        if label in pred:
            p = pred[label]
        else:
            p = set()
        intersec = p.intersection(s)
        prec = 0
        rec = 0
        f1 = 0
        if len(p) > 0:
            prec = len(intersec) / len(p)
        if len(s) > 0:
            rec = len(intersec) / len(s)
        pr = prec + rec
        if pr > 0:
            f1 = (2 * prec * rec) / pr
        print(label, prec, rec, f1, len(s))
        if label != "|micro":
            precs.append(prec)
            recs.append(rec)
            f1s.append(f1)
            total += len(s)
    #print("micro", sum(wprecs)/total, sum(wrecs)/total, sum(wf1s)/total, total)
    print("|macro", mean(precs), mean(recs), mean(f1s), total)


#Main

import sys
import json

file1 = open(sys.argv[1], encoding="utf-8")
file2 = open(sys.argv[2], encoding="utf-8")
pred = json.load(file1)
gt = json.load(file2)

evaluate(pred, gt)







