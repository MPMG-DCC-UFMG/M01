import json
import sys


#Hardcoded filter
def filter_json(jdata):
    #Indexes to be discarded
    #blacklist = set([240, 241, 242, 275, 284, 300, 286, 301])
    blacklist = set([5, 7, 17, 23, 32, 43, 44, 49])

    res = []
    for i, doc in enumerate(jdata):
        #Aditional filter
        #if i < 100 or (i > 150 and i < 200):
        #    continue
        if i > 48:
            break
        if i in blacklist:
            continue
        res.append(doc)
    return res


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
jdata = json.load(infile)
infile.close()

res = filter_json(jdata)

json.dump(res, outfile, indent=4)
outfile.close()


