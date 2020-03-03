
# Regras fixas para identificacao inicial de entidades

import re
import sys
from preprocessing.text_cleaner import *
from pycpfcnpj import cpfcnpj

import spacy
nlp = spacy.load("pt")

NSENTS=10
NAME_RE = "([A-Z\u00c0-\u00da][a-z\u00e0\u00fa]+\s)([A-Z\u00c0-\u00da][a-z\u00e0\u00fa]+\s)+"
UPPER_NAME_RE = "([A-Z\u00c0-\u00da]+\s)([A-Z\u00c0-\u00da]\s?)+"
UPPER_NAME_PATTERN = re.compile(UPPER_NAME_RE)
UPPER_NAME_MASP_RE = "([A-Z\u00c0-\u00da]+\s*)+[,/]\s[Mm][Aa][Ss][Pp]"
UPPER_NAME_MASP_PATTERN = re.compile(UPPER_NAME_MASP_RE)

NON_PER_STARTS = set("secretaria polic centro extrato companhia conselho endere\u00e7o ee e.e. escola empresa".split())
NON_PER_ENDS = set("ltda ltd.".split())

NON_ORGS = set("ano di\u00e1rio ato cpf cnpj termo caderno processo objeto partes licita\u00e7\u00e3o pr\u00eamio".split())




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


def person_org_ner(text):
    ents = []
    doc = nlp(text)
    for ent in doc.ents:
        spl = ent.text.split()
        if ent.label_ == "PER":
            if re.match(NAME_RE, ent.text) == None:
                continue
            if spl[0].lower() in NON_PER_STARTS:
                continue
            if spl[-1].lower() in NON_PER_ENDS:
                continue
            ents.append( [ent.start_char, ent.end_char, "PESSOA"] )

        if ent.label_ == "ORG":
            if ent.text.strip().lower() in NON_ORGS:
                continue
            ents.append( [ent.start_char, ent.end_char, "ORG"] )
    return ents

def additional_person_ner(text, ents_dict):
    ents = []
    for match in UPPER_NAME_PATTERN.finditer(text):
        start, end = match.span()
        if "MASP" not in text[end:end+6]:
            continue
        if (start, end) not in ents_dict:
            ents.append( [start, end, "PESSOA"] )
    return ents


def ents2dict(ents):
    res = {}
    for start, end, label in ents:
        res[ (start, end) ] = label
    return res

        

def print_output_line(out, outfile):
    print("{\"text\": \"%s\", \"labels\":" % out["text"], end=" ", file=outfile)
    labels = str(out["labels"]).replace("\'", "\"")
    print(labels, end="", file=outfile)
    #for l in out["labels"]:
    #    print(", [%d, %d, \"%s\"]" % (l[0], l[1], l[2]), end="", file=outfile)
    print("}", file=outfile)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file> <outfile> " % sys.argv[0])
        sys.exit(-1)


    patterns = load_regex_file("rules.tsv")

    infile = open(sys.argv[1], encoding="utf-8")
    outfile = open(sys.argv[2], "w", encoding="utf-8")
    outjson = open(sys.argv[2] + ".json", "w", encoding="utf-8")
    text = infile.read().replace("-\n", "")
    text = clear_special_chars(text)
    infile.close()
    sents = merge_sentences(split_sentences(text))

    for i in range(0, len(sents), NSENTS):
        sep = ". "
        text = sep.join(sents[i : i + NSENTS]).strip()
        ents = person_org_ner(text) + rule_based_ner(patterns, text)
        ents_dic = ents2dict(ents)
        ents = ents + additional_person_ner(text, ents_dic)
        ents = sorted(ents)
        out = {"text":text, "labels":ents}
        print_output_line(out, outjson)
        for start, end, ent_type in ents:
            span = text[start:end]
            print(ent_type, "\t", span, "\t\t", text[start-50:end+50], file=outfile)

    outfile.close()
    outjson.close()


