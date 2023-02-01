
from relation_featurizer import RelationFeaturizer
from feature_encoder import FeatureEncoder
from entity import Entity
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import KFold
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
        relation_featurizer = RelationFeaturizer(entities, text, ents2rels, ngc, labels=labels_to_use)
        features = relation_featurizer.extract_features()
        X += features
    return np.array(X)


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
    train_filename = sys.argv[1]
    test_filename = sys.argv[2]

    with open(train_filename, encoding="utf-8") as infile:
        train_data = json.load(infile)

    with open(test_filename, encoding="utf-8") as infile:
        test_data = json.load(infile)

    train_data = [train_data] if "sentences" not in train_data else train_data["sentences"]
    test_data = [test_data] if "sentences" not in test_data else test_data["sentences"]

    features_train = segments2features(train_data)
    features_test = segments2features(test_data)
    feature_enc = FeatureEncoder()
    feature_enc.fit(features_train)
    X_train, y_train = feature_enc.transform(features_train)
    X_test, y_test = feature_enc.transform(features_test)

    sample_indices = negative_sampling(y_train, frac=1)
    X_train = X_train[sample_indices]
    y_train = y_train[sample_indices]

    #clf = MLPClassifier(hidden_layer_sizes=(1000,))
    #clf = RandomForestClassifier(n_estimators=200)
    clf = SVC(kernel='linear')
    clf.fit(X_train, y_train)
    pred = feature_enc.label_enc.inverse_transform(clf.predict(X_test))
    y_true = feature_enc.label_enc.inverse_transform(y_test)
    labels = set(list(y_true))
    labels -= set(["0"])
    labels = list(labels)

    print(classification_report(y_true, pred, labels=labels))

