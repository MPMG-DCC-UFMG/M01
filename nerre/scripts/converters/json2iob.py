import sys
from datetime import datetime

PUNCT=".,;?!:"

#Funcoes de convercao de formatos

def to_iob(jdata, outfile):
    for obj in jdata:
        idx2ent = {}
        for ent in obj["entities"]:
            start = ent["start"]
            end = ent["end"]
            ent_type = ent["type"]
            idx2ent[start] = (ent_type, end)

        tokens = obj["tokens"]
        i = 0
        while i < len(tokens):
            print(tokens[i].replace(" ", ""), end=" ", file=outfile)
            if i in idx2ent:
                ent_type, end = idx2ent[i]
                print("B-" + ent_type, file=outfile)
                i += 1
                while i < end:
                    print(tokens[i].replace(" ", ""), end=" ", file=outfile)
                    print("I-" + ent_type, file=outfile)
                    i += 1
            else:
                print("O", file=outfile)
                i += 1
        print(file=outfile)


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

jdata = json.load(infile)
infile.close()

to_iob(jdata, outfile)
outfile.close()



