import sys

from inout import load_conll, load_conll_probs
from scipy.stats import entropy
from ml.categorical_feat_reader import load_feats, to_text
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
#from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
from numpy import array, mean, zeros
from inout import load_set

def pre_select(mat, labels, n=1):
    res = []
    indexes = []
    sent_indexes = []
    entropies = []
    j = 0
    for sent_ind,labs in enumerate(labels):
        token_entropy = []
        for lab in labs:
            start,end,lab,probs = lab
            h = entropy(list(probs.values()))
            token_entropy.append( (h, j) )
            j += 1
        for (entr, mat_ind) in sorted(token_entropy, reverse=True)[:n]:
            res.append(mat[mat_ind])
            sent_indexes.append(sent_ind)
            indexes.append(mat_ind)
            entropies.append(entr)
    return res, sent_indexes, indexes, entropies


def filter_stopwords(mat, stopwords):
    res = []
    indexes = []
    for i,row in enumerate(mat):
        if row[2] not in stopwords:
            res.append(row)
            indexes.append(i)
    return res, indexes


#"Unlabeled" dataset
sents,labels = load_conll_probs(sys.argv[2])
mat = load_feats(sys.argv[3])
sents,true_labels = load_conll(sys.argv[1], col=2)

n = int(sys.argv[5])
entr_thresh = 0.6
sim_thresh = 0.8
frac = 0.1
if len(sys.argv) == 9:
    frac = float(sys.argv[8])
if len(sys.argv) > 7:
    entr_thresh = float(sys.argv[6])
    sim_thresh = float(sys.argv[7])

out = open(sys.argv[4], "w", encoding="utf-8")

dist_thresh = 1 - sim_thresh

print("unlabeled examples:", sys.argv[1], file=sys.stderr)
print("label probabilities of the unlabeled examples:", sys.argv[2], file=sys.stderr)
print("features of the unlabeled examples", sys.argv[3], file=sys.stderr)
print("output:", sys.argv[4], file=sys.stderr)
print("n:", n, file=sys.stderr)
print("entr_thresh:", entr_thresh, file=sys.stderr)
print("sim_thresh:", sim_thresh, file=sys.stderr)


#stopwords = load_set("data/stopwords.txt")
mat_filtered, indexes_sent, indexes, entropies = pre_select(mat, labels, n=n)
print("len(mat)=", len(mat))

mat_text = to_text(mat_filtered)

print("len(mat_filtered)=", len(mat_filtered))
#vectorizer = TfidfVectorizer(lowercase=False)
vectorizer = CountVectorizer(lowercase=False)
mat_filtered = vectorizer.fit_transform(mat_text)

#Initial labeled dataset
#mat0 = load_feats(sys.argv[4])
#sents0,true_labels0 = load_conll(sys.argv[3], col=2)

nselect = int(frac * len(sents))



print("Computing similarities...")
sim = cosine_distances(mat_filtered)

print("Clustering...")
#clusterer = AgglomerativeClustering(n_clusters=nselect, affinity="precomputed", linkage="average")
clusterer = AgglomerativeClustering(n_clusters=None, affinity="precomputed", linkage="average", distance_threshold=dist_thresh)
clusters = clusterer.fit_predict(sim)

groups = {}
selected = []

for i, c in enumerate(clusters):
    if c not in groups:
        groups[c] = []
    groups[c].append( (entropies[i], i) )

sorted_groups = []

for group in groups.values():
    print("Cluster size:", len(group), end=" ")
    s = sorted(group)
    sorted_groups.append(s)
    for j in range(len(s)):
        entr,i = s[len(s) - j - 1]
        if j == 0:
            print(entr)
        print(mat[indexes[i]], entr)
    print("============\n")

nrelevant_clusters = 0

for group in sorted_groups:
    if len(group) > 0:
        entr, i = group[len(group) - 1]
        if entr > entr_thresh:
            nrelevant_clusters += 1


while len(selected) < nselect:
    met_thresh = False
    for group in sorted_groups:
        if len(group) > 0:
            entr, i = group.pop()
            if entr > entr_thresh:
                selected.append(indexes_sent[i])
                met_thresh = True
                if  len(selected) >= nselect:
                    break
    if not met_thresh:
        break

print("entr_thresh, sim_thresh, #clusters, #relevant_clusters, #to_select, #selected, #coverage_of_rel_clusters:")
print(entr_thresh, sim_thresh, len(sorted_groups), nrelevant_clusters, nselect, len(selected), len(selected)/nrelevant_clusters)

#Print selected sentences
for i in selected:
    sent_labels = true_labels[i]
    sent = sents[i]
    for j, lab in enumerate(sent_labels):
        start,end,true_lab = lab
        tok = sent[start:end]
        print("%s\t%s" % (tok, true_lab), file=out)
    print(file=out)

