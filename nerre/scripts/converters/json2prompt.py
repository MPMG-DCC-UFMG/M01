import sys
import json

PUNCT = ",;.?!:"


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
    res = []
    for dic in data:
        rows = []
        tokens = dic["tokens"]
        text = tokens2sentence(tokens)
        rows.append(f"[Texto]: {text}")
        ent_strs = []
        added_ents = set()
        for ent in dic["entities"]:
            label = ent["type"].lower()
            ent_str = tokens2sentence(tokens[ent["start"]:ent["end"]])
            ent_strs.append(ent_str)
            ent_str_low = ent_str.lower()
            if ent_str_low not in added_ents:
                rows.append(f"[entidade]: {label}: {ent_str}")
                added_ents.add(ent_str_low)
        for rel in dic["relations"]:
            label = rel["type"].lower()
            head = ent_strs[rel["head"]]
            tail = ent_strs[rel["tail"]]
            rows.append(f"[relação]: {head}; {label}; {tail}")
        res.append("\n".join(rows))
    return "\n###\n".join(res)


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)
infile.close()
s = convert(data)
print(s, file=outfile)
outfile.close()


