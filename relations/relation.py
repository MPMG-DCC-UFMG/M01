class Relation:
    def __init__(self, entity_list, label):
        self.entity_list = entity_list
        self.label = label

    def to_dict(self, use_entity_indices=False):
        if use_entity_indices:
            return {"entities": [ent.idx for ent in self.entity_list], "label": self.label}
        return {"entities": [ent.string for ent in self.entity_list], "label": self.label}

    def transpose(self):
        self.entity_list.reverse()
