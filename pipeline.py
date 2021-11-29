
import sys
import json
from preprocessing.text_cleaner import merge_sentences, split_sentences, clear_special_chars, replacements, tokens2sentence
from preprocessing.json_formater import JsonFormater, to_iob
from regex_ner import RegexNER
import spacy

class Pipeline:

    def __init__(self):
        self.replace_list = [ ["-\n", ""], [" / ", "/"], ["Av.", "Av"], ["\u00ba.", "\u00ba"], ["\u00aa.", "\u00aa"] ]
        self.tokenizer = spacy.load("pt_core_news_sm")
        self.regex_ner = RegexNER("rules_do.tsv")
        self.json_formater = JsonFormater(self.tokenizer)


    def process(self, text):
        text = replacements(clear_special_chars(text), self.replace_list)
        sents = merge_sentences(split_sentences(text))
        print("#Number of sentences:", len(sents))
        res = []
        for sent in sents:
            ents = self.regex_ner.ner(sent)
            res.append(self.json_formater.format(sent, ents))

        marked = res.copy()
        marked = self.json_formater.mark_ents(marked)
        return marked
        #return sents

    def process_json(self, data):
        res = []
        dif = 0
        for dic in data:
            tokens = dic["tokens"]
            sent = tokens2sentence(tokens)
            ents = self.regex_ner.ner(sent)
            item = self.json_formater.format_given_json(sent, ents, dic)
            res.append(item)
            if len(item["tokens"]) != len(tokens):
                dif += 1
        print("diff:", dif)
        marked = res.copy()
        marked = self.json_formater.mark_ents(marked)

        #Get original labels
        for i,dic in enumerate(data):
            marked[i]["entities"] = dic["entities"]
            marked[i]["relations"] = dic["relations"]
            
        return res,marked



#Test
infile = open(sys.argv[1], encoding="utf-8")
outfile = open(sys.argv[2], "w", encoding="utf-8")
outfile_iob = open(sys.argv[2] + ".iob", "w", encoding="utf-8")

#text = infile.read()
text = json.load(infile)
infile.close()

pipeline = Pipeline()

res,marked = pipeline.process_json(text)
to_iob(res, outfile_iob)
outfile_iob.close()
json.dump(marked, outfile, indent=4)
outfile.close()

#for sent in pipeline.process(text):
#    print(sent)
#    print()
