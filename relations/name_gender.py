from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.model_selection import cross_validate
import pickle

class NameGenderClassifier:
    def __init__(self, lookup=None):
        self.lookup = lookup
        self.onehot = OneHotEncoder(handle_unknown='ignore')
        self.classifier = SVC(kernel='linear')

    def featurize(self, name):
        return [name[-1], name[-3:], name[:3]]

    def fit(self, data):
        X = [self.featurize(x) for x, y in data]
        X = self.onehot.fit_transform(X)
        y = [d[1] for d in data]
        self.classifier.fit(X, y)

    def predict(self, name):
        name = name.upper()
        if self.lookup is not None:
            if name in self.lookup:
                return self.lookup[name]
        return self.classifier.predict(self.onehot.transform([self.featurize(name)]))[0]

    def cross_validate(self, data):
        X = [self.featurize(x) for x, y in data]
        X = self.onehot.fit_transform(X)
        y = [d[1] for d in data]
        return cross_validate(self.classifier, X, y, scoring="accuracy")


with open("data/name_gender.pkl", "rb") as infile:
    ngc = pickle.load(infile)

for nome in "Mariana Mariane Marcela Capitu Dorotenilde Adriele Adriel Bento Bentinho Tales Rafael Doruvey".split():
    print(nome, ngc.predict(nome))

