from relation_featurizer import RelationFeaturizer
from feature_encoder import FeatureEncoder
import numpy as np
from sklearn.svm import SVC
from name_gender import NameGenderClassifier
from entity import Entity
import json
import sys
import joblib
from train import segments2features
import time

ngc = joblib.load("data/name_gender.joblib")

#Adiciona relacoes ao orig_json (alteracoes in-place)
def predictions2json(predictions, probabilities, features, index, segments, use_indices=True):
    seg2ents = {i: {} for i in range(len(segments))}
    for pred, prob, feats, seg_idx in zip(predictions, probabilities, features, index):
        if pred == "0": #no-relation
            continue
        e1 = int(feats[1])
        e2 = int(feats[2])
        seg_entities = seg2ents[seg_idx]
        ents = segments[seg_idx]["entities"]
        ent1 = ents[e1]
        ent2 = ents[e2]
        ent1_obj = Entity(ent1["start"], ent1["end"], ent1["entity"], ent1["label"], idx=e1)
        ent2_obj = Entity(ent2["start"], ent2["end"], ent2["entity"], ent2["label"], idx=e2)
        ent1_obj.add_candidate(ent2_obj, 1 - prob, pred)

        if e1 not in seg_entities:
            seg_entities[e1] = ent1_obj

    for seg_idx, seg_entities in seg2ents.items():
        for ent_idx, ent_obj in seg_entities.items():
            for rel_type, candidates in ent_obj.relation_candidates.items():
                score, top_ent = sorted(candidates)[0]
                if use_indices:
                    ent_pair = [ent_obj.idx, top_ent.idx]
                else:
                    ent_pair = [ent_obj.string, top_ent.string]
                segments[seg_idx]["relations"].append({"entities": ent_pair, "label": rel_type})


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} <dados para inferência (.json com entidades)> [modelo de extração de relações]')
        exit(1)

    model_name = "models/relations.joblib"
    train_filename = sys.argv[1]
    if len(sys.argv) > 2:
        model_name = sys.argv[2]

    with open(train_filename, encoding="utf-8") as infile:
        test_data = json.load(infile)

    test_segments = [test_data] if "sentences" not in test_data else test_data["sentences"]
    for segment in test_segments:
        if "relations" in segment:
            segment["relations"] = [] #Limpa relacoes, caso existam

    features_test, index = segments2features(test_segments)
    start_time = time.time()
    clf, feature_enc = joblib.load(model_name)
    #print("Load model time:", time.time() - start_time)
    X_test, y_test = feature_enc.transform(features_test)
    probs = clf.predict_proba(X_test)
    pred = np.argmax(probs, axis=1)
    prob_max = np.max(probs, axis=1)
    pred = feature_enc.label_enc.inverse_transform(pred)
    predictions2json(pred, prob_max, features_test, index, test_segments)

    print(json.dumps(test_data, indent=4))
