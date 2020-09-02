import sys

from inout import load_conll
from collections import deque

def get_ent_type(label):
    if "-" in label:
        return label[2:]
    return label

def get_iob(label):
    if "-" in label:
        return label[:2]
    return ""

def can_be_proper_name(string, next_tok=None):
    nextcond = False
    if next_tok != "":
        nextcond = next_tok[0].isupper() or next_tok[0].isdigit()
    return string[0].isupper() or string[0].isdigit() or (len(string) > 1 and len(string) < 4 and nextcond)


def calc_score(labels):
    for j,lab in enumerate(labels):
        start,end,lab,probs = lab
        
sents,labels = load_conll_probs(sys.argv[1], col=3)
sents,true_labels = load_conll(sys.argv[1], col=2)

out = open(sys.argv[2], "w", encoding="utf-8")
scores = []

for i, label in enumerate(labels):
    sent = sents[i]
    true_label = true_labels[i]
    changeTo = None
    for j, lab in enumerate(label):
        start,end,lab,probs = lab
        true_lab = true_label[j][2]
        tok = sent[start:end]
        print("%s\t%s\t%s" % (tok, true_lab), file=out)
    print(file=out)
print("ncorrections:", ncorrections)
print(context_names)

