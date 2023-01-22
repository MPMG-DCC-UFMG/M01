#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import json
import spacy
import sys

infilename = sys.argv[1]

#df = pd.read_csv("/kaggle/input/generator-for-relation-extraction/generated_licitacoes.csv", encoding="utf-8")
#df = pd.read_csv("/kaggle/input/generated-licitacoes/generated_licitacoes.csv", encoding="utf-8")
df = pd.read_csv(infilename, encoding="utf-8").fillna("")

nlp = spacy.load('pt_core_news_sm')

from unicodedata import normalize

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('UTF-8')

# Estrutura de arvore de prefixos, eficiente para casamento exato de todas as
# palavras de um dicionario em um dado texto

class TreeNode:
    def __init__(self, token="", is_terminal=False):
        self.children = {}
        self.token = token
        self.terminal = is_terminal

    # Find node containing token
    # Returns None if token not found
    def find(self, token):
        if token == self.token:
            return self
        elif token in self.children:
            return self.children[token]
        # else:
        # for node in self.children.values():
        #    res = node.find(token)
        #    if res != None:
        #        return res
        return None

    # Adds the sequence of tokens "seq" to the vocabulary of the tree

    def add(self, seq):
        if len(seq) == 0:
            return
        tok = seq[0]
        if tok not in self.children:
            if len(seq) == 1:
                self.children[tok] = TreeNode(tok, is_terminal=True)
            else:
                self.children[tok] = TreeNode(tok, is_terminal=False)
            # print("Created node for:", tok)
        else:
            if len(seq) == 1:
                self.children[tok].terminal = True
            # print("Matched token:", tok)
        self.children[tok].add(seq[1:])

    def print_tree(self):
        print("Token:", self.token)
        print("children:", self.children.keys())
        for node in self.children.values():
            node.print_tree()

    def find_all(self, sentence_tokens_low):
        i = 0
        matches = []
        while i < len(sentence_tokens_low):
            seq = []
            node = self.find(sentence_tokens_low[i])
            terminal = False
            while node != None:
                terminal = node.terminal
                seq.append(node.token)
                i += 1
                if i >= len(sentence_tokens_low):
                    break
                node = node.find(sentence_tokens_low[i])
            if terminal:  # match
                start = i - len(seq)
                end = i
                matches.append((start, end))
            if len(seq) == 0:
                i += 1
        return matches


VALID_ENTS = set("PESSOA ORGANIZACAO CPF CNPJ LICITACAO VALOR_MONETARIO COMPETENCIA CONTRATO DATA ENDERECO".split())
def convert(df):
    res = []
    for i, row in df.iterrows():
        rel_type = row["relation_type"]
        if rel_type == "":
            continue
        gen_text = row["generated_text"]
        first_item = gen_text.split("###")[0].strip()
        lines = first_item.split("\n")
        text = "\n".join([line for line in lines if not line.strip().startswith("[")])
        if len(text) < 10:
            continue
        tokens = [x.text for x in nlp(text)]
        tokens_low = [x.lower() for x in tokens]
        text_low = text.lower()
        ents = []
        spans = []
        rels = []
        for line in lines:
            lin = line.strip()
            if lin.startswith("["):
                spl = lin.split("]:")
                if len(spl) == 2:
                    ent_label = remover_acentos(spl[0][1:].strip())
                    if ent_label not in VALID_ENTS:
                        continue
                    ent_str = spl[1].strip()
                    spans.append((ent_label, ent_str))
        if len(spans) != 2:
            continue
        for label, span in spans:            
            matcher = TreeNode()
            seq = [tok.text for tok in nlp(span.lower())]
            matcher.add(seq)
            matches = matcher.find_all(tokens_low)
            for start, end in matches:
                ents.append({"start": start, "end": end, "type": label})
        if len(ents) == 2:
            rels.append({"head": 0, "tail": 1, "type": rel_type})
            res.append({"tokens": tokens, "entities": ents, "relations": rels})
            print(f'{ents[0]["type"]} --> {ents[1]["type"]}: {rel_type}')
    return res


if True:
    res = convert(df)
    with open(sys.argv[2], "w", encoding="utf-8") as outfile:
        json.dump(res, outfile, indent=4)

