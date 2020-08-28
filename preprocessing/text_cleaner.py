# coding: utf-8
import sys
import re


def extract_digits(string):
    digits = []
    for char in string:
        if char.isdigit():
            digits.append(char)
    return "".join(digits)


def clear_special_chars(text):
    res = ""
    for c in text:
        if (c >= "\u0020" and c <= "\u007E") or (c >= "\u00A1" and c <= "\u00FF") or c == "\n":
            res += c
        else:
            res += " "
    return res


def tokenize(string):
    for punct in ".,:;!?":
        string = string.replace(punct, " ")
    return string.split()


#Utility function to return a list of sentences.
#@param text The text that must be split in to sentences.

def split_sentences(text):
    sentence_delimiters = re.compile(u'[\\[\\].!?;]\s|\n')
    sentences = sentence_delimiters.split(text)
    return sentences


#Merge sentences that should not be separated

def merge_sentences(sentences):
    new_sents = []
    acc = ""
    for sentence in sentences:
        sent = sentence.strip()
        if len(sent) < 1:
            continue
        if sent[0].isupper():
            if acc != "":
                new_sents.append(acc.strip())
            acc = ""  
        acc += " " + sent
    new_sents.append(acc.strip())
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
    outfile = open(sys.argv[2], "w", encoding="utf-8")
    infile = open(sys.argv[1], encoding="utf-8")

    replace_list = [ ["-\n", ""], [" / ", "/"], ["Av.", "Av"], ["\u00ba.", "\u00ba"], ["\u00aa.", "\u00aa"] ]

    text = infile.read()
    text = replacements(clear_special_chars(text), replace_list)
    outfile.write(text)
    outfile.close()


