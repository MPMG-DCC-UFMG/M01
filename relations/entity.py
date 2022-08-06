from collections import defaultdict


class Entity:
    def __init__(self, start, end, string, label):
        self.start = start #indice do caractere inicial da entidade no texto
        self.end = end #indice do caractere final da entidade no texto
        self.string = string #sequencia de caracteres da entidade (equivale a texto[start:end])
        self.label = label #tipo da entidade
        self.idx = None #Indice da entidade na lista de entidades (ajustado depois)
        self.lower_string = self.string.lower()

        # mapeia o nome da relacao p/ a lista de entidades relacionadas
        # A lista será ordenada de acordo com a proximidade entre esta entidade e a entidade candidata
        self.relation_candidates = defaultdict(list)

        # Variaveis para auxiliar nas regras para relacionar entidades:
        self.has_competencia = False

    # Funcao para deixar objetos da classe ordenaveis:
    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def to_dict(self):
        return {"entity": self.string, "start": self.start, "end": self.end, "label": self.label, "idx": self.idx}

    def is_public_org(self):
        words = ["públic", "public", "municip", "municíp", "estadual", "federal", "secretaria", "fundação", "conselho", "diretoria"]
        for word in words:
            if word in self.lower_string:
                return True
        return False

    def add_candidate(self, cand, dist, rel_type):
        self.relation_candidates[rel_type].append((dist, cand))
