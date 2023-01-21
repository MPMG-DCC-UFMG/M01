import sys
import json

generated = open(sys.argv[1], encoding="utf-8")
original = open(sys.argv[2], encoding="utf-8")

out = open(sys.argv[3], "w", encoding="utf-8")

generated_data = json.load(generated)
original_data = json.load(original)

generated.close()
original.close()

original_texts = set()
original_ents = set()

for dic in original_data:
    tokens = dic["tokens"]
    for ent in dic["entities"]:
        start = ent["start"]
        end = ent["end"]
        ent_str = " ".join(tokens[start:end]).lower()
        original_ents.add(ent_str)
    original_texts.add(" ".join(tokens).strip().lower())

res = []

for dic in generated_data:
    tokens = dic["tokens"]
    text = " ".join(tokens).strip().lower()
    if text in original_texts:
        continue
    original_texts.add(text)
    ok = True
    for ent in dic["entities"]:
        start = ent["start"]
        end = ent["end"]
        ent_str = " ".join(tokens[start:end]).lower()
        if ent_str in original_ents:
            ok = False
        original_ents.add(ent_str)
    if ok:
        res.append(dic)

print("taxa de novos exemplos:", len(res)/len(generated_data))
print("quantidade de novos exemplos:", len(res))

res_corrected = []

for dic in res:
    tokens = dic["tokens"]
    text = " ".join(tokens)
    entities = dic["entities"]
    rel_type = dic["relations"][0]["type"]

    start1 = entities[0]["start"]
    end1 = entities[0]["end"]
    label1 = entities[0]["type"]
    start2 = entities[1]["start"]
    end2 = entities[1]["end"]
    label2 = entities[1]["type"]

    e1 = " ".join(tokens[start1:end1])
    e2 = " ".join(tokens[start2:end2])

    #print(f'{rel_type}: {e1}({label1}) --> {e2}({label2})?')
    #print(f'{text}')

    if False: #rel_type in ["localizado_em", "contrato-licitacao"]:
        resp = input('(s/n)?')
        if resp != 'n':
            res_corrected.append(dic)
    else:
        res_corrected.append(dic)

print("taxa de acertos:", len(res_corrected)/len(res))

json.dump(res_corrected, out, indent=4)

out.close()


