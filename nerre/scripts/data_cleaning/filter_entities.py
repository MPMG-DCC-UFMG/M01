import sys
import json


def filter(jdata, keep="PESSOA ORGANIZACAO LEGISLACAO".split(), dontkeep="ESTADO CEP ATO ATA PRODUTO SERVICO OBJETO OBRA".split()):
    res = []
    for dic in jdata:
        tokens = dic["tokens"]
        entities = dic["entities"]
        rels = dic["relations"]
        new_ents = []
        for ent in entities:
            if ent["type"] not in dontkeep or ent["type"] in keep:
                new_ents.append(ent)
        for rel in rels:
            if rel["type"] == "proposta-valor":
                rel["type"] = "valor-proposta"
                aux = rel["head"]
                rel["head"] = rel["tail"]
                rel["tail"] = aux
        res.append({"tokens": tokens, "entities": entities, "relations": rels})
    return res

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
jdata = json.load(infile)
infile.close()

new_jdata = filter(jdata)

json.dump(new_jdata, outfile, indent=4)
outfile.close()

