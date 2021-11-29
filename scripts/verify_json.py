import sys
import json
import tqdm

infile = open(sys.argv[1], encoding="utf-8")
data = json.load(infile)

for dic in tqdm.tqdm(data):
    tokens = dic["tokens"]
    entities = dic["entities"]
    relations = dic["relations"]
    for ent in entities:
        start = ent["start"]
        end = ent["end"]
        if start >= end:
            print("Ent start >= end Error in:", tokens)
        if start >= len(tokens):
            print("Ent Error in:", tokens)
        if end > len(tokens):
            print("Ent Error in:", tokens)
    for rel in relations:
        head = rel["head"]
        tail = rel["tail"]
        if head >= len(entities):
            print("Rel Error in:", tokens)
        if tail >= len(entities):
            print("Rel Error in:", tokens)


