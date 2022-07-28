from relation import Relation

class RelationExtractor:
    def __init__(self, entities, text):

        # entities: vetor de entidades na ordem em que elas aparecem no texto
        self.entities = entities

        self.text = text

        # Mapeia o tipo de entidade da "head" da relacao p/ a funcao de extracao correspondente
        # (switch-case implementado por dicionario)

        self.extraction_functions = {
            "LICITACAO": self.licitacao_relations,
            "COMPETENCIA": self.competencia_relations,
            "CONTRATO": self.contrato_relations,
            "CPF": self.cpf_relations,
            "CNPJ": self.cnpj_relations
            # ...
        }


    # Retorna a próxima entidade do tipo ent_type depois da head_entity
    # a uma distancia maxima context_size

    def next_entity_of_type(self, head_entity, ent_type, context_size=100):
        idx = head_entity.idx
        position = head_entity.end
        upper_bound = position + context_size
        while position < upper_bound:
            idx += 1
            next_entity = self.entities[idx]
            if next_entity.label == ent_type:
                return next_entity
        return None #Nao encontrou


    # Retorna a entidade do tipo ent_type que anteceda a head_entity
    # a uma distancia maxima context_size

    def previous_entity_of_type(self, head_entity, ent_type, context_size=100):
        idx = head_entity.idx
        position = head_entity.start
        lower_bound = position - context_size
        while position > lower_bound:
            idx -= 1
            prev_entity = self.entities[idx]
            if prev_entity.label == ent_type:
                return prev_entity
        return None #Nao encontrou

    def extract_relations(self):
        relations = []
        for entity in self.entities:
            if entity.label in self.extraction_functions:
                relations += self.extraction_functions[entity.label](entity)
        return relations

    #Retorna relacoes que tem como "head" uma entidade do tipo LICITACAO
    def licitacao_relations(self, entity):
        relations = []

        # Relacao LICITACAO - PROCESSO
        prev = self.previous_entity_of_type(entity, "PROCESSO", context_size=100)
        if prev == None:
            next = self.next_entity_of_type(entity, "PROCESSO", context_size=100)
            if next != None:
                relations.append(Relation([entity, next], "licitacao-processo"))
        else:
            relations.append(Relation([entity, prev], "licitacao-processo"))

        return relations

