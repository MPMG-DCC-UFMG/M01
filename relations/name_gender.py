from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.model_selection import cross_validate
import joblib
import pandas as pd

class NameGenderClassifier:
    def __init__(self, lookup=None):
        self.lookup = lookup
        self.onehot = OneHotEncoder(handle_unknown='ignore')
        self.classifier = BernoulliNB() #SVC(kernel='linear')

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
                #print("usou lookup")
                return self.lookup[name]
        #print("usou classificador")
        return self.classifier.predict(self.onehot.transform([self.featurize(name)]))[0]

    def cross_validate(self, data):
        X = [self.featurize(x) for x, y in data]
        X = self.onehot.fit_transform(X)
        y = [d[1] for d in data]
        return cross_validate(self.classifier, X, y, scoring="accuracy")


if __name__ == "__main__":
    #ngc = joblib.load("data/name_gender_old.joblib")
    ngc = NameGenderClassifier()
    data = pd.read_csv("data/name_gender.csv", encoding="utf-8").dropna().values
    ngc.fit(data)
    for nome in "Mariana Mariane Marcela Capitu Dorotenilde Valdirene Adriele Adriel Bento Bentinho Tales Fabiano Doruvey Valdir".split():
        print(nome, "M" if ngc.predict(nome) == 1 else "F")
    joblib.dump(ngc, "data/name_gender.joblib")
