import pandas
import json
import sys


def load_ents_from_json(jdata):
    res = []
    for dic in jdata:
        tokens = dic["tokens"]
        for ent in dic["entities"]:
            res.append( [" ".join(tokens[ent["start"]:ent["end"]]), ent["type"] ] )
    return pandas.DataFrame(res, columns=["ENTITY", "LABEL"])



infile = open(sys.argv[1], encoding="utf-8")
jdata = json.load(infile)
infile.close()

data = load_ents_from_json(jdata)

data["PREFIX"] = [x[:3] for x in data["ENTITY"]]
data["SUFFIX"] = [x[len(x)-4:] for x in data["ENTITY"]]


#print("PREFIX")
#for item in data["PREFIX"].value_counts().items():
#    print(item)

print("SUFFIX")
for item in data["SUFFIX"].value_counts().items():
    print(item)




