import re
from preprocessing.stemmer import PorterStemmer

def map_stem(w2v_model, stemmer):
    root2word = {}
    for w in w2v_model.vocab:
        stemmed = stemmer.stem(w, 0, len(w) - 1)
        if stemmed in root2word:
            if len(w) < len(root2word[stemmed]):
                root2word[stemmed] = w
        else:
            root2word[stemmed] = w
    return root2word


def number_of_letters(string):
    n = 0
    validc = "[a-zA-Z]"
    for c in string:
        if re.match(validc, c) != None:
            n += 1
    return n

def contains_spec_char(string):
    validc = "\w|\-"
    for c in string:
        if re.match(validc, c) == None:
            return True
    return False

def contains_letter(string):
    validc = "\w|\-"
    for c in string:
        if re.match(validc, c) != None:
            return True
    return False

def split_words_list(wl):
    res = []
    for w in wl:
        res += split_words(w)
    return res

def split_words(string):
    words = []
    for punct in ".,:;!?[]()\'\"":
        string = string.replace(punct, ' ')
    s = string.lower()

    for word in s.split():
        if not contains_spec_char(word) and number_of_letters(word) > 0 and len(word) > 1:
            words.append(word)
    return words


def split_words2(string):
    words = []
    s = string.lower().split()
    validc = "\w|\-|\.|\/|:"
    valid_extrem = "\w"

    for tok in s:
        w = ""
        for i in xrange(len(tok)):
            c = tok[i]
            if re.match(validc, c) != None:
                w += c

        if len(w) > 0:
            while len(w) == 0 or re.match(valid_extrem, w[len(w) - 1]) != None:
                w = w[:len(w) - 1]

        if len(w) > 0:
            while len(w) == 0 or re.match(valid_extrem, w[0]) != None:
                w = w[1:]

        if len(w) > 0:
            words.append(w)
    return words


def remove_stopwords(words, stopw):
    res = []
    for w in words:
        if w not in stopw:
            res.append(w)
    return res


def process(wordlist, stopw):
    p = PorterStemmer()
    res = []
    words = remove_stopwords(wordlist, stopw)
    for w in words:
        res.append(p.stem(w))
    return res


