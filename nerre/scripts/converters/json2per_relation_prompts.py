import sys
import json

PUNCT = ",;.?!:"

import random

#Junta novamente palavras que foram separadas pelo tokenizer
def tokens2sentence(tokens):
    tokens_with_spaces = []
    for token in tokens:
        if token not in PUNCT:
            tokens_with_spaces.append(" " + token)
        else:
            tokens_with_spaces.append(token)
    return "".join(tokens_with_spaces)[1:]


def convert(data):
    res = {}
    for dic in data:
        tokens = dic["tokens"]

        ents = []
        for ent in dic["entities"]:
            label = ent["type"]
            start = ent["start"]
            end = ent["end"]
            ent_str = tokens2sentence(tokens[start: end])
            ents.append((start, end, ent_str, label))

        for rel in dic["relations"]:
            label = rel["type"].lower()
            head = rel["head"]
            tail = rel["tail"]

            if label not in res:
                res[label] = []

            i = random.randint(0, 4)
            j = random.randint(0, 4)

            head_ent = ents[head]
            tail_ent = ents[tail]

            s = head_ent[0] if head < tail else tail_ent[0]
            if s >= i:
                s -= i
            e = tail_ent[1] if head < tail else head_ent[1]
            if e + j < len(tokens):
                e += j
            text = tokens2sentence(tokens[s:e])
            head_label = head_ent[3]
            tail_label = tail_ent[3]
            head_str = head_ent[2]
            tail_str = tail_ent[2]

            prompt = f"[Texto]: {text}\n[{head_label}]: {head_str}\n[{tail_label}]: {tail_str}\n"
            res[label].append(prompt)
    return res


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)
infile.close()

res = convert(data)

json.dump(res, outfile, indent=4)
outfile.close()






