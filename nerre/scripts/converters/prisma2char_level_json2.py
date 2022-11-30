import sys
import json
import sys

def convert(jdata):
    res_segments = []
    segments = jdata["entities"]
    for dic in segments:
        res_segments.append(convert_doc(dic))
    return {"sentences": res_segments}


def convert_doc(dic):
    text = dic["sentence"]
    entities = dic["annotations"]
    relations = dic["relationships"]

    converted_entities = []
    converted_relations = []
    mapping = {}

    for i, ent in enumerate(entities):
        eid = ent["id"]
        mapping[eid] = i
        # start_char = ent["start"]
        # end_char = ent["end"]
        # label = ent["label"]
        # converted_entities.append({"start": start_char, "end": end_char, "label": label})
    for rel in relations:
        h = rel["from_annotation_id"]
        t = rel["to_annotation_id"]
        head = mapping[h]
        tail = mapping[t]
        label = rel["label"]
        converted_relations.append({"entities": [head, tail], "label": label})
    return {"text": text, "entities": entities, "relations": converted_relations}


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

jdata = json.load(infile)
infile.close()

jdata_new = convert(jdata)
json.dump(jdata_new, outfile, indent=4)

outfile.close()

