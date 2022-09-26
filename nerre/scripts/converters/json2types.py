import sys
import json


infile = open(sys.argv[1], encoding="utf-8")

objs = json.load(infile)
infile.close()


types = set( [ rel["type"] for obj in objs for rel in obj["relations"] ] )
ents = set( [ ent["type"] for obj in objs for ent in obj["entities"] ] )

entities = {}
for ent in ents:
    entities[ent] = {"short":ent[:15], "verbose":ent}

relations = {}
for t in types:
    relations[t] = {"short":t[:15], "verbose":t, "symmetric":False}

dic = {"entities":entities, "relations":relations}

out = open(sys.argv[2], "w", encoding="utf-8")
json.dump(dic, out, indent=4)
out.close()
