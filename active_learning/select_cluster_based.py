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

def pre_select(mat, labels, last_unlabeled_index, n=1):
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
            p = 1 - probs["O"]
            token_entropy.append( (p, h, j) )
            j += 1
            #if j == last_unlabeled_index:
            #    n = 10
        for (p, entr, mat_ind) in sorted(token_entropy, reverse=True)[:n]:
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



unlab_filename = sys.argv[1]
unlabprob_filename = sys.argv[2]
unlabfeats_filename = sys.argv[3]

lab_filename = sys.argv[4]
labprob_filename = sys.argv[5]
labfeats_filename = sys.argv[6]
outfilename = sys.argv[7]

#"Unlabeled" dataset
sents,labels = load_conll_probs(unlabprob_filename)
mat = load_feats(unlabfeats_filename)
sents,true_labels = load_conll(unlab_filename, col=2)

#"Labeled" dataset
Lsents,Llabels = load_conll_probs(labprob_filename)
Lmat = load_feats(labfeats_filename)
Lsents,Ltrue_labels = load_conll(lab_filename, col=2)

last_unlab_index = len(mat) - 1

n = int(sys.argv[8])
entr_thresh = 0.6
sim_thresh = 0.8
frac = 0.1
if len(sys.argv) == 12:
    frac = float(sys.argv[11])
if len(sys.argv) > 10:
    entr_thresh = float(sys.argv[9])
    sim_thresh = float(sys.argv[10])

out = open(outfilename, "w", encoding="utf-8")

dist_thresh = 1 - sim_thresh

print("unlabeled examples:", unlab_filename, file=sys.stderr)
print("label probabilities of the unlabeled examples:", unlabprob_filename, file=sys.stderr)
print("features of the unlabeled examples", unlabfeats_filename, file=sys.stderr)

print("labeled examples:", unlab_filename, file=sys.stderr)
print("label probabilities of the labeled examples:", unlabprob_filename, file=sys.stderr)
print("features of the labeled examples", unlabfeats_filename, file=sys.stderr)

print("output:", outfilename, file=sys.stderr)
print("n:", n, file=sys.stderr)
print("entr_thresh:", entr_thresh, file=sys.stderr)
print("sim_thresh:", sim_thresh, file=sys.stderr)

print("|U| =", len(mat))
print("|L| =", len(Lmat))

print("#U sentences =", len(labels))
print("#L sentences =", len(Llabels))

print("U ntokens= ", sum([len(x) for x in labels]))
print("L ntokens= ", sum([len(x) for x in Llabels]))

mat += Lmat
labels += Llabels

print("|L| + |U| =", len(mat))
print("#U+L sentences =", len(labels))

print("ntokens= ", sum([len(x) for x in labels]))



#stopwords = load_set("data/stopwords.txt")
mat_filtered, indexes_sent, indexes, entropies = pre_select(mat, labels, last_unlab_index, n=n)
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

num_labeled_in_cluster = {}

for i, c in enumerate(clusters):
    if c not in groups:
        num_labeled_in_cluster[c] = 0
        groups[c] = []
    if indexes[i] > last_unlab_index:
        num_labeled_in_cluster[c] += 1
    groups[c].append( (entropies[i], i, indexes[i] <= last_unlab_index) )

sorted_groups = []

for group_id, group in groups.items():
    print("Cluster size:", len(group), end=" ")
    s = sorted(group)
    max_entropy = s[len(s) - 1][0]

    #Adds (max_entropy, group_id, and sorted elements of the group) in the list
    sorted_groups.append( (max_entropy, group_id, s) )
    print(max_entropy, num_labeled_in_cluster[group_id])
    for j in range(len(s)):
        entr,i,is_unlab = s[len(s) - j - 1]
        print(mat[indexes[i]], entr, is_unlab)
    print("============\n")

nrelevant_clusters = 0
nrel_and_no_labeled = 0

for max_entr, group_id, group in sorted_groups:
    if len(group) > 0:
        if max_entr > entr_thresh:
            nrelevant_clusters += 1
            if num_labeled_in_cluster[group_id] == 0:
                nrel_and_no_labeled += 1

while len(selected) < nselect:
    met_thresh = False
    for max_entr, group_id, group in sorted(sorted_groups, reverse=True):
        if len(group) > 0:
            is_new = num_labeled_in_cluster[group_id] == 0
            entr, i, is_unlab = group.pop()
            if entr > entr_thresh and is_new:
                selected.append(indexes_sent[i])
                met_thresh = True
                if  len(selected) >= nselect:
                    break
    if not met_thresh:
        break

print("entr_thresh, sim_thresh, #clusters, #relevant_clusters, #nrel_and_no_labeled, #to_select, #selected, #coverage_of_rel_clusters, #coverage_of_rel_nolabeled_clusters:")
print(entr_thresh, sim_thresh, len(sorted_groups), nrelevant_clusters, nrel_and_no_labeled, nselect, len(selected), len(selected)/nrelevant_clusters, len(selected)/nrel_and_no_labeled)

#Print selected sentences
for i in selected:
    sent_labels = true_labels[i]
    sent = sents[i]
    for j, lab in enumerate(sent_labels):
        start,end,true_lab = lab
        tok = sent[start:end]
        print("%s\t%s" % (tok, true_lab), file=out)
    print(file=out)

