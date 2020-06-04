from inout import *
import sys
import spacy
from preprocessing.text_cleaner import * 
from spacy.gold import biluo_tags_from_offsets

NSENTS=10

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("usage: %s <input file> <model dir> <output file> " % sys.argv[0])
        sys.exit(-1)

    nlp = spacy.load(sys.argv[2])

    filename = sys.argv[1]
    infile = open(filename, encoding="utf-8")
    outfile = open(sys.argv[3], "w", encoding="utf-8")
    conll = False

    if filename.endswith(".conll"):
        sents, labels = load_conll(infile)
        NSENTS = 1
        conll = True
    else: #Texto de entrada livre, deve ser limpo
        text = infile.read().replace("-\n", "")
        text = clear_special_chars(text)
        sents = merge_sentences(split_sentences(text))
    infile.close()

    for i in range(0, len(sents), NSENTS):
        sep = ". "
        text = sep.join(sents[i : i + NSENTS])
        doc = nlp(text)
        ents = [ (ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        biluo_tags = biluo_tags_from_offsets(doc, ents)
        tags = biluo2biotags(biluo_tags)

        #tags = [ent.label_ for ent in doc.ents]
        #conll output
        if conll: #Se formato de entrada for CoNLL
            ents_dic = ents2dict_conll(doc, tags)
            print_conll_paired(text, ents_dic, labels[i], outfile)
        else:
            print_conll(doc, tags, outfile)

    outfile.close()
