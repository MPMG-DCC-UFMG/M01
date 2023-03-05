import sys
import json

predicted = open(sys.argv[1], encoding="utf-8")
expected_answer = open(sys.argv[2], encoding="utf-8")

out = open(sys.argv[3], "w", encoding="utf-8")

predictions = json.load(predicted)
answer = json.load(expected_answer)


predictions = predictions["sentences"] if "sentences" in predictions else [predictions]
answer = answer["sentences"] if "sentences" in answer else [answer]

predicted.close()
expected_answer.close()

to_check = {"data_abertura"}

def get_entities(dic_ents):
    return [(ent["start"], ent["end"]) for ent in dic_ents]

def get_relation_tuple(rel, ent_list):
    e1 = rel["entities"][0]
    e2 = rel["entities"][1]
    return ent_list[e1], ent_list[e2]


res = []

for dic_pred, dic_true in zip(predictions, answer):
    text = dic_true["text"]
    ents_pred = dic_pred["entities"]
    ents_true = dic_true["entities"]
    ent_list_pred = get_entities(ents_pred)
    ent_list_true = get_entities(ents_true)
    processed_relations = set()

    new_relations = []
    for rel in dic_pred["relations"]:
        rel_tuple = get_relation_tuple(rel, ent_list_pred)
        if rel_tuple not in processed_relations:
            if rel["label"] not in to_check:
                new_relations.append(rel)
            else:
                print(text)
                h, t = rel["entities"]
                print(rel["label"], ":", ents_pred[h], "-->", ents_pred[t])
                resp = input("Correct? (s/n): ")
                if resp != "n":
                    new_relations.append(rel)
            processed_relations.add(rel_tuple)

    for rel in dic_true["relations"]:
        rel_tuple = get_relation_tuple(rel, ent_list_true)
        if rel_tuple not in processed_relations:
            if True: #rel["label"] not in to_check:
                new_relations.append(rel)
            else:
                print(text)
                h, t = rel["entities"]
                print(rel["label"], ":", ents_true[h], "-->", ents_true[t])
                resp = input("Correct? (s/n): ")
                if resp != "n":
                    new_relations.append(rel)
            processed_relations.add(rel_tuple)
    res.append({"text": text, "entities": ents_true, "relations": new_relations})

json.dump({"sentences": res}, out, indent=4)
out.close()

