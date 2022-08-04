import sys
import json

def print_ents(jdata, label):
    for dic in jdata["sentences"]:
        for ent in dic["entities"]:
            if ent["label"] == label:
                print(ent["entity"])
        print()

infile = open(sys.argv[1], encoding="utf-8")
label = sys.argv[2]
jdata = json.load(infile)
infile.close()

print_ents(jdata, label)



