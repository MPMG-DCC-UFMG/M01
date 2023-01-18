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

for dic in original_data:
    tokens = dic["tokens"]
    original_texts.add(" ".join(tokens).strip().lower())

res = []

for dic in generated_data:
    tokens = dic["tokens"]
    if " ".join(tokens).strip().lower() not in original_texts:
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

    print(f'{rel_type}: {e1}({label1}) --> {e2}({label2})?')
    print(f'{text}')
    resp = input('(s/n)?')
    if resp != 'n':
        res_corrected.append(dic)

print("taxa de acertos:", len(res_corrected)/len(res))

json.dump(res_corrected, out, indent=4)

out.close()


