from inout import load_conll
import sys
import pandas
from preprocessing.pt_stemmer import RSLPStemmer 

vowels = set(['a', 'e', 'i', 'o', 'u'])

def word_shape_num_digits(word):
    shape = ""
    ndigits = 0
    for char in word:
        if char.isdigit():
            shape += "d"
            ndigits += 1
        else:
            if char.isupper():
                shape += "X"
            else:
                shape += "x"
    if ndigits > 0:
        return shape[:10], ndigits
    else:
        return shape[:5], ndigits

def abbreviate(word):
    if len(word) == 0:
        return ""
    res = word[0]
    for c in word[1:]:
        if c not in vowels:
            res += c
    return res[:5]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input .conll file> <outfile> " % sys.argv[0])
        sys.exit(-1)

    stemmer = RSLPStemmer()
    sents,true_labels = load_conll(sys.argv[1], col=2)
    out = open(sys.argv[2], "w", encoding="utf-8")
    data  = []
    for i, labels in enumerate(true_labels):
        sent = sents[i]
        for j, lab in enumerate(labels):
            start, end, ent = lab
            tok = sent[start:end]
            prevWord = ""
            shapePrevWord = ""
            nextWord = ""
            shapeNextWord = ""
            shape, ndigits = word_shape_num_digits(tok)
            ndigitsPrev = 0
            ndigitsNext = 0

            if j > 0:
                prev_start, prev_end, prev_ent = labels[j - 1]
                prevWord = sent[prev_start : prev_end]
                shapePrevWord, ndigitsPrev = word_shape_num_digits(prevWord)

            if j < len(labels) - 1:
                next_start, next_end, next_ent = labels[j + 1]
                nextWord = sent[next_start : next_end]
                shapeNextWord, ndigitsNext = word_shape_num_digits(nextWord)

            stemmed_word = ""
            stemmed_prev = ""
            stemmed_next = ""

            if len(tok) > 0:
                stemmed_word = stemmer.stem(tok.lower())
            abbrev = abbreviate(stemmed_word)

            if len(prevWord) > 0:
                stemmed_prev = stemmer.stem(prevWord.lower())
            if len(nextWord) > 0:
                stemmed_next = stemmer.stem(nextWord.lower())

            row = [tok, ent, stemmed_prev, shapePrevWord, stemmed_word, shape, stemmed_next, shapeNextWord, ndigits, ndigitsPrev, ndigitsNext, abbrev]
            #print(row, file=out)
            #print("|".join(row), file=out)
            data.append(row)
        #print(file=out)
    data = pandas.DataFrame(data)
    data.to_csv(out)


