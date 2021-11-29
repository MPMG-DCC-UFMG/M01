import sys
import json
import pandas
import spacy

nlp = spacy.load("pt")



def find_ent(ahead, ent_tokens):
    for i in range(len(ent_tokens)):
        match = True
        ent = ent_tokens[i]
        #[ print("ent_tok:", e) for e in ent ]
        for j in range(len(ent)):
            #print("====", ahead[j], "VS", ent[j], "====")
            try:
                cond = (ahead[j].text.lower() != ent[j].text.lower())
            except:
                print("Error processing:", ent, "sentence:", ahead, file=sys.stderr)
                cond = True
            #print(cond)
            if cond:
                match = False
                break
        if match:
            return i
    return -1 #not found
           


#data = pd.DataFrame(rows, columns="SENTENCE MANUALLY_CHECKED ENTITY1 TYPE1 ENTITY2 TYPE2 REL_TYPE".split())

print("Reading DataFrame...", file=sys.stderr)

infile = open(sys.argv[1], encoding="utf-8")
data = pandas.read_csv(infile)
infile.close()

data.sort_values(by="FRASE", inplace=True)

out = open(sys.argv[2], "w", encoding="utf-8")

#data = data[data["MANUALLY_CHECKED"] == "true"]
sent_ents_rels = []
row = data.iloc[0]["FRASE"]
current_sent = " ".join(row.replace("-\n", "").replace("\n", " ").replace(",", " , ").split())

print("First sent:", current_sent)
ents = set()
rels = {}

print("Extracting sentences/entities...",  file=sys.stderr)

for i,row in data.iterrows():
    sent = " ".join(row["FRASE"].replace("-\n", "").replace("\n", " ").replace(",", " , ").split())
    if sent != current_sent:
       sent_ents_rels.append( (current_sent, list(ents), rels) )
       ents = set()
       rels = {}
    ent1 = " ".join(row["ENTIDADE_1"].strip().replace("-\n", "").replace("\n", " ").split())
    ent2 = " ".join(row["ENTIDADE_2"].strip().replace("-\n", "").replace("\n", " ").split())
    rel_type = row["TIPO_RELACAO"]

    ents.add( (ent1, row["TIPO_ENTIDADE_1"]) )
    if ent2 != "-":
        ents.add( (ent2, row["TIPO_ENTIDADE_2"]) )
    if rel_type != "-":
        if ent1 not in rels:
            rels[ent1] = {}
        rels[ent1][ent2] = rel_type
    current_sent = sent

sent_ents_rels.append( (current_sent, list(ents), rels) )

print(len(sent_ents_rels), "sentences found.", file=sys.stderr)
print("Converting format...",  file=sys.stderr)


idx = 0
res = []

for sent,ents,rels in sent_ents_rels:
    print(idx, file=sys.stderr)
    idx += 1
    #if s > 1:
    #    break
    doc = nlp(sent)
    tokens = [ d.text for d in doc ]
    triples_ents = []
    ent_tokens = []
    for ent, ent_type in ents:
        ent_tokens.append(nlp(ent))

    i = 0
    while i < len(doc):
        ahead = doc[i:]
        pos = find_ent(ahead, ent_tokens)
        if pos == -1:
            i += 1
        else:
            ent_text = ents[pos][0]
            t = ents[pos][1]
            start = i
            end = i + len(ent_tokens[pos])
            i += len(ent_tokens[pos])
            triples_ents.append( (start, end, t, ent_text) )
    res_ents = []
    ent2index = {}
    ent_idx = 0
    for start, end, t, ent_text in sorted(triples_ents):
        res_ents.append( {"start": start, "end": end, "type": t} )
        ent2index[ent_text] = ent_idx
        ent_idx += 1

    res_rel = []
    for ent1,dic in rels.items():
        for ent2,rel_type in dic.items():
            if ent1 not in ent2index:
                e1 = [ x.text for x in nlp(ent1) ]
                print("Entity not found:", e1, "Text:", tokens)
                continue
            if ent2 not in ent2index:
                e2 = [ x.text for x in nlp(ent2) ]
                print("Entity not found:", e2, "Text:", tokens)
                continue
            res_rel.append( {"head":ent2index[ent1], "tail":ent2index[ent2], "type":rel_type} )

    if len(res_rel) > 0:
        res.append( {"orig_id": idx, "tokens": tokens, "entities": res_ents, "relations": res_rel} )



json.dump(res, out, indent=4)

out.close()



