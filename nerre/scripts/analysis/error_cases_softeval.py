from numpy import mean, sum
import pandas as pd

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

def evaluate(pred, gt):
    gt_ents, gt_rels = convert(gt)
    pred_ents, pred_rels = convert(pred)
    print("Entities")
    print_metrics(pred_ents, gt_ents, gt, verbose=True, relation=False)


def print_metrics(pred, gt, docs, verbose=False, relation=False):
    total = 0
    precs = []
    recs = []
    f1s = []
    sprecs = []
    srecs = []
    span_size_diffs = []
    df = []
    for label,s in sorted(gt.items()):
        if label == "|micro":
            continue
        if label in pred:
            p = pred[label]
        else:
            p = set()
        intersec = p.intersection(s)
        prec = 0
        rec = 0
        f1 = 0
        soft_prec = 0
        soft_rec = 0
        if len(p) > 0:
            prec = len(intersec) / len(p)
        if len(s) > 0:
            rec = len(intersec) / len(s)
        pr = prec + rec
        if pr > 0:
            f1 = (2 * prec * rec) / pr
        print(label, prec, rec, f1, len(s))

        occupied_p = {}

        for elem in p:
            doc_idx, (start, end, label) = elem
            if doc_idx not in occupied_p:
                occupied_p[doc_idx] = [None for t in docs[doc_idx]["tokens"]]
            for k in range(start, end):
                occupied_p[doc_idx][k] = (start, end)

        occupied_s = {}

        for elem in s:
            doc_idx, (start, end, label) = elem
            if doc_idx not in occupied_s:
                occupied_s[doc_idx] = [None for t in docs[doc_idx]["tokens"]]
            for k in range(start, end):
                occupied_s[doc_idx][k] = (start, end)


        if verbose:
            #print("Not retrieved:")
            for elem in sorted(list(s)):
                correct = 0
                if elem not in p:
                    if not relation:
                        doc_idx, (start, end, label) = elem
                        span_size_s = end - start
                        tokens = docs[doc_idx]["tokens"]
                        has_intersec = False
                        for k in range(start, end):
                            if doc_idx not in occupied_p:
                                break
                            o = occupied_p[doc_idx][k]
                            if o is not None:
                                other_start, other_end = o
                                has_intersec = True
                                break

                        first = " ".join(tokens[start:end])
                        second = ""
                        #print("\t" + " ".join(tokens[start:end]), end="|")
                        if has_intersec:
                            correct = 1
                            #print(" ".join(tokens[other_start:other_end]), end="")
                            second = " ".join(tokens[other_start:other_end])
                            span_size_p = other_end - other_start
                            span_size_diffs.append(span_size_s - span_size_p)
                        #print()
                        df.append((first, second))
                else:
                    correct = 1
                soft_rec += correct
            soft_rec /= len(s)

            #print("Wrong retrieval:")
            for elem in sorted(list(p)):
                correct = 0
                if elem not in s:
                    if not relation:
                        doc_idx, (start, end, label) = elem
                        tokens = docs[doc_idx]["tokens"]

                        has_intersec = False
                        for k in range(start, end):
                            if doc_idx not in occupied_s:
                                break
                            o = occupied_s[doc_idx][k]
                            if o is not None:
                                other_start, other_end = o
                                has_intersec = True
                                break
                        if has_intersec:
                            correct = 1
                            #print(" ".join(tokens[other_start:other_end]), end="")
                        else:
                            df.append(("", " ".join(tokens[start:end])))
                        #print("|" + " ".join(tokens[start:end]))
                else:
                    correct = 1
                soft_prec += correct
            soft_prec /= len(p)
            print(label, soft_prec, soft_rec, mean(span_size_diffs))
        if label != "|micro":
            precs.append(prec)
            recs.append(rec)
            f1s.append(f1)
            sprecs.append(soft_prec)
            srecs.append(soft_rec)
            total += len(s)
    #print("micro", sum(wprecs)/total, sum(wrecs)/total, sum(wf1s)/total, total)
    print("|macro", mean(precs), mean(recs), mean(f1s), total)
    print("soft_macro|", mean(sprecs), mean(srecs))
    df = pd.DataFrame(df, columns=["BLOOM", "CRF"])
    df.to_csv("error_cases.csv", index=None)

#Main

import sys
import json

file1 = open(sys.argv[1], encoding="utf-8")
file2 = open(sys.argv[2], encoding="utf-8")
pred = json.load(file1)
gt = json.load(file2)
file1.close()
file2.close()

evaluate(pred, gt)


