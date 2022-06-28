import sys

from inout import load_conll, load_conll_probs
from collections import deque
from random import shuffle
from numpy import mean

def get_ent_type(label):
    if "-" in label:
        return label[2:]
    return label

def get_iob(label):
    if "-" in label:
        return label[:2]
    return ""


#Calcula score de utilidade de uma frase rotulada com labels
def calc_score(labels, n=1):
    values = []
    for j,lab in enumerate(labels):
        start,end,lab,probs = lab
        #print(probs)
        values.append(1 - probs["O"])
    return mean(sorted(values, reverse=True)[:n])

        
sents,labels = load_conll_probs(sys.argv[2])
sents,true_labels = load_conll(sys.argv[1], col=2)

frac = 0.1
n = int(sys.argv[4])
if len(sys.argv) == 6:
    frac = float(sys.argv[5])

out = open(sys.argv[3], "w", encoding="utf-8")
scores = []
nselect = int(frac * len(labels))

for i, labs in enumerate(labels):
    sc = calc_score(labs, n)
    scores.append( (sc, i) )
    print(sc)

for sc,i in sorted(scores, reverse=True)[:nselect]:
    label = labels[i]
    sent = sents[i]
    true_label = true_labels[i]

    for j, lab in enumerate(label):
        start,end,lab,probs = lab
        true_lab = true_label[j][2]
        tok = sent[start:end]
        print("%s\t%s" % (tok, true_lab), file=out)
    print(file=out)


