import sys
import json


json1 = open(sys.argv[1], encoding="utf-8")
json2 = open(sys.argv[2], encoding="utf-8")

out = open(sys.argv[3], "w", encoding="utf-8")


data1 = json.load(json1)
data2 = json.load(json2)

data = data1 + data2

json.dump(data, out, indent=4)

json1.close()
json2.close()
out.close()


