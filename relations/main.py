import sys
import json
##from nltk.metrics.distance import edit_distance
#from preprocessing.casing import title_case
#from preprocessing.text_cleaner import extract_digits, tokenize
from inout import read_lower_cased_strings
from prefix_tree import *
from entity import Entity
#from relation_extractor import RelationExtractor
from relation_extractor_pairs import RelationExtractor
from municipio_matcher import MunicipioMatcher

from collections import Counter

import re

#DATE_PATTERN = re.compile("(\d\d?\s?/\s?\d\d?/\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\-\s?\d\d?\-\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\.\s?\d\d?\.\s?\d\s?\.?\s?\d(\d\d)?)")
#WSIZE = 100
#MODALIDADES = ["convite", "tomada de preços", "concorrência", "concurso", "pregão presencial", "pregão eletrônico", "leilão"]
#TIPOS = ["melhor técnica", "menor preço", "maior lance ou oferta", "técnica e preço"]
#INF = 999999999


#TREE_MODALIDADES.print_tree()
#TREE_TIPOS.print_tree()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file (.json produced by NER)> <outfile (.json with relations included)>" % sys.argv[0])
        sys.exit(-1)

    use_indices = False
    verbose = False
    for arg in sys.argv[1:]:
        if "--use-indices" == arg:
            use_indices = True
        if "--verbose" == arg:
            verbose = True
    filename = sys.argv[1]
    outname = sys.argv[2]
    infile = open(filename, encoding="utf-8")
    outfile = open(outname, "w", encoding="utf-8")
    data = json.load(infile)
    infile.close()

    mun_matcher = MunicipioMatcher()

    # Trata os dois formatos - texto segmentado ou nao
    if "sentences" in data:
        segments = data["sentences"]
    else:
        segments = [data]

    for segment in segments:

        text = segment["text"]
        municipio_ents = mun_matcher.match(text) #Adiciona municipios identificados

        # entities: vetor de entidades na ordem em que elas aparecem no texto
        entities = municipio_ents + [Entity(ent["start"], ent["end"], ent["entity"], ent["label"]) for ent in segment["entities"]]
        entities = sorted(entities)

        for i, ent in enumerate(entities):
            entities[i].idx = i

        relation_extractor = RelationExtractor(entities, text)
        relation_extractor.extract_relations()
        rels = [rel.to_dict(use_entity_indices=use_indices) for rel in relation_extractor.relations]
        ents = [ent.to_dict() for ent in entities]
        segment["relations"] = rels
        segment["entities"] = ents

        if verbose:
            for rel in rels:
                print(rel)

    json.dump(data, outfile, indent=4)
    outfile.close()



