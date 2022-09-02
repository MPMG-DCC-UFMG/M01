import sys
import json


def delete_annot(jdata, start, end):
    for i in range(start, end+1):
        if i >= len(jdata):
            break
        jdata[i]["entities"] = []
        jdata[i]["relations"] = []

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

start = int(sys.argv[3])
end = int(sys.argv[4])

jdata = json.load(infile)
infile.close()

delete_annot(jdata, start, end)

json.dump(jdata, outfile, indent=4)
outfile.close()

