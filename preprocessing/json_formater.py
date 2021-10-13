import json

class JsonFormater:
    #tokenizer: spaCy model
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    #ents = triples (start, end, label)
    def format(self, text, ents):
        ind_char = 0
        tokens = []
        entities = []
        for start_char, end_char, label in sorted(ents):
            #Tokens before entity
            tokens += [ token.text for token in tokenizer(text[ind_char:start_char].strip()) ]
            ind = len(tokens)

            #Entity tokens
            tokens += [ token.text for token in tokenizer(text[start_char:end_char].strip()) ]
            entities.append( {"start": ind, "end": len(tokens), "type": label} )
            ind_char = end_char

        #Tokens after last entity
        tokens += [ token.text for token in tokenizer(text[ind_char:].strip()) ]
        return {"tokens":tokens, "entities": entities}




#Test

import spacy
tokenizer = spacy.load("pt_core_news_sm")

formater = JsonFormater(tokenizer)
data = formater.format(u"O Nobre Rato roeu a roupa do rei de Roma.", [(2, 12, "PER"), (36, 40, "LOC")])
                        #012345678901234567890123456789012345678901
                        #0         1         2         3         4
print(json.dumps(data, indent=4))



