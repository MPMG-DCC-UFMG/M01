import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from scipy.sparse import hstack
from sklearn.preprocessing import OneHotEncoder


class FeatureEncoder:
    def __init__(self):
        self.enc = OneHotEncoder(handle_unknown='ignore')
        self.label_enc = LabelEncoder()
        self.text_enc = TfidfVectorizer(analyzer='char_wb', ngram_range=(1, 4),
                                        strip_accents='unicode', max_df=200)
        self.n_numerical_features = 11

    def fit(self, X):
        X = np.array(X)
        n = len(X[0])
        y = X[:, 0]
        self.label_enc.fit(y)
        categorical_features = X[:, 3:n-self.n_numerical_features]
        self.enc.fit(categorical_features)
        texts = X[:, n-1]
        self.text_enc.fit(texts)

    def transform(self, X):
        X = np.array(X)
        n = len(X[0])
        y = X[:, 0]
        y = self.label_enc.transform(y)
        np_num = X[:, n-self.n_numerical_features:n-1]
        X_num = csr_matrix(np_num.astype(np.float64))
        categorical_features = X[:, 3:n-self.n_numerical_features]
        X_cat = self.enc.transform(categorical_features)
        texts = X[:, n-1]
        X_text = self.text_enc.transform(texts)
        return hstack([X_cat, X_text, X_num]), y

    def feature_names(self):
        NUMS = "preceeds closest closest_by_type e1_father e2_father e1_mother e2_mother e1_parent e2_parent proximity".split()
        return np.concatenate([self.enc.get_feature_names(["e1", "e2"]), self.text_enc.get_feature_names(), NUMS])



    #Numerical features
    # row.append(1 if e1_preceds_e2 else 0)
    # row.append(1 if j == closest else 0)
    # row.append(1 if j == closest_by_type[e2.label][0] else 0)
    # row.append(1 if e1.is_pai else 0)
    # row.append(1 if e2.is_pai else 0)
    # row.append(1 if e1.is_mae else 0)
    # row.append(1 if e2.is_mae else 0)
    # row.append(1 if (e1.is_pai or e1.is_mae) else 0)
    # row.append(1 if (e2.is_pai or e2.is_mae) else 0)
    # row.append(1 / (d / 10 + 1))
