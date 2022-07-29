import sys
import json

PUNCT = ".;,?!/()"
def remove_digits_and_punct(string):
    chars = []
    for char in string:
        if char not in PUNCT and not char.isdigit():
            chars.append(char)
    return "".join(chars)


def clean_minicipio(string):
    return string.replace("-MG", "").strip()

def clean_annot(jdata):
    for dic in jdata:
        tokens = dic["tokens"]
        entities = dic["entities"]
        for ent in entities:
            start = ent["start"]
            end = ent["end"]
            if ent["type"] == "LOCAL":
                ent["type"] = "ENDERECO"
            elif ent["type"] == "PESSOA":
                for j in range(start, end):
                    tokens[j] = remove_digits_and_punct(tokens[j])
            elif ent["type"] == "MUNICIPIO":
                for j in range(start, end):
                    tokens[j] = clean_minicipio(tokens[j])


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
jdata = json.load(infile)
infile.close()

clean_annot(jdata)

json.dump(jdata, outfile, indent=4)
outfile.close()

