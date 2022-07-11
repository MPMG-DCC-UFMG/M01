import sys

from inout import load_conll, load_conll_probs
from collections import deque
from random import shuffle
from scipy.stats import entropy
from sklearn.metrics.pairwise import cosine_similarity
from numpy import array, mean

def get_ent_type(label):
    if "-" in label:
        return label[2:]
    return label

def get_iob(label):
    if "-" in label:
        return label[:2]
    return ""


# Calcula score de utilidade de uma frase referente a posicao start_end_indexes
# da matriz de distancias sum_distance

def calc_score(start_end_indexes, sum_distance, n=1):
    values = []
    start,end = start_end_indexes
    for i in range(start, end):
        values.append(sum_distance[i])
    return mean(sorted(values, reverse=True)[:n])


def convert2mat(labels):
    sent2indexes = []
    mat = []
    j = 0
    start,end,lab,probs = labels[0][0]
    feature_index = []
    for name in probs:
        feature_index.append(name)

    for labs in labels:
        indexes = []
        ind_start = j
        for lab in labs:
            start,end,lab,probs = lab
            vec = [probs[feat] for feat in feature_index]
            mat.append(vec)
            indexes.append(j)
            j += 1
        sent2indexes.append( (ind_start, j) )
    return array(mat), sent2indexes


def sum_dist(similarities):
    sums = []
    for i in range(len(similarities)):
        sums.append( -sum(similarities[i,:]) )
    return array(sums)


#"Unlabeled" dataset
sents,labels = load_conll_probs(sys.argv[2])
sents,true_labels = load_conll(sys.argv[1], col=2)


#Initial labeled dataset
sents0,labels0 = load_conll_probs(sys.argv[4])
sents0,true_labels0 = load_conll(sys.argv[3], col=2)


n = int(sys.argv[6])

frac = 0.1
if len(sys.argv) == 8:
    frac = float(sys.argv[7])

out = open(sys.argv[5], "w", encoding="utf-8")

nselect = int(frac * len(labels))

mat, sent2indexes =  convert2mat(labels)
mat0, sent2indexes0 = convert2mat(labels0)

print("Computing similarities...")

#Similarity matrix unlabeled X labeled samples
similarities = cosine_similarity(mat, mat0)
sum_distance = sum_dist(similarities)

print("Finished computing similarities.")
print("SumOfDistances:\n", sum_distance)

to_select = set([i for i in range(len(labels))])
selected = set()

for t in range(nselect):
    print("Iter:", t)
    chosen_sent = 0
    max_score = -999999999
    for i in to_select:
        sc = calc_score(sent2indexes[i], sum_distance, n)
        if sc > max_score:
            max_score = sc
            chosen_sent = i
    to_select.discard(chosen_sent)
    selected.add(chosen_sent)

    start,end = sent2indexes[chosen_sent]

    #Add similarities of the tokens of the chosen sent
    new_similarities = cosine_similarity(mat, mat[start:end,:])
    new_sum_dist = sum_dist(new_similarities)
    sum_distance += new_sum_dist
    print("SumOfDistances:\n", sum_distance)

#Print selected sentences
for i in selected:
    label = labels[i]
    sent = sents[i]
    true_label = true_labels[i]

    for j, lab in enumerate(label):
        start,end,lab,probs = lab
        true_lab = true_label[j][2]
        tok = sent[start:end]
        print("%s\t%s" % (tok, true_lab), file=out)
    print(file=out)


