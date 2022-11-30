import sys
import json
import spacy
import uuid

tokenizer = spacy.load("pt_core_news_sm")

def convert(jdata, title=""):
    res_ents = []
    if "sentences" in jdata:
        dics = jdata["sentences"]
    else:
        dics = [jdata]
    for dic in dics:
        res_ents.append(convert_doc(dic))
    return {"name": title, "entities": res_ents}


def convert_doc(dic):
    text = dic["text"]
    entities = dic["entities"]
    if "relations" in dic:
        relations = dic["relations"]
    else:
        relations = []

    converted_entities = []
    converted_relations = []
    ent_uuids = []
    for ent in entities:
        eid = str(uuid.uuid4())
        ent_uuids.append(eid)
        start_char = ent["start"]
        end_char = ent["end"]
        label = ent["label"]
        converted_entities.append({"id": eid, "start": start_char, "end": end_char,
                                   "entity": text[start_char:end_char], "label": label})
    for rel in relations:
        ents = rel["entities"]
        head = ent_uuids[ents[0]]
        tail = ent_uuids[ents[1]]
        label = rel["label"]
        converted_relations.append({"from_annotation_id": head, "to_annotation_id": tail, "label": label})
    return {"sentence": text, "annotations": converted_entities, "relationships": converted_relations}

def map_chars2tokens(text, tokens):
    res = {}
    char_idx = 0
    for token_idx, token in enumerate(tokens):
        start_char = token.idx
        end_char = start_char + len(token)
        while char_idx < end_char:
            res[char_idx] = token_idx
            char_idx += 1
    token_idx += 1
    for i in range(char_idx, len(text)+1):
        res[i] = token_idx
    return res


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

jdata = json.load(infile)
infile.close()

jdata_new = convert(jdata, title=outfile.name)
json.dump(jdata_new, outfile, indent=4)

outfile.close()

