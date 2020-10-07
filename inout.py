import json
#import spacy
#from spacy.gold import offsets_from_biluo_tags


#nlp = spacy.load("pt")

def load_2col_annotated_data(filename):
    data = []
    infile = open(filename)
    for line in infile:
        spl = line.strip().split(",")
        label = spl[0]
        text = spl[1]
        dic = {"entities":[(0, len(text), label)]}
        data.append( (text, dic) )
    infile.close()
    return data

def json2spacy_train_data(filename):
    infile = open(filename, encoding="utf-8")
    data = json.load(infile)
    infile.close()
    res = []
    for dic in data:
        ents = {"entities": dic["labels"]}
        res.append( (dic["text"], ents) )
    return res


def load_conll(filename, col=2):
    infile = open(filename, encoding="utf-8")
    labels = []
    sents = []
    ind = 0
    acc = ""
    sent_labels = []
    for line in infile:
        lin = line.strip()
        if lin == "":
            ind = 0
            #labels.append( (0, 0, None) )
            sents.append(acc)
            labels.append(sent_labels)
            acc = ""
            sent_labels = []
        else:
            if "\t" in lin:
                spl = lin.split("\t")
            else:
                spl = lin.split()
            acc += spl[0] + " "
            start = ind
            ind += len(spl[0])
            end = ind
            sent_labels.append( [start, end, spl[col-1]] )
            ind += 1
    infile.close()
    return sents, labels

def load_conll_probs(filename, col=2):
    infile = open(filename, encoding="utf-8")
    labels = []
    sents = []
    ind = 0
    acc = ""
    sent_labels = []
    for line in infile:
        lin = line.strip()
        if lin == "":
            ind = 0
            #labels.append( (0, 0, None) )
            sents.append(acc)
            labels.append(sent_labels)
            acc = ""
            sent_labels = []
        else:
            spl = lin.split()
            acc += spl[0] + " "
            start = ind
            ind += len(spl[0])
            end = ind
            probs = {}
            for s in spl[col:]:
                spl_ = s.split("=")
                probs[spl_[0]] = float(spl_[1])
            sent_labels.append( [start, end, spl[col-1], probs] )
            ind += 1
    infile.close()
    return sents, labels



def conll2spacy_train_data(filename):
    sents, labels = load_conll(filename)
    assert len(sents) == len(labels)
    res = []
    for i in range(len(sents)):
        sent = sents[i]
        #doc = nlp(sent)
        sent_labels = labels[i]
        sent_labels2 = merge_bio_tags(sent_labels)
        #doc = nlp(sent)
        #tags = [x[2] for x in sent_labels]
        #ents = offsets_from_biluo_tags(doc, tags)
        res.append( (sent, {"entities": sent_labels2}) )
    return res


def print_conll(doc, tags, out):
    tokens = list(doc)
    assert len(tokens) == len(tags)
    for i in range(len(tokens)):
        t = tags[i]
        if len(t.replace("-", "")) < len(t) - 1:
            t = t[2:]
        print("%s %s" % (tokens[i], t), file=out)
    print(file=out)


def print_conll_paired(text, ents_dic, labels, out):
    for start, end, true_label in labels:
        span = text[start:end].replace(" ", "")
        interv = (start, end)
        if interv in ents_dic:
            print(span, true_label, remove_extra_biluo_(ents_dic[interv]), file=out)
        else:
            print(span, true_label, "O", file=out)
    print(file=out)


#Entidades indexadas no ents_dic pela string
def print_conll_paired2(text, ents_dic, labels, out):
    for start, end, true_label in labels:
        span = text[start:end]
        if span in ents_dic:
            print(span, true_label, remove_extra_biluo_(ents_dic[interv]), file=out)
        else:
            print(span, true_label, "O", file=out)
    print(file=out)

       

#Indexa entidades pelo seus offsets (indices de inicio e fim) em um dicionario
def ents2dict_conll(doc, tags):
    res = {}
    ind = 0
    i = 0
    for token in list(doc):
        start = ind
        ind += len(token)
        end = ind
        res[ (start, end) ] = tags[i]
        i += 1
        ind += 1
    return res


#Converte formato de labels BILUO para BIO
def biluo2biotags(tags):
    aux = [lab.replace("U-", "B-").replace("L-", "I-") for lab in tags]
    res = []
    for lab in aux:
        if lab.endswith("-O"):
            res.append("O")
        else:
            res.append(lab)
    return res


def remove_extra_biluo_(lab):
    if len(lab.replace("-", "")) < len(lab) - 1:
        return lab[2:]
    return lab

def remove_extra_biluo(tags):
    res = []
    for lab in tags:
        if "-" in lab:
            res.append(lab[2:])
        else:
            res.append(lab)
    return res

    #aux = [lab.replace("U-", "B-").replace("L-", "I-") for lab in tags]
    #res = []
    #for lab in aux:
    res = []
    for lab in tags:
        if "-" in lab:
            res.append(lab[2:])
        else:
            res.append(lab)
    return res

    #aux = [lab.replace("U-", "B-").replace("L-", "I-") for lab in tags]
    #res = []
    #for lab in aux:
    #    if lab.endswith("-O"):
    #        res.append("O")
    #    else:
    #        res.append(lab[2:])


def merge_bio_tags(ents):
    res = []
    i = 0
    while i < len(ents):
        start,end,lab = ents[i]
        if lab[0] == "B":
            current = lab[2:]
        else:
            current = lab
        i += 1
        if i >= len(ents):
            break
        while ents[i][2][0] == "I":
            end = ents[i][1]
            i += 1
            if i >= len(ents):
                break
        if current != "O":
            res.append( [start, end, current] )
    return res


def read_lower_cased_strings(filename):
    infile = open(filename, encoding="utf-8")
    res = set()
    for line in infile:
        res.add(line.strip().lower())
    infile.close()
    return res


def load_set(filename):
    infile = open(filename, encoding="utf-8")
    res = []
    for line in infile:
        res.append(line.strip())
    infile.close()
    return set(res)



