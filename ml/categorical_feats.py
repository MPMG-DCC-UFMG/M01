
from numpy import array, zeros


def load_feats(filename):
    mat = []
    infile = open(filename, encoding="utf-8")
    for line in infile:
        lin = line.strip()
        if len(lin) == 0:
            continue
        row = line.strip.split("\t")
        mat.append(row)
    infile.close()
    return mat

#Similaridade entre dois vetores de atributos categoricos
def sim(a, b):
    if len(a) == 0:
        return 0
    s = 0
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


