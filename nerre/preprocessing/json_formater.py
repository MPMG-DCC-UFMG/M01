import json
from datetime import datetime

PUNCT=".,;?!:"

#Funcoes de convercao de formatos

def to_iob(jdata, outfile):
    for obj in jdata:
        idx2ent = {}
        for ent in obj["entities"]:
            start = ent["start"]
            end = ent["end"]
            ent_type = ent["type"]
            idx2ent[start] = (ent_type, end)

        tokens = obj["tokens"]
        i = 0
        while i < len(tokens):
            print(tokens[i].replace(" ", ""), end=" ", file=outfile)
            if i in idx2ent:
                ent_type, end = idx2ent[i]
                print("B-" + ent_type, file=outfile)
                i += 1
                while i < end:
                    print(tokens[i].replace(" ", ""), end=" ", file=outfile)
                    print("I-" + ent_type, file=outfile)
                    i += 1
            else:
                print("O", file=outfile)
                i += 1
        print(file=outfile)


def to_char_level_format(jdata, source_file=None, dest_file=None, use_entity_indices=False):
    segments = []
    res = {}
    for dic in jdata:
        idx_token2char = {}
        tokens = dic["tokens"]
        char_idx = 0
        tokens_and_spaces = []
        if len(tokens) > 0:
            tokens_and_spaces.append(tokens[0])
            idx_token2char[0] = char_idx
            char_idx += len(tokens[0])
        for i in range(1, len(tokens)):
            token = tokens[i]
            if token in PUNCT:
                tokens_and_spaces.append(token)
            else:
                tokens_and_spaces.append(" ")
                tokens_and_spaces.append(token)
                char_idx += 1
            idx_token2char[i] = char_idx
            char_idx += len(token)
        segment_text = "".join(tokens_and_spaces)
        new_entities = []
        if "entities" in dic:
            entities = dic["entities"]
            for ent in entities:
                try:
                    start = ent["start"]
                    end = ent["end"] - 1
                    start_char = idx_token2char[start]
                    end_char = idx_token2char[end] + len(tokens[end])
                    new_entities.append({"entity": segment_text[start_char:end_char],
                                         "start": start_char, "end": end_char,
                                         "label": ent["type"]})
                except:
                    print("tokens:", tokens)
                    print("entity:", ent)
        new_relations = []
        if "relations" in dic:
            relations = dic["relations"]
            for rel in relations:
                if use_entity_indices:
                    ent_a = rel["head"]
                    ent_b = rel["tail"]
                else:
                    ent_a = new_entities[rel["head"]]["entity"]
                    ent_b = new_entities[rel["tail"]]["entity"]
                new_relations.append({"entities": [ent_a, ent_b],
                                      "label": rel["type"]})
        segments.append({"text": segment_text,
                         "entities": new_entities,
                         "relations": new_relations})
    res["timestamp"] = str(datetime.now())
    if source_file != None:
        res["src_file"] = source_file
    if dest_file != None:
        res["file"] = dest_file
    res["sentences"] = segments

    return res



def match_tokens(ent_str, tokens, start_from=0):
    token_idx = start_from
    char2token = {}
    j = 0
    for i in range(start_from, len(tokens)):
        token = tokens[i]
        for c in token:
            if c != " ":
                char2token[j] = i
                j += 1

    #print("len(char2token):", len(char2token))
    to_match = ent_str.replace(" ", "")
    tokens_str = "".join(tokens[start_from:]).replace(" ", "")

    #print("to_match:", to_match)
    #print("tokens_str:", tokens_str)

    c = tokens_str.find(to_match)
    if c != -1:
        return char2token[c], 1+char2token[c+len(to_match)-1]
    else:
        return -1, 0




class JsonFormater:
    #tokenizer: spaCy model
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.labels = {"DATA": "Data", "CPF": "Id", "CNPJ": "Jurídica", "MASP": "Matrícula", "LOCAL": "Local", "ORGANIZACAO": "Org", "COMPETENCIA": "Cargo", "LEGISLACAO": "Lei"}

    #ents = triples (start, end, label)
    def format(self, text, ents):
        ind_char = 0
        tokens = []
        entities = []
        for start_char, end_char, label in sorted(ents):
            #Tokens before entity
            tokens += [ token.text for token in self.tokenizer(text[ind_char:start_char].strip()) ]
            ind = len(tokens)

            #Entity tokens
            tokens += [ token.text for token in self.tokenizer(text[start_char:end_char].strip()) ]
            entities.append( {"start": ind, "end": len(tokens), "type": label, "score": 0.999999} )
            ind_char = end_char

        #Tokens after last entity
        tokens += [ token.text for token in self.tokenizer(text[ind_char:].strip()) ]
        return {"tokens":tokens, "entities": entities}


    def format_given_json(self, text, ents, jdoc):
        tokens = jdoc["tokens"]
        entities = []
        not_found = 0
        end = 0
        ent_map = {}
        for start_char, end_char, label in sorted(ents):
            ent_str = text[start_char:end_char]
            start,end = match_tokens(ent_str, tokens, start_from=end)
            if start != -1:
                entities.append({"start":start, "end":end, "type":label, "score":1})
            else:
                not_found += 1
        orig_ents = []
        if "entities" in jdoc:
            orig_ents = jdoc["entities"] 
        #print("Not matched entities:", not_found)
        return {"tokens":tokens, "entities": entities + orig_ents}


    #TO UPDATE
    def mark_ents(self, data):
        res = []
        for dic in data:
            tokens = [t for t in dic["tokens"]]
            if "entities" in dic:
                entities = dic["entities"]
            else:
                entities = []

            if "relations" in dic:
                relations = dic["relations"]
            else:
                relations = []

            #if len(tokens) + 2*len(entities) > 255:
            #    continue
            for ent in entities:
                start = ent["start"]
                end = ent["end"]
                label = ent["type"]
                if label in self.labels:
                    tokens[start] = "[" + self.labels[label] + " " + tokens[start]
                    tokens[end-1] += " " + self.labels[label] + "]"
            res.append({"tokens":tokens, "entities": entities, "relations": relations})
        return res


#Test

if __name__ == '__main__':

    import spacy
    tokenizer = spacy.load("pt_core_news_sm")

    formater = JsonFormater(tokenizer)
    data = formater.format(u"O Nobre Rato roeu a roupa do rei de Roma.", [(2, 12, "PER"), (38, 42, "LOC")])
                            #012345678901234567890123456789012345678901
                            #0         1         2         3         4
    print(json.dumps([data], indent=4))
    segs = to_char_level_format([data])
    print(json.dumps(segs, indent=4))


