
from numpy import array, zeros
from operator import itemgetter
from sklearn.feature_extraction.text import *
from sklearn.metrics.pairwise import cosine_similarity
import pandas
import sys

def load_feats(filename):
    mat = []
    infile = open(filename, encoding="utf-8")
    df = pandas.read_csv(infile)
    mat = df.astype(str).iloc[:, 3:].values.tolist()
    infile.close()
    return mat


def to_text(mat):
   ncols = len(mat[0])
   mat_text = []
   for row in mat:
       row_text = ["attr" + str(j) + "_" + row[j] for j in range(ncols)]
       mat_text.append(" ".join(row_text))
   return mat_text
   

#Similaridade entre dois vetores de atributos categoricos
def sim(a, b):
    if len(a) == 0:
        return 0
    s = 0
    #print(a, b)
    for i, ai in enumerate(a):
        if ai == b[i]:
            s += 1
    return s / len(a)

def sim_matrix(a, b):
    res = zeros( (len(a), len(b)) )
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            res[i, j] = sim(ai, bj)
    return res


def todics(mat):
    res = []
    for row in mat:
        res_row = []
        for value in row:
            dic = {value : 1}
            res_row.append(dic)
        res.append(res_row)
    return res


#Categorical data represented as a list of lists of dictionaries
# (each attribute value is represented as a dictionary)
def dicmean(data):
    n_inv = 1/len(data)
    m = [ {} for d in data[0] ]
    for diclist in data:
        for i,dic in enumerate(diclist):
            for key in dic:
                mi = m[i]
                if key not in mi:
                    mi[key] = 0
                mi[key] += n_inv
    return m



def dicsim(a, b):
    s = 0
    for i, adic in enumerate(a):
        bdic = b[i]
        for akey, avalue in adic.items():
            if akey in bdic:
                s += avalue * bdic[akey]
    return s



def dicsim_matrix(A, B):
    res = zeros( (len(A), len(B)) )
    for i in range(len(A)):
        for j in range(len(B)):
            res[i, j] = dicsim(A[i], B[j])
    return res



def visualize_diclist(diclist, k=5):
    for dic in diclist:
        for key,value in sorted(dic.items(), key=itemgetter(1), reverse=True)[:k]:
            print(key, value)
        print()



#mat_text = to_text(load_feats(sys.argv[1]))
#print(mat_text)

#vectorizer = CountVectorizer(lowercase=False)
#vec = vectorizer.fit_transform(mat_text)
#print(vec)

#sim = cosine_similarity(vec)
#print(sim)


