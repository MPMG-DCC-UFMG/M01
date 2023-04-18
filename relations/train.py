
from relation_featurizer import RelationFeaturizer
from feature_encoder import FeatureEncoder
from entity import Entity
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import json
import sys
import joblib
from name_gender import NameGenderClassifier


ngc = joblib.load("data/name_gender.joblib")

#labels_to_use = set("cpf pessoa-pai pessoa-mae data_nascimento".split())
#labels_to_use = set("cpf cnpj licitacao-processo valor-proposta competencia-organizacao competencia-pessoa".split())
labels_to_use = None

def segments2features(segments):
    X = []
    index = []
    for seg_idx, segment in enumerate(segments):
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
        relation_featurizer = RelationFeaturizer(entities, text, ents2rels, ngc, labels=labels_to_use)
        features = relation_featurizer.extract_features()
        for j in range(len(features)):
            index.append(seg_idx)
        X += features
    return np.array(X), index


def negative_sampling(y, frac=0.1, negative_label=0):
    every = int(1/frac)
    indices = []
    count = 0
    for i, label in enumerate(y):
        if label == negative_label:
            count += 1
            if count == every:
                indices.append(i)
                count = 0
        else:
            indices.append(i)
    return indices


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} <dados de treino (.json)> [saída (modelo treinado]>')
        exit(1)

    train_filename = sys.argv[1]
    outname = "models/relations.joblib"
    if len(sys.argv) > 2:
        outname = sys.argv[2]

    with open(train_filename, encoding="utf-8") as infile:
        train_data = json.load(infile)

    train_data = [train_data] if "sentences" not in train_data else train_data["sentences"]
    features_train, index_train = segments2features(train_data)
    index_train = None #nao usado aqui
    feature_enc = FeatureEncoder()
    feature_enc.fit(features_train)
    X_train, y_train = feature_enc.transform(features_train)
    #sample_indices = negative_sampling(y_train, frac=1)
    #X_train = X_train[sample_indices]
    #y_train = y_train[sample_indices]

    clf = SVC(kernel='linear', probability=True)
    clf.fit(X_train, y_train)

    joblib.dump((clf, feature_enc), outname)

