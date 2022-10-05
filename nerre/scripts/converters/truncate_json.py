import sys
import json

#from transformers import BertTokenizer, BertModel

#tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)
res = []

max_size = 200
total = 0
total_new = 0

for item in data:
    tokens = item["tokens"]
    #tokens_bert = tokenizer.tokenize(" ".join(tokens))
    #print(len(tokens_bert))
    #if len(tokens_bert) > 510:
    #    print(tokens)
    ents = item["entities"]
    rels = item["relations"]
    total += len(ents)
    new_tokens = tokens[:max_size + 1]
    new_ents = []
    new_rels = []
    to_exclude = set()

    for i, ent in enumerate(ents):
        end = ent["end"]
        start = ent["start"]
        label = ent["type"]
        if end - start < 1:
            print(tokens[start:start+2], ent["type"])
        if end < max_size:# and start < max_size:
            new_ents.append(ent)
        else:
            to_exclude.add(i)
    for rel in rels:
        head = rel["head"]
        tail = rel["tail"]
        if not (head in to_exclude or tail in to_exclude):
            new_rels.append(rel)
    res.append({"tokens": new_tokens, "entities": new_ents, "relations": new_rels})
    total_new += len(new_ents)

print("%%kept instances:", len(res) / len(data))
print("%%kept entities:", total_new / total)
json.dump(res, outfile, indent=4)

