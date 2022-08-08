import sys
import json


def load_webanno(filename):
    infile = open(filename, encoding="utf-8")
    rows = []
    for line in infile:
        lin = line.strip()
        if lin.startswith("#"):
            continue
        spl = lin.split("\t")
        if len(spl) == 4:
            spl += ["_", "_"]
        rows.append(spl)
    infile.close()
    return rows


rows = load_webanno(sys.argv[1])
outfile = open(sys.argv[2], "w", encoding="utf-8")


span_sizes = {}
span_labels = {}
start2eid = {}
spanid2eid = {}
eid = -1
doc2eids = {}

for row in rows:
    #3-1        28-33   Frase   PESSOA[1]       data de aquisição       1-2[0_1]
    if len(row) < 6:
        continue
    rid, char_idx, token, ent_type, rel_type, related_to = row
    spl = rid.split("-")
    doc_id = int(spl[0])
    if doc_id not in doc2eids:
        doc2eids[doc_id] = []
    token_id = int(spl[1])
    if ent_type != "_":
        k = ent_type.find("[")
        if k != -1:
            spanid = ent_type[k+1:len(ent_type)-1]
            label = ent_type[:k]
            if spanid not in spanid2eid:
                eid += 1
                spanid2eid[spanid] = eid
                span_sizes[eid] = 0
                start2eid[rid] = eid
                doc2eids[doc_id].append(eid)
            span_sizes[eid] += 1
            span_labels[eid] = label.replace("\\", "")
        else:
            eid += 1
            label = ent_type
            span_sizes[eid] = 1
            start2eid[rid] = eid
            doc2eids[doc_id].append(eid)
            span_labels[eid] = label.replace("\\", "")



#Second pass: relations

entities = [ [] for i in range(len(doc2eids)) ]
relations = [ [] for i in range(len(doc2eids)) ]
tokens = [ [] for i in range(len(doc2eids)) ]

for row in rows:
    #3-1        28-33   Frase   PESSOA[1]       data de aquisição       1-2[0_1]
    if len(row) < 6:
        continue
    rid, char_idx, token, ent_type, rel_type, related_to = row
    spl = rid.split("-")
    doc_id = int(spl[0])
    token_id = int(spl[1])
    ents = entities[doc_id-1]
    rels = relations[doc_id-1]
    tokens[doc_id-1].append(token)

    if rel_type != "_":
        types = rel_type.split("|")
        subjs = related_to.split("|")
        m = min(doc2eids[doc_id])
        for i, rel in enumerate(types):
            subj = subjs[i].split("[")[0]
            head = start2eid[subj] - m
            tail = start2eid[rid] - m
            rels.append({"head":head, "tail":tail, "type":rel.replace("\\", "")})

    if rid in start2eid:
        eid = start2eid[rid]
        ents.append({"start":token_id-1, "end":token_id + span_sizes[eid] - 1, "type": span_labels[eid]})


jdata = []
for i in range(len(tokens)):
    jdata.append({"tokens":tokens[i], "entities":entities[i], "relations":relations[i]})


json.dump(jdata, outfile, indent=4)
outfile.close()


