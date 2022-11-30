import json
import sys

PUNCT=".,;:!?"

#Junta novamente palavras que foram separadas pelo tokenizer
def tokens2sentence(tokens):
    tokens_with_spaces = []
    for token in tokens:
        if token not in PUNCT:
            tokens_with_spaces.append(" " + token)
        else:
            tokens_with_spaces.append(token)
    return "".join(tokens_with_spaces)[1:]

#labeldic = {"LEGISLACAO": "LEGISLAÇÃO", "JURISPRUDENCIA": "JURISPRUDÊNCIA", "ORGANIZACAO": "ORGANIZAÇÃO", "MUNICIPIO": "MUNICÍPIO", "LICITACAO": "LICITAÇÃO"}
labeldic = {}

infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")

data = json.load(infile)
infile.close()


#header="#FORMAT=WebAnno TSV 3.3\n \
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|PosValue|coarseValue\n \
#T_SP=webanno.custom.Classesemntica|Classesemntica\n \
#T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency|DependencyType|flavor|BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS\n"

header="#FORMAT=WebAnno TSV 3.3\n\
#T_SP=webanno.custom.Entidade|Rtulo\n\
#T_RL=webanno.custom.Relao|Rtulo|BT_webanno.custom.Entidade\n"

print(header, file=outfile)

spanidx = 0
char_start = -1
for sent_idx, item in enumerate(data):
    char_start += 1
    tokens = item["tokens"]
    print("\n#Text=%s" % tokens2sentence(tokens).replace("\n", " ").replace("\t", " ").strip(), file=outfile)
    entities = {}
    relations = {}
    entno2start = {}
    if "entities" in item:
        ents = item["entities"]
        for entno, ent in enumerate(ents):
            ent_type = ent["type"].replace("_", "\\_")
            start = ent["start"]
            end = ent["end"]
            entno2start[entno] = start
            for i in range(start, end):
                entities[i] = (ent_type, spanidx)
            spanidx += 1
    if "relations" in item:
        for rel in item["relations"]:
            reltype = rel["type"].replace("_", "\\_")
            tail = rel["tail"]
            head = rel["head"]
            t = entno2start[tail]
            h = entno2start[head]
            if t not in relations:
                relations[t] = []
            #print("======")
            #print(entities)
            try:
                relations[t].append( (reltype, head, tail, entities[h][1], entities[t][1]) )
            except:
                print("======")
                print(entities)
    for i, token in enumerate(tokens):
        if token.strip() == "":
            continue

        if token in PUNCT and i > 0:
            char_start -= 1
        char_end = char_start + len(token)
        tid = str(sent_idx+1) + "-" + str(i+1)
        cid = str(char_start) + "-" + str(char_end)
        char_start = char_end + 1
        #if token not in PUNCT:
        #    char_start += 1
        if i in entities:
            label, spid = entities[i]
            if label in labeldic:
                label = labeldic[label]
            span = "[" + str(spid) + "]"
            sp = "*" + span
            lab = label + span
        else:
            sp = "_"
            lab = "_"

        if i in relations:
            rel = relations[i]
            obj = i
            subjs = []
            for reltype, head, tail, span_h, span_t in rel:
                subjs.append(str(sent_idx+1) + "-" + str(entno2start[head]+1) + "[" + str(span_h) + "_" + str(span_t) + "]")
            reltypes = [ elem[0] for elem in rel ]
            subjs = "|".join(subjs)
            reltypes = "|".join(reltypes)
            #star = "|".join(["*"]*len(rel))
        else:
            subjs = "_"
            reltypes = "_"
            #star = "_"
        print("\t".join([tid, cid, token, lab, reltypes, subjs, ""]), file=outfile)

outfile.close()


