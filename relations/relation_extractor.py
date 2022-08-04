from relation import Relation
from entity import Entity

class RelationExtractor:
    def __init__(self, entities, text):

        # entities: vetor de entidades na ordem em que elas aparecem no texto
        self.entities = entities
        self.text = text

        #Informacoes globais do segmento de texto atual
        self.licitacao = None
        self.contrato = None
        self.contratante = None
        self.contratado = None
        self.data_abertura = None
        self.vencedor = None
        self.municipio = None

        # Mapeia o tipo de entidade da "head" da relacao p/ a funcao de extracao correspondente
        # (switch-case implementado por dicionario)

        self.extraction_functions = {
            "LICITACAO": self.licitacao_relations,
            "COMPETENCIA": self.competencia_relations,
            "CONTRATO": self.contrato_relations,
            "CPF": self.cpf_relations,
            "CNPJ": self.cnpj_relations,
            "VALOR_MONETARIO": self.valor_relations,
            "PESSOA": self.pessoa_relations,
            "ORGANIZACAO": self.organizacao_relations,
            "DATA": self.data_relations,
            "MUNICIPIO": self.municipio_relations,
            "MASP": self.masp_relations
            # ...
        }

    def extract_relations(self):
        self.relations = []
        for entity in self.entities:
            if entity.label in self.extraction_functions:
                self.extraction_functions[entity.label](entity)
        self.finalize()

    # Etapa final
    def finalize(self):
        self.relate(self.contrato, self.contratado, "contrato-contratado")
        self.relate(self.contratante, self.contratado, "contratante-contratado")
        self.relate(self.licitacao, self.data_abertura, "data_abertura")
        self.relate(self.licitacao, self.vencedor, "licitacao-vencedor")
        if self.licitacao != None:
            key_entity = self.licitacao
        else:
            key_entity = Entity(0, 0, "-", "None")
        self.relate(self.municipio, key_entity, "municipio")
        if self.municipio != None:
            print("Municipio:", self.municipio.string)

    def relate(self, entity1, entity2, label):
        if entity1 != None and entity2 != None:
            self.relations.append(Relation([entity1, entity2], label))

    # Se pelo menos uma das palavras em words estiver no contexto proximo a "head_entity", retorna True

    def is_in_context(self, words, head_entity, prioritize_previous=True, context_size=20):
        window_start = max(0, head_entity.start - context_size)
        window_end = min(len(self.text), head_entity.end + context_size)
        for word in words:
            if prioritize_previous:
                if word in self.text[window_start:head_entity.start]:
                    return True
                if word in self.text[head_entity.end:window_end]:
                    return True
            else:
                if word in self.text[head_entity.end:window_end]:
                    return True
                if word in self.text[window_start:head_entity.start]:
                    return True
        return False


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



    # Funcao geral para retornar relacoes (list[Relation]) que têm como "head" a entidade "head_entity",
    # como "tail" uma entidade do tipo "ent_type" e como tipo "rel_type"
    # A entidade relacionada "tail" aqui preferencialmente aparece depois da "head" no texto

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
    # A entidade relacionada "tail" aqui preferencialmente aparece antes da "head" no texto

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
        self.relations += self.relate_to_next_entity(entity, ["PROCESSO"], "licitacao-processo")

    # "head": COMPETENCIA
    def competencia_relations(self, entity):
        self.relations += self.relate_to_previous_entity(entity, ["PESSOA"], "competencia-pessoa", context_size=30)
        self.relations += self.relate_to_next_entity(entity, ["ORGANIZACAO"], "competencia-organizacao", context_size=30)

    def contrato_relations(self, entity):
        self.contrato = entity
        self.relations += self.relate_to_next_entity(entity, ["LICITACAO"], "contrato-licitacao")

    def cpf_relations(self, entity):
        self.relations += self.relate_to_previous_entity(entity, ["PESSOA"], "cpf", context_size=30)

    def masp_relations(self, entity):
        self.relations += self.relate_to_previous_entity(entity, ["PESSOA"], "masp", context_size=30)

    def cnpj_relations(self, entity):
        self.relations += self.relate_to_previous_entity(entity, ["ORGANIZACAO", "MUNICIPIO"], "cnpj", context_size=30)

    def valor_relations(self, entity):
        relations = []
        relations += self.relate_to_previous_entity(entity, ["ORGANIZACAO", "PESSOA"], "proposta-valor", context_size=300)
        relations += self.relate_to_previous_entity(entity, ["CONTRATO"], "contrato-valor", context_size=500)

        for r in relations:
            r.transpose()
        self.relations += relations

    def pessoa_relations(self, entity):
        if self.is_in_context(["contratant"], entity, prioritize_previous=True):
            self.contratante = entity
        elif self.is_in_context(["contratad"], entity, prioritize_previous=True):
            self.contratado = entity

        if self.is_in_context(["vence"], entity, prioritize_previous=True, context_size=20):
            self.vencedor = entity

    def organizacao_relations(self, entity):
        if self.is_in_context(["contratant"], entity, prioritize_previous=True):
            self.contratante = entity
        elif self.is_in_context(["contratad"], entity, prioritize_previous=True):
            self.contratado = entity

        if self.is_in_context(["vence"], entity, prioritize_previous=True, context_size=20):
            self.vencedor = entity


    def data_relations(self, entity):
        if self.is_in_context(["abert", "receb", "início", "partir", "inicia"], entity, prioritize_previous=True, context_size=40):
            self.data_abertura = entity

    def municipio_relations(self, entity):
        if self.municipio == None: #Utilizar a primeira ocorrencia de MUNICIPIO
            self.municipio = entity
