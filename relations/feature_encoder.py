import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from scipy.sparse import hstack
from sklearn.preprocessing import OneHotEncoder


class FeatureEncoder:
    def __init__(self):
        self.enc = OneHotEncoder()
        self.label_enc = LabelEncoder()
        self.text_enc = TfidfVectorizer(analyzer='char_wb', ngram_range=(1, 4),
                                        strip_accents='unicode', max_df=200)

    def fit(self, X):
        X = np.array(X)
        n = len(X[0])
        y = X[:, 0]
        self.label_enc.fit(y)
        categorical_features = X[:, 1:n-5]
        self.enc.fit(categorical_features)
        texts = X[:, n-1]
        self.text_enc.fit(texts)

    def transform(self, X):
        X = np.array(X)
        n = len(X[0])
        y = X[:, 0]
        y = self.label_enc.transform(y)
        np_num = X[:, n-5:n-1]
        X_num = csr_matrix(np_num.astype(np.float64))
        categorical_features = X[:, 1:n-5]
        X_cat = self.enc.transform(categorical_features)
        texts = X[:, n-1]
        X_text = self.text_enc.transform(texts)
        return hstack([X_cat, X_text, X_num]), y

