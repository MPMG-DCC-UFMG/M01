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
from name_gender import NameGenderClassifier
import joblib
from collections import Counter
import re

#DATE_PATTERN = re.compile("(\d\d?\s?/\s?\d\d?/\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\-\s?\d\d?\-\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\.\s?\d\d?\.\s?\d\s?\.?\s?\d(\d\d)?)")
#WSIZE = 100
#MODALIDADES = ["convite", "tomada de preços", "concorrência", "concurso", "pregão presencial", "pregão eletrônico", "leilão"]
#TIPOS = ["melhor técnica", "menor preço", "maior lance ou oferta", "técnica e preço"]
#INF = 999999999


#TREE_MODALIDADES.print_tree()
#TREE_TIPOS.print_tree()



def extract_relations(data, use_indices=True, verbose=False):
    global ngc
    mun_matcher = MunicipioMatcher()
    # Trata os dois formatos - texto segmentado ou nao
    if "sentences" in data:
        segments = data["sentences"]
    else:
        segments = [data]

    for segment in segments:
        text = segment["text"]
        municipio_ents = mun_matcher.match(text)  # Adiciona municipios identificados
        #if len(municipio_ents) > 0:
        #    print("len(municipios):", len(municipio_ents))

        # entities: vetor de entidades na ordem em que elas aparecem no texto

        entities = municipio_ents + [Entity(ent["start"], ent["end"], ent["entity"], ent["label"]) for ent in
                                     segment["entities"]]
        #entities = [Entity(ent["start"], ent["end"], ent["entity"], ent["label"]) for ent in segment["entities"]]
        entities = sorted(entities)

        for i, ent in enumerate(entities):
            entities[i].idx = i

        relation_extractor = RelationExtractor(entities, text, ngc)
        relation_extractor.extract_relations()
        rels = [rel.to_dict(use_entity_indices=use_indices) for rel in sorted(relation_extractor.relations)]
        ents = [ent.to_dict() for ent in entities]
        segment["relations"] = rels
        segment["entities"] = ents

        if verbose:
            for rel in rels:
                print(rel)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file (.json produced by NER)> [outfile (.json with relations included)]" % sys.argv[0])
        sys.exit(-1)

    ngc = joblib.load("data/name_gender.joblib")
    use_indices = False
    verbose = False
    num_file_args = len(sys.argv)
    for arg in sys.argv[1:]:
        if "--use-indices" == arg:
            use_indices = True
            num_file_args -= 1
        if "--verbose" == arg:
            verbose = True
            num_file_args -= 1

    filename = sys.argv[1]
    if num_file_args < 3:
        outfile = sys.stdout
    else:
        outname = sys.argv[2]
        outfile = open(outname, "w", encoding="utf-8")
    infile = open(filename, encoding="utf-8")
    data = json.load(infile)
    infile.close()
    #data é modificado, acrescentando-se as relações
    extract_relations(data, use_indices=use_indices, verbose=verbose)
    json.dump(data, outfile, indent=4)
    outfile.close()



