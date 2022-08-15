from prefix_tree import ExactDictionaryMatcher
from inout import read_lower_cased_strings
from entity import Entity
import re

from unicodedata import normalize

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

# Tokenizador simples (nao mantem pontuacao)
def tokenize(string, hifen=False):
    puncts = ".,:;!?/()"
    for punct in puncts:
        string = string.replace(punct, " ")
    return string.split()


class MunicipioMatcher:
    def __init__(self):
        municipios = read_lower_cased_strings("data/municipios.txt")
        self.matcher = ExactDictionaryMatcher(municipios)

    def match(self, text, context_size=20):
        text_lower = remover_acentos(text.lower())
        tokens = tokenize(text_lower)
        matches = self.matcher.exact_matches(tokens)
        res = []
        context_municipios = set() #Conjunto de nomes que, neste contexto, sao municipios

        for start, end, name in matches:
            char_level_matches = re.finditer(name, text_lower)
            for m in char_level_matches:
                #print("Match:", name)
                start_char, end_char = m.span()
                window_start = max(0, start_char - context_size)
                context = text_lower[window_start:start_char]
                if "municip" in context or "prefeit" in context or "municíp" in context:
                    context_municipios.add(name)
                res.append( (name, Entity(start_char, end_char, name.upper(), "MUNICIPIO")) )
        return [ent for (name, ent) in res if name in context_municipios]
