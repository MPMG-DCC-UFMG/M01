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


infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
data = json.load(infile)
infile.close()

for dic in data:
    print(tokens2sentence(dic["tokens"]).replace("\n", " "), file=outfile)

outfile.close()


