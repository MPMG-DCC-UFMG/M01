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


#Calcula score de utilidade de uma frase rotulada com labels
def calc_score(labels):
    m = 1
    for j,lab in enumerate(labels):
        start,end,lab,probs = lab
        #print(probs)
        prob_o = probs["O"]
        if prob_o < m:
            m = prob_o
    return 1 - m


        
sents,labels = load_conll_probs(sys.argv[2])
sents,true_labels = load_conll(sys.argv[1], col=2)

frac = 0.1
if len(sys.argv) == 5:
    frac = float(sys.argv[4])

out = open(sys.argv[3], "w", encoding="utf-8")
scores = []
nselect = int(frac * len(labels))

for i, labs in enumerate(labels):
    sc = calc_score(labs)
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


