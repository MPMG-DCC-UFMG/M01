import sys, os

from inout import load_conll, load_conll_probs
from scipy.stats import entropy
from ml.categorical_feat_reader import load_feats, to_text
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
from numpy import array, mean, zeros, dot
from numpy.random import rand, randint
from inout import load_set
from operator import itemgetter
from math import log
from random import shuffle

def pre_select(mat, labels, last_unlabeled_index, n=1):
    res = []
    indexes = []
    sent_indexes = []
    entropies = []
    prob_ent = []

    j = 0
    for sent_ind,labs in enumerate(labels):
        token_entropy = []
        for lab in labs:
            start,end,lab,probs = lab
            h = entropy(list(probs.values()))
            p = 1 - probs["O"]
            token_entropy.append( (h, p, j) )
            j += 1
            #if j == last_unlabeled_index:
            #    n = 10
        for (entr, p, mat_ind) in sorted(token_entropy, reverse=True)[:n]:
            res.append(mat[mat_ind])
            sent_indexes.append(sent_ind)
            indexes.append(mat_ind)
            entropies.append(entr)
            prob_ent.append(p)
    return res, sent_indexes, indexes, entropies, prob_ent


def extract_f1(filename):
    infile = open(filename)
    f1 = -1
    for line in infile:
        if "Over" in line:
            spl = line.strip().split()
            f1 = float(spl[6])/100
    infile.close()
    return f1


if __name__ == "__main__":
    if len(sys.argv) < 10:
        print ("usage: %s <unlabeled set (U)> <label probabilities of U> <features of U> \n \
                          <labeled set (L)> <label probabilities of L> <features of L> \n \
                          <validation set (V)> <out path> <n (tokens to consider per sentence> \n \
                          <similarity thresh> [fraction of U to select]" % sys.argv[0])
        sys.exit(-1)


    unlab_filename = sys.argv[1]
    unlabprob_filename = sys.argv[2]
    unlabfeats_filename = sys.argv[3]

    lab_filename = sys.argv[4]
    labprob_filename = sys.argv[5]
    labfeats_filename = sys.argv[6]
    valid_filename = sys.argv[7]
    outpath = sys.argv[8]

    #"Unlabeled" dataset
    sents,labels = load_conll_probs(unlabprob_filename)
    mat = load_feats(unlabfeats_filename)
    sents,true_labels = load_conll(unlab_filename, col=2)

    #"Labeled" dataset
    Lsents,Llabels = load_conll_probs(labprob_filename)
    Lmat = load_feats(labfeats_filename)
    Lsents,Ltrue_labels = load_conll(lab_filename, col=2)

    last_unlab_index = len(mat) - 1

    n = int(sys.argv[9])
    entr_thresh = 0.6
    sim_thresh = 0.8
    frac = 0.1

    if len(sys.argv) == 12:
        frac = float(sys.argv[11])
    sim_thresh = float(sys.argv[10])

    #out = open(outpath, "w", encoding="utf-8")

    dist_thresh = 1 - sim_thresh

    print("unlabeled examples:", unlab_filename, file=sys.stderr)
    print("label probabilities of the unlabeled examples:", unlabprob_filename, file=sys.stderr)
    print("features of the unlabeled examples", unlabfeats_filename, file=sys.stderr)

    print("labeled examples:", lab_filename, file=sys.stderr)
    print("label probabilities of the labeled examples:", labprob_filename, file=sys.stderr)
    print("features of the labeled examples", labfeats_filename, file=sys.stderr)

    print("outpath:", outpath, file=sys.stderr)
    print("n:", n, file=sys.stderr)
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

    mat_filtered, indexes_sent, indexes, entropies, prob_ent = pre_select(mat, labels, last_unlab_index, n=n)
    print("len(mat)=", len(mat))

    mat_text = to_text(mat_filtered)

    print("len(mat_filtered)=", len(mat_filtered))
    #vectorizer = TfidfVectorizer(lowercase=False)
    vectorizer = CountVectorizer(lowercase=False)
    mat_filtered = vectorizer.fit_transform(mat_text)


    nselect = int(frac * len(sents))



    print("Computing similarities...")
    sim = cosine_distances(mat_filtered)

    print("Clustering...")
    #clusterer = AgglomerativeClustering(n_clusters=nselect, affinity="precomputed", linkage="average")
    clusterer = AgglomerativeClustering(n_clusters=None, affinity="precomputed", linkage="average", distance_threshold=dist_thresh)
    clusters = clusterer.fit_predict(sim)

    groups = {}

    num_labeled_in_cluster = {}
    cluster_score = {}
    for i, c in enumerate(clusters):
        if c not in groups:
            num_labeled_in_cluster[c] = 0
            cluster_score[c] = 0
            groups[c] = []
        if indexes[i] > last_unlab_index:
            num_labeled_in_cluster[c] += 1
        groups[c].append(i)

    larger_cluster_size = max([len(g) for g in groups.values()])
    log_larger_cluster_size = log(larger_cluster_size)
    NFEATURES = 3
    f1_ant = 0

    #Inicializar w com pesos aleatorios
    w = rand(NFEATURES)
    S = 20 #tamanho de cada mini-amostra
    T = 50
    A = 3 #numero de mini-amostras
    M = A #numero de pares (x, recompensa) a serem selecionados da memoria de replay
    epsilon = 0.1
    SA = S*A
    x_cluster = {}
    print("w:", w)
    lr = 1

    mem_size = 1000
    memory = [] #History of most recent pairs (x_mean, DeltaF1)

    for t in range(T):
        X = []
        selected = []
        for i, c in enumerate(clusters):
            x = [entropies[i], prob_ent[i], log(len(groups[c]))/log_larger_cluster_size]
            sc = dot(w, array(x))
            if sc > cluster_score[c]:
                cluster_score[c] = sc
                x_cluster[c] = (i, x)

        for c, sc in sorted(cluster_score.items(), key=itemgetter(1), reverse=True):
            if len(selected) > SA:
                break
            if rand() < epsilon:
                c = randint(0, len(groups))
            if num_labeled_in_cluster[c] == 0:
                i,x = x_cluster[c]
                X.append(x)
                selected.append(indexes_sent[i])
                print("sent:", sents[indexes_sent[i]])
                print("repr:", mat[indexes[i]])
                print("x:", x)

        gradient = zeros(NFEATURES)
        avg_f1 = 0

        #Para cada mini-amostra
        for a in range(A):
            subsample = X[a*S:(a+1)*S]
            x_mean = mean(array(subsample), axis=0)

            #Print selected sentences
            out = open(outpath, "w", encoding="utf-8")
            for i in selected[a*S:(a+1)*S]:
                sent_labels = true_labels[i]
                sent = sents[i]
                for j, lab in enumerate(sent_labels):
                    start,end,true_lab = lab
                    tok = sent[start:end]
                    print("%s\t%s" % (tok, true_lab), file=out)
                print(file=out)
            out.close()

            cmd = "cat " +  lab_filename + " " + outpath + " > " +  outpath + ".conll"
            #cmd = "cat " +  lab_filename + "_sample5k " + outpath + " > " +  outpath + ".conll"
            #cmd = "cat " + outpath + " > " +  outpath + ".conll"
            #os.system("cat " + outpath + ".conll")

            print(cmd)
            os.system(cmd)

            cmd = "train/make_prop.sh " + outpath + ".conll " + outpath + ".ser.gz > " + outpath + "_prop.txt"
            print(cmd)
            os.system(cmd)

            cmd = "./train_corenlp.sh " + outpath + "_prop.txt"
            print(cmd)
            os.system(cmd)

            cmd = "./test_corenlp.sh " + valid_filename + " " + outpath + ".ser.gz " + outpath + ".out"
            print(cmd)
            os.system(cmd)

            cmd = "scripts/conlleval < " + outpath + ".out -d \"\\t\" -l > " + outpath + ".metrics"
            print(cmd)
            os.system(cmd)

            f1 = extract_f1(outpath + ".metrics")
            avg_f1 += f1
            delta_f1 = f1 - f1_ant

            gradient += delta_f1 * x_mean

            memory.append( (x_mean, delta_f1) )
            if len(memory) > mem_size:
                memory.pop(0)

            print("x_mean:", x_mean)
            print("DeltaF1:", delta_f1)
            print("f1:", f1)

        mem = memory
        shuffle(mem)

        n_selected_from_mem = min(M, len(memory))
        #Use random sample from "replay" memory
        for m in range(n_selected_from_mem):
            x_mean, delta_f1 = mem[m]
            gradient += delta_f1 * x_mean

        gradient *= 1/(A+n_selected_from_mem)
        #Atualizar pesos
        w += lr * gradient
        avg_f1 /= A
        f1_ant = avg_f1
        print("avgF1:", avg_f1)
        print("w:", w)
        print("gradient:", gradient)


