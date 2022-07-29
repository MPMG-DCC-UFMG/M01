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
            "CNPJ": self.cnpj_relations,
            "VALOR_MONETARIO": self.valor_relations
            # ...
        }


    # Retorna a próxima entidade de um dos tipos em "ent_types" que ocorre depois da head_entity
    # a uma distancia maxima context_size

    def next_entity_of_type(self, head_entity, ent_types, context_size=100):
        idx = head_entity.idx
        position = head_entity.end
        upper_bound = position + context_size
        while position < upper_bound:
            idx += 1
            if idx >= len(self.entities):
                break
            next_entity = self.entities[idx]
            position = next_entity.start
            if position > upper_bound:
                break
            if next_entity.label in ent_types:
                return next_entity
        return None #Nao encontrou


    # Retorna a entidade de um dos tipos em "ent_types" que anteceda a head_entity
    # a uma distancia maxima context_size

    def previous_entity_of_type(self, head_entity, ent_types, context_size=100):
        idx = head_entity.idx
        position = head_entity.start
        lower_bound = position - context_size
        while position > lower_bound:
            idx -= 1
            if idx < 0:
                break
            prev_entity = self.entities[idx]
            position = prev_entity.end
            if position < lower_bound:
                break
            if prev_entity.label in ent_types:
                return prev_entity
        return None #Nao encontrou

    def extract_relations(self):
        relations = []
        for entity in self.entities:
            if entity.label in self.extraction_functions:
                relations += self.extraction_functions[entity.label](entity)
        return relations


    # Funcao geral para retornar relacoes (list[Relation]) que têm como "head" a entidade "head_entity",
    # como "tail" uma entidade do tipo "ent_type" e como tipo "rel_type"
    # A entidade relacionada "tail" aqui peferencialmente aparece depois da "head" no texto

    def relate_to_next_entity(self, head_entity, ent_types, rel_type, context_size=100):
        relations = []
        next = self.next_entity_of_type(head_entity, ent_types, context_size=context_size)
        if next == None:
            prev = self.previous_entity_of_type(head_entity, ent_types, context_size=context_size)
            if prev != None:
                relations.append(Relation([head_entity, prev], rel_type))
        else:
            relations.append(Relation([head_entity, next], rel_type))
        return relations


    # Funcao geral para retornar relacoes (list[Relation]) que têm como "head" a entidade "head_entity",
    # como "tail" uma entidade do tipo "ent_type" e como tipo "rel_type"
    # A entidade relacionada "tail" aqui peferencialmente aparece antes da "head" no texto

    def relate_to_previous_entity(self, head_entity, ent_types, rel_type, context_size=100):
        relations = []
        prev = self.previous_entity_of_type(head_entity, ent_types, context_size=context_size)
        if prev == None:
            next = self.next_entity_of_type(head_entity, ent_types, context_size=context_size)
            if next != None:
                relations.append(Relation([head_entity, next], rel_type))
        else:
            relations.append(Relation([head_entity, prev], rel_type))
        return relations

    #Retorna relacoes (list[Relation]) que têm como "head" uma entidade do tipo LICITACAO
    def licitacao_relations(self, entity):
        return self.relate_to_next_entity(entity, ["PROCESSO"], "licitacao-processo")

    # "head": COMPETENCIA
    def competencia_relations(self, entity):
        res = self.relate_to_previous_entity(entity, ["PESSOA"], "competencia-pessoa")
        res.extend(self.relate_to_next_entity(entity, ["ORGANIZACAO"], "competencia-organizacao", context_size=30))
        return res

    def contrato_relations(self, entity):
        return self.relate_to_next_entity(entity, ["LICITACAO"], "contrato-licitacao")

    def cpf_relations(self, entity):
        return self.relate_to_previous_entity(entity, ["PESSOA"], "cpf")

    def cnpj_relations(self, entity):
        return self.relate_to_previous_entity(entity, ["ORGANIZACAO", "MUNICIPIO"], "cnpj")

    def valor_relations(self, entity):
        relations = []
        relations += self.relate_to_previous_entity(entity, ["ORGANIZACAO", "PESSOA"], "proposta-valor")
        relations += self.relate_to_previous_entity(entity, ["CONTRATO"], "contrato-valor", context_size=300)

        for r in relations:
            r.transpose()
        return relations

