import sys
import json

def do_it(jdata):
    n_ents = 0
    n_rels = 0
    for dic in jdata:
        n_ents += len(dic["entities"])
        if "relations" in dic:
            n_rels += len(dic["relations"])
    print("n_texts:", len(jdata), "n_ents:", n_ents, "n_rels:", n_rels)

infile = open(sys.argv[1], encoding="utf-8")
jdata = json.load(infile)
infile.close()

do_it(jdata)

