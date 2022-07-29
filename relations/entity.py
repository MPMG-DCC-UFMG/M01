class Entity:
    def __init__(self, start, end, string, label):
        self.start = start #indice do caractere inicial da entidade no texto
        self.end = end #indice do caractere final da entidade no texto
        self.string = string #sequencia de caracteres da entidade (equivale a texto[start:end])
        self.label = label #tipo da entidade
        self.idx = None #Indice da entidade na lista de entidades (ajustado depois)

    # Funcao para deixar objetos da classe ordenaveis:
    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def to_dict(self):
        return {"entity": self.string, "start": self.start, "end": self.end, "label": self.label, "idx": self.idx}
