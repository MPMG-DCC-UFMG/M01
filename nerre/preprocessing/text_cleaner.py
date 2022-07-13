# coding: utf-8
import sys
import re

import spacy

nlp = spacy.load("pt_core_news_sm")

from unicodedata import normalize


PUNCT=".,:;!?"

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('UTF-8')

def extract_digits(string):
    digits = []
    for char in string:
        if char.isdigit():
            digits.append(char)
    return "".join(digits)


def clear_special_chars(text):
    res = ""
    for c in text:
        if (c >= "\u0020" and c <= "\u007E") or (c >= "\u00A1" and c <= "\u00FF"):
            res += c
        else:
            res += " "
    return res


def tokenize(string, hifen=False):
    puncts = ".,:;!?"
    if hifen:
        puncts += "-"
    for punct in puncts:
        string = string.replace(punct, " ")
    return string.split()


#Junta novamente palavras que foram separadas pelo tokenizer
def tokens2sentence(tokens):
    tokens_with_spaces = []
    for token in tokens:
        if token not in PUNCT:
            tokens_with_spaces.append(" " + token)
        else:
            tokens_with_spaces.append(token)
    return "".join(tokens_with_spaces)[1:]


#Utility function to return a list of sentences.
#@param text The text that must be split in to sentences.

def split_sentences(text):
    sentence_delimiters = re.compile(u'[\\[\\].!\?]\s')
    sentences = sentence_delimiters.split(text)
    return sentences



def tokenize_sentences(text, approx_seg_size=600, min_seg_size=100):
    end_of_sentence_pattern = re.compile("[\.\?][\s\n]+[A-Z]")
    sentences = []
    acc = ""
    #matches = end_of_sentence_pattern.finditer(text)
    #print("len(matches):", list(matches))
    previous_start = 0
    for match in end_of_sentence_pattern.finditer(text):
        start = match.start()
        segment = text[previous_start: start + 1]
        acc += segment
        prev_seg = text[:start]
        if len(acc) > approx_seg_size and len(segment) > min_seg_size and (not is_acronym(prev_seg[-10:].strip().split()[-1])):
            sentences.append(acc)
            acc = ""
        previous_start = start + 1
    sentences.append(acc + text[previous_start:])
    return sentences


def is_acronym(token):
    return (len(token) < 4) or (len(token) < 7 and token.isupper())

#Merge sentences that should not be separated

def merge_sentences(sentences):
    new_sents = []
    acc = ""
    for sent_idx, sentence in enumerate(sentences):
        #print(sentence)
        if sent_idx > 0:
            prev_sent = sentences[sent_idx-1].strip()
        else:
            prev_sent = "a"
        sent = sentence.strip()
        #print("prev_sent", prev_sent)
        if len(sent) < 1 or len(prev_sent) < 1:
            continue
        if sent[0].isupper() and (not is_acronym(prev_sent[-10:].strip().split()[-1]) or len(acc) > 350) :
            if acc != "":
                new_sents.append(acc.strip())
            acc = ""  
        acc += " " + sent
    new_sents.append(" ".join(acc.strip().split()))
    return new_sents



def replacements(text, replace_list):
    for expr,repl in replace_list:
        text = text.replace(expr, repl)
    return text

#Limpa texto e exclui linhas que nao tem entidades nomeadas

def clean_text(text):
    res = []
    lines = text.replace("-\n", "").split("\n")
    for line in lines:
        if len(line) < 3:
            continue
        doc = nlp(line)
        if len(doc.ents) > 0:
            res.append(line)
    print("lines with entities:", len(res)/len(lines))
    return " ".join(res)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file> <outfile> " % sys.argv[0])
        sys.exit(-1)

    rows = []
    #outfile = open(sys.argv[2], "w", encoding="utf-8")
    infile = open(sys.argv[1], encoding="utf-8")

    replace_list = [ ["-\n", ""], [" / ", "/"], ["\u00ba.", "\u00ba"], ["\u00aa.", "\u00aa"] ]

    text = infile.read()
    text = replacements(clear_special_chars(text), replace_list)
    sents = tokenize_sentences(text)
    print("\n===============\n".join(sents))
    #outfile.close()


