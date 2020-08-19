
# Regras fixas para identificacao inicial de entidades

import re
import sys
from preprocessing.text_cleaner import *
from pycpfcnpj import cpfcnpj
import json
from datetime import datetime
from inout import *


NSENTS=1
WSIZE=100

NAME_RE = "([A-Z\u00c0-\u00da][a-z\u00e0\u00fa]+\s)([A-Z\u00c0-\u00da][a-z\u00e0\u00fa]+\s)+"
UPPER_NAME_RE = "([A-Z\u00c0-\u00da]+\s)([A-Z\u00c0-\u00da]\s?)+"
UPPER_NAME_PATTERN = re.compile(UPPER_NAME_RE)
UPPER_NAME_MASP_RE = "([A-Z\u00c0-\u00da]+\s*)+[,/]\s[Mm][Aa][Ss][Pp]"
UPPER_NAME_MASP_PATTERN = re.compile(UPPER_NAME_MASP_RE)

NON_PER_STARTS = set("secretaria polic centro extrato companhia conselho endere\u00e7o ee e.e. escola empresa".split())
NON_PER_ENDS = set("ltda ltd.".split())

NON_ORGS = set("ano di\u00e1rio ato cpf cnpj termo caderno processo objeto partes licita\u00e7\u00e3o pr\u00eamio".split())



#TODO: adicionar IGNORE-CASE como opcao pra cada regex
def load_regex_file(filename):
    patterns = []
    infile = open(filename, encoding="utf-8")
    for line in infile:
        lin = line.strip()
        if lin.startswith("#"):
            continue
        spl = lin.strip().split("\t")
        if len(spl) < 2:
            continue
        name = spl[0]
        expr = spl[1]
        patterns.append( (name, re.compile(expr)) )
    infile.close()
    return patterns


def additional_validation(ent_type, token):
    if ent_type == "CPF" or ent_type == "CNPJ":
        return cpfcnpj.validate(token)
    return True

def rule_based_ner(rules, text):
    ents = []
    for ent_type, pattern in rules:
        for match in pattern.finditer(text):
            start, end = match.span()
            token = text[start:end]
            if additional_validation(ent_type, token):
                ents.append([start, end, ent_type])
    return ents



def ents2dict(ents):
    res = {}
    for start, end, label in ents:
        res[ (start, end) ] = label
    return res

def ents2dict_conll(doc, tags):
    res = {}
    ind = 0
    i = 0
    for token in list(doc):
        start = ind
        ind += len(token)
        end = ind
        res[ (start, end) ] = tags[i]
        i += 1
        ind += 1
    return res

  

def print_output_line(out, outfile):
    print("{\"text\": \"%s\", \"labels\":" % out["text"], end=" ", file=outfile)
    labels = str(out["labels"]).replace("\'", "\"")
    print(labels, end="", file=outfile)
    #for l in out["labels"]:
    #    print(", [%d, %d, \"%s\"]" % (l[0], l[1], l[2]), end="", file=outfile)
    print("}", file=outfile)

def mark_occupied(ents, labeled):
    for start,end,lab in ents:
        for i in range(start, end):
            labeled.add(i)

def filter_occupied(ents, labeled):
    res = []
    for start,end,lab in ents:
        include = True
        for i in range(start, end):
            if i in labeled:
                include = False
                break
        if include:
            res.append( (start, end, lab) )
    return res


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file> <outfile> [model file]" % sys.argv[0])
        sys.exit(-1)


    patterns = load_regex_file("rules.tsv")
    infilename = sys.argv[1]
    infile = open(infilename, encoding="utf-8")
    out_mp = {"file": sys.argv[1], "sentences": [], "timestamp":str(datetime.now())}
    mp_sents = out_mp["sentences"]

    outfile = open(sys.argv[2] + ".aux", "w", encoding="utf-8")
    outjson = open(sys.argv[2] + "_doccano.json", "w", encoding="utf-8")
    outfile_mp = open(sys.argv[2] + ".json", "w", encoding="utf-8")
    #out_conll =  open(sys.argv[2] + ".conll", "w", encoding="utf-8")


    conll = False

    if infilename.endswith(".conll"):
        conll = True

    if conll: #Texto de entrada montado a partir do arquivo em formato CoNLL
        sents, labels = load_conll(infilename)
        assert len(sents) == len(labels)
        NSENTS = 1
    else: #Texto de entrada livre, deve ser limpo
        infile = open(infilename, encoding="utf-8")
        text = infile.read().replace("-\n", "")
        text = clear_special_chars(text)
        sents = merge_sentences(split_sentences(text))
        infile.close()

    for i in range(0, len(sents), NSENTS):
        sep = ". "
        text = sep.join(sents[i : i + NSENTS])
        window = ""
        if i > 0:
            window += (sents[i-1] + ". ")
        window += (text + ". ")
        if i < len(sents) - 1:
            window += sents[i+1]
        labeled = set()
        ents = rule_based_ner(patterns, text)
        mp_sent = {"text": text, "entities":[]}
        mp_ents = mp_sent["entities"]

        #Trata sobreposicoes de entidades
        if conll:
            mark_occupied(ents, labeled)
            ents += filter_occupied(merge_bio_tags(labels[i]), labeled)
        ents_dic = ents2dict(ents)
        out = {"text":text, "labels":ents}
        print_output_line(out, outjson)
        for start, end, ent_type in ents:
            span = text[start:end]
            #if ent_type != "O":
            print(ent_type, "\t", span, "\t", text[max(0, start-WSIZE):start], "\t", text[end:end+WSIZE], file=outfile)
            mp_ents.append({"entity":span, "start":start, "end":end, "label":ent_type})
        mp_sents.append(mp_sent)
        #doc = nlp(text)
        #tags = [tok.ent_iob_ + "-" + tok.ent_type_ for tok in doc]
        #tags = [lab.replace("U-", "B-").replace("L-", "I-") for lab in biluo_tags_from_offsets(doc, ents)]

        #conll output
        #if False: #conll: #Se formato de entrada for CoNLL
        #    ents_dic = ents2dict_conll(doc, tags)
        #    print_conll_paired(text, ents_dic, labels[i], out_conll)
        #else:
        #    print_conll(doc, tags, out_conll)

    json.dump(out_mp, outfile_mp, indent=3)
    outfile.close()
    outjson.close()
    #out_conll.close()
    outfile_mp.close()


