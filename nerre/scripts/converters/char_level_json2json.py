import sys
import json
import spacy

tokenizer = spacy.load("pt_core_news_sm")

def convert(jdata):
    res = []
    if "sentences" in jdata:
        dics = jdata["sentences"]
    else:
        dics = [jdata]
    for dic in dics:
        res.append(convert_doc(dic))
    return res


def convert_doc(dic):
    text = dic["text"]
    entities = dic["entities"]
    relations = dic["relations"]

    tokens = tokenizer(text)
    tokens_text = [tok.text for tok in tokens]
    char2token = map_chars2tokens(text, tokens)

    converted_entities = []
    converted_relations = []

    for ent in entities:
        start_char = ent["start"]
        end_char = ent["end"]
        label = ent["label"]
        start_token = char2token[start_char]
        end_token = char2token[end_char]
        converted_entities.append({"start": start_token, "end": end_token, "type": label})
    for rel in relations:
        ents = rel["entities"]
        head = ents[0]
        tail = ents[1]
        label = rel["label"]
        converted_relations.append({"head": head, "tail": tail, "type": label})
    return {"tokens": tokens_text, "entities":converted_entities, "relations": converted_relations}

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

jdata_new = convert(jdata)
json.dump(jdata_new, outfile, indent=4)

outfile.close()

