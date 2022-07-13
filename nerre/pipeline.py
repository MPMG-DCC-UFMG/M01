
import sys
import json
from preprocessing.text_cleaner import tokenize_sentences, clear_special_chars, replacements, tokens2sentence
from preprocessing.json_formater import JsonFormater, to_iob
from regex_ner import RegexNER
import spacy

class Pipeline:

    def __init__(self):
        #self.replace_list = [ ["-\n", ""], [" / ", "/"], ["Av.", "Av"], ["\u00ba.", "\u00ba"], ["\u00aa.", "\u00aa"] ]
        self.replace_list = [ ["-\n", ""], [" / ", "/"] ]
        self.tokenizer = spacy.load("pt_core_news_sm")
        self.regex_ner = RegexNER("rules_do.tsv")
        self.json_formater = JsonFormater(self.tokenizer)


    def process(self, text, max_sentence_len=1500):
        text = replacements(clear_special_chars(text), self.replace_list)
        sents = tokenize_sentences(text)
        print("#Number of sentences:", len(sents))
        res = []
        print("Regex-based preprocessing...")

        for sent in sents:
            n = len(sent)
            for i in range(0, n, max_sentence_len):
                subsent = sent[i: i+max_sentence_len]
                ents = self.regex_ner.ner(subsent)
                #print(ents)
                res.append(self.json_formater.format(subsent, ents))

        marked = res.copy()
        marked = self.json_formater.mark_ents(marked)
        return res, marked

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
            if "entities" in dic:
                marked[i]["entities"] = dic["entities"]
            if "relations" in dic:
                marked[i]["relations"] = dic["relations"]
            
        return res,marked




if __name__ == '__main__':

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


