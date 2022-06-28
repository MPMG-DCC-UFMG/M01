import sys

from inout import load_conll, load_conll_probs
from collections import deque
from random import shuffle

def get_ent_type(label):
    if "-" in label:
        return label[2:]
    return label

def get_iob(label):
    if "-" in label:
        return label[:2]
    return ""


def calc_score(labels):
    for j,lab in enumerate(labels):
        start,end,lab,probs = lab

        
sents,labels = load_conll_probs(sys.argv[2], col=3)
sents,true_labels = load_conll(sys.argv[1], col=2)

frac = 0.1
if len(sys.argv) == 5:
    frac = float(sys.argv[4])

out = open(sys.argv[3], "w", encoding="utf-8")
scores = []

nselect = int(frac * len(labels))
indexes = [i for i in range(len(labels))]
shuffle(indexes)


for i in indexes[:nselect]:
    label = labels[i]
    sent = sents[i]
    true_label = true_labels[i]

    for j, lab in enumerate(label):
        start,end,lab,probs = lab
        true_lab = true_label[j][2]
        tok = sent[start:end]
        print("%s\t%s" % (tok, true_lab), file=out)
    print(file=out)


