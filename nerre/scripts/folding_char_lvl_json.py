import json
import sys
import random

random.seed(42)

infile = open(sys.argv[1], encoding="utf-8")
outdir = sys.argv[2]
nfolds = int(sys.argv[3])

data = json.load(infile)["sentences"]
infile.close()

out_trains = []
out_tests = []

for i in range(nfolds):
    out_trains.append( open(outdir + "/" + "train" + str(i) + ".json", "w", encoding="utf-8") )
    out_tests.append( open(outdir + "/" + "test" + str(i) + ".json", "w", encoding="utf-8") )


random.shuffle(data)

foldsize = int(len(data) / nfolds - 0.5)

tests = []
trains = []

for i in range(0, len(data), foldsize):
    tests.append(data[i:i+foldsize])


for i in range(nfolds):
    train = []
    for j in range(nfolds):
        if j != i : # and j != (i + 1) % nfolds:
            train += tests[j]
    trains.append(train)

for i in range(nfolds):
    json.dump({"sentences": trains[i]}, out_trains[i], indent=4)
    json.dump({"sentences": tests[i]}, out_tests[i], indent=4)

    out_trains[i].close()
    out_tests[i].close()


