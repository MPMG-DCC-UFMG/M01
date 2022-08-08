class Relation:
    def __init__(self, entity_list, label):
        self.entity_list = entity_list
        self.label = label

    # Funcao para deixar objetos da classe ordenaveis:
    def __lt__(self, other):
        return (self.entity_list[0], self.entity_list[1]) < (other.entity_list[0], other.entity_list[1])

    def to_dict(self, use_entity_indices=False):
        if use_entity_indices:
            return {"entities": [ent.idx for ent in self.entity_list], "label": self.label}
        return {"entities": [ent.string for ent in self.entity_list], "label": self.label}

    def transpose(self):
        self.entity_list.reverse()
