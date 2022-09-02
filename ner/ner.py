from regex_ner import RegexNER
import nltk
from nltk.tag.stanford import StanfordNERTagger
from datetime import datetime


class NER:
    def __init__(self, model_filename, regex_filename):
        self.model = StanfordNERTagger(model_filename=model_filename,
                                       path_to_jar="./stanford-ner.jar",
                                       encoding='utf-8')
        self.ner_regex = RegexNER(regex_filename)

        self.PUNCT = ".,;?!:"

    def ner(self, text, source_file=None, dest_file=None):
        tokens = nltk.word_tokenize(text)
        tagged = self.model.tag(tokens)
        spans = self.merge_bio_tags(tagged)
        ents, new_text = self.to_char_level_format(tokens, spans)
        regex_ents = self.ner_regex.ner(new_text)
        ents = sorted(ents + regex_ents)
        jdata = self.json_format(new_text, ents, source_file=source_file, dest_file=dest_file)
        return jdata


    #Funções auxiliares

    def merge_bio_tags(self, tagged):
        res = []
        i = 0
        while i < len(tagged):
            token, lab = tagged[i]
            if lab[0] == "B":
                current = lab[2:]
                start = i
                end = i
            else:
                current = lab
            i += 1
            if i >= len(tagged):
                break
            while tagged[i][1][0] == "I":
                end = i
                i += 1
                if i >= len(tagged):
                    break
            if current != "O":
                res.append( (start, end, current) )
        return res


    def to_char_level_format(self, tokens, ents, source_file=None, dest_file=None):
        idx_token2char = {}
        char_idx = 0
        tokens_and_spaces = []
        if len(tokens) > 0:
            tokens_and_spaces.append(tokens[0])
            idx_token2char[0] = char_idx
            char_idx += len(tokens[0])
        for i in range(1, len(tokens)):
            token = tokens[i]
            if token in self.PUNCT:
                tokens_and_spaces.append(token)
            else:
                tokens_and_spaces.append(" ")
                tokens_and_spaces.append(token)
                char_idx += 1
            idx_token2char[i] = char_idx
            char_idx += len(token)
        text = "".join(tokens_and_spaces)
        new_entities = []

        for start, end, label in ents:
            start_char = idx_token2char[start]
            end_char = idx_token2char[end] + len(tokens[end])
            new_entities.append((start_char, end_char, label))
        return new_entities, text

    def json_format(self, text, ents, source_file=None, dest_file=None):
        res = {"text": text}
        entities = []
        for start, end, label in ents:
            entities.append({"entity": text[start:end], "start": start, "end": end, "label": label})
        res["entities"] = entities
        if source_file is not None:
            res["src_file"] = source_file
        if dest_file is not None:
            res["file"] = dest_file
        res["timestamp"] = str(datetime.now())
        return res
