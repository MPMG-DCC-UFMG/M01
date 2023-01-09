import json
import sys

from relation import Relation
from entity import Entity
from collections import defaultdict
import re
import numpy as np

class RelationFeaturizer:
    def __init__(self, entities, text, ents2rels):

        # entities: vetor de entidades na ordem em que elas aparecem no texto
        self.entities = entities
        self.text = text
        self.lower_cased_text = self.text.lower()
        self.ents2rels = ents2rels


    def overlap(self, e1, e2):
        return self.dist(e1, e2) < 0

    def extract_features(self):
        closest_ent = {}
        closest_ent_of_type = {}
        for i, e1 in enumerate(self.entities):
            closest_ent[i] = 0
            closest_ent_of_type[i] = {}
            dist_min = np.inf
            for j, e2 in enumerate(self.entities):
                d = self.dist(e1, e2)
                if d > 0: #non overlapping
                    if d < dist_min:
                        dist_min = d
                        closest_ent[i] = j
                    if e2.label not in closest_ent_of_type:
                        closest_ent_of_type[i][e2.label] = (j, d)
                    else:
                        ent, d_current = closest_ent_of_type[i][e2.label]
                        if d < d_current:
                            closest_ent_of_type[i][e2.label] = (j, d)
        X = []
        for i, e1 in enumerate(self.entities):
            closest = closest_ent[i]
            closest_by_type = closest_ent_of_type[i]
            for j, e2 in enumerate(self.entities):
                d = self.dist(e1, e2)
                if d > 0: #non overlapping
                    rel_ident = (e1.start, e1.end, e2.start, e2.end)
                    y = self.ents2rels[rel_ident] if rel_ident in self.ents2rels else "0"
                    row = [y]
                    d = self.dist(e1, e2)
                    row.append(e1.label)
                    row.append(e2.label)
                    e1_preceds_e2 = (e1.start < e2.start)
                    cstart = e2.end
                    cend = e1.start
                    if e1_preceds_e2:
                        cstart = e1.end
                        cend = e2.start
                    context = self.lower_cased_text[cstart:cend]

                    #Non-categorical and textual features:

                    row.append(1 if e1_preceds_e2 else 0)
                    row.append(1 if j == closest else 0)
                    row.append(1 if j == closest_by_type[e2.label][0] else 0)
                    row.append(1 / (d / 10 + 1))
                    row.append(context)
                    X.append(row)
        return X

    # Numero de caracteres entre e1 e e2
    def dist(self, e1, e2):
        if e1.start < e2.start:
            a = e1
            b = e2
        else:
            a = e2
            b = e1
        return b.start - a.end

    # Score utilizado para priorizar entidades mais proximas e que ocorram antes (prioritize_e1_before_e2=True)
    # ou depois de uma dada entidade (prioritize_e1_before_e2=False)
    def proximity_score(self, e1, e2, context_size=30, prioritize_e1_before_e2=True):
        d = self.dist(e1, e2)
        if d > context_size:
            return None

        # Penalizar proximidade caso e1 ocorra depois de e2
        # Isto é, vai ser preferível pegar uma entidade mais distante, mas que apareça antes
        if (e1.start > e2.start) != (prioritize_e1_before_e2): #xor
            d += context_size
        return d

    # Se pelo menos uma das palavras em "words" estiver no contexto proximo a "head_entity", retorna True
    def is_in_context(self, words, head_entity, left_context_size=20, right_context_size=20):
        window_start = max(0, head_entity.start - left_context_size)
        window_end = min(len(self.lower_cased_text), head_entity.end + right_context_size)
        for word in words:
            if word in self.lower_cased_text[window_start:head_entity.start]:
                return True
            if word in self.lower_cased_text[head_entity.end:window_end]:
                return True
        return False

    def pattern_is_in_context(self, pattern, head_entity, left_context_size=20, right_context_size=20):
        window_start = max(0, head_entity.start - left_context_size)
        window_end = min(len(self.lower_cased_text), head_entity.end + right_context_size)
        if pattern.search(self.lower_cased_text[window_start:head_entity.start]):
            return True
        if pattern.search(self.lower_cased_text[head_entity.end:window_end]):
            return True
        return False


if __name__ == "__main__":
    filename = sys.argv[1]
    infile = open(filename, encoding="utf-8")
    data = json.load(infile)
    infile.close()

    # Trata os dois formatos - texto segmentado ou nao
    if "sentences" in data:
        segments = data["sentences"]
    else:
        segments = [data]

    X = []
    for segment in segments:
        text = segment["text"]
        entities = [Entity(ent["start"], ent["end"], ent["entity"], ent["label"]) for ent in segment["entities"]]
        for i, ent in enumerate(entities):
            entities[i].idx = i
        ents2rels = {}
        for rel in segment["relations"]:
            rel_ents = rel["entities"]
            label = rel["label"]
            e1 = entities[rel_ents[0]]
            e2 = entities[rel_ents[1]]
            tupl = (e1.start, e1.end, e2.start, e2.end)
            ents2rels[tupl] = label

        relation_featurizer = RelationFeaturizer(entities, text, ents2rels)
        features = relation_featurizer.extract_features()
        X += features
    relation_featurizer.fit(X)
    M, y = relation_featurizer.transform(X)
    print("M.shape:", M.shape)
    print("len(y):", len(y))
    print("y:", y)
    print(relation_featurizer.label_enc.classes_)
    print(M[[1, 2, 3]])

