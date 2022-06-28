
from numpy import array
from sklearn.feature_extraction.text import *
import pandas
import sys

def load_feats_sparse(filename):
    mat = load_feats(filename)
    vectorizer = CountVectorizer(lowercase=False)
    return vectorizer.fit_transform(to_text(mat))

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
   

if __name__ == "__main__":
    vec = load_feats_sparse(sys.argv[1])
    print(vec)

