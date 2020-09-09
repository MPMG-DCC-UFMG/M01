from inout import load_conll
import sys


def word_shape(word):
    shape = ""
    for char in word:
        if char.isdigit():
            shape += "d"
        else:
            if char.isupper():
                shape += "X"
            else:
                shape += "x"
    return shape[:5]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input .conll file> <outfile> " % sys.argv[0])
        sys.exit(-1)


    sents,true_labels = load_conll(sys.argv[1], col=2)
    out = open(sys.argv[2], "w", encoding="utf-8")

    for i, labels in enumerate(true_labels):
        sent = sents[i]
        for j, lab in enumerate(labels):
            start, end, ent = lab
            tok = sent[start:end]
            prevWord = ""
            shapePrevWord = ""
            nextWord = ""
            shapeNextWord = ""
            shape = word_shape(tok)

            if j > 0:
                prev_start, prev_end, prev_ent = labels[j - 1]
                prevWord = sent[prev_start : prev_end]
                shapePrevWord = word_shape(prevWord)

            if j < len(labels) - 1:
                next_start, next_end, next_ent = labels[j + 1]
                nextWord = sent[next_start : next_end]
                shapeNextWord = word_shape(nextWord)

            row = [tok, ent, prevWord.lower(), shapePrevWord, tok.lower(), shape, nextWord.lower(), shapeNextWord]
            print("\t".join(row), file=out)
        print(file=out)

