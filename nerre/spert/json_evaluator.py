import numpy as np
import pandas as pd

def ent_tuple(ent):
    return (ent["start"], ent["end"], ent["type"])

def ent_tuple_typeless(ent):
    return (ent["start"], ent["end"])


def convert(jdata, min_score=0):
    rels = {"|micro": set()}
    ents = {"|micro": set()}
    for i,dic in enumerate(jdata):
        entities = dic["entities"]
        for ent in entities:
            if "score" in ent:
                score = ent["score"]
            else:
                score = 1
            if score < min_score:
                continue
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
            if "score" in rel:
                score = rel["score"]
            else:
                score = 1
            if score < min_score:
                continue
            head = rel["head"]
            tail = rel["tail"]
            pair1 = ent_tuple_typeless(entities[head])
            pair2 = ent_tuple_typeless(entities[tail])
            if pair1 > pair2:
                aux = pair2
                pair2 = pair1
                pair1 = aux
            label = rel["type"]
            if label not in rels:
                rels[label] = set()
            cls = (i, pair1, pair2, label)
            rels[label].add(cls)
            rels["|micro"].add(cls)
    return ents,rels

def evaluate(pred, gt, min_score=0):
    gt_ents, gt_rels = convert(gt, min_score=min_score)
    pred_ents, pred_rels = convert(pred)
    print("Entities")
    print(calc_metrics(pred_ents, gt_ents))
    print("Relations")
    print(calc_metrics(pred_rels, gt_rels))


def calc_metrics(pred, gt):
    total = 0
    precs = []
    recs = []
    f1s = []

    wprecs = []
    wrecs = []
    wf1s = []
    values = []


    for label,s in sorted(gt.items()):
        if label in pred:
            p = pred[label]
        else:
            p = set()
        intersec = p.intersection(s)
        prec = 0
        rec = 0
        f1 = 0
        wprec = 0
        wrec = 0
        wf1 = 0
        if len(p) > 0:
            prec = len(intersec) / len(p)
            wprec = len(s) * prec
        if len(s) > 0:
            rec = len(intersec) / len(s)
            wrec = len(intersec)
        pr = prec + rec
        if pr > 0:
            f1 = (2 * prec * rec) / pr
            wf1 = len(s) * f1
        values.append( (label, prec, rec, f1, len(s)) )
        if label != "|micro":
            precs.append(prec)
            recs.append(rec)
            f1s.append(f1)
            total += len(s)
            wprecs.append(wprec)
            wrecs.append(wrec)
            wf1s.append(wf1)
    values.append(("|weighted", np.sum(wprecs) / total, np.sum(wrecs) / total, np.sum(wf1s) / total, total))
    values.append(("|macro", np.mean(precs), np.mean(recs), np.mean(f1s), total))
    return pd.DataFrame(values, columns="Label Precision Recall F1 Support".split())
    #print("micro", sum(wprecs)/total, sum(wrecs)/total, sum(wf1s)/total, total)
    #print("|macro", mean(precs), mean(recs), mean(f1s), total)

#Main

import sys
import json

file1 = open(sys.argv[1], encoding="utf-8")
file2 = open(sys.argv[2], encoding="utf-8")
pred = json.load(file1)
gt = json.load(file2)

min_score = 0
if len(sys.argv) == 4:
    min_score = float(sys.argv[3])

evaluate(pred, gt, min_score=min_score)

