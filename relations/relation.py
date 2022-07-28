class Relation:
    def __init__(self, entity_list, label):
        self.entity_list = entity_list
        self.label = label

    def to_dict(self):
        return {"entities": [ent.string for ent in self.entity_list], "label": self.label}
