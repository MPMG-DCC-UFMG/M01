from relation import Relation
from entity import Entity
from collections import defaultdict
import re

p_pai = re.compile("(nome do)?\s+pai[:\s]+", flags=re.IGNORECASE)
p_mae = re.compile("(nome da)?\s+m[ãa]e[:\s]+", flags=re.IGNORECASE)

class RelationExtractor:
    def __init__(self, entities, text):

        # entities: vetor de entidades na ordem em que elas aparecem no texto
        self.entities = entities
        self.text = text
        self.lower_cased_text = self.text.lower()

        #Informacoes globais do segmento de texto atual
        self.licitacao = None
        self.data_abertura = None
        self.municipio = None

        # Mapeia o par de tipos de entidade p/ a funcao de extracao correspondente
        # (switch-case implementado por dicionario)

        self.extraction_functions_1st_step = {
            ("LICITACAO", "PROCESSO"): self.licitacao_processo,
            ("COMPETENCIA", "PESSOA"): self.competencia_pessoa,
            ("COMPETENCIA", "ORGANIZACAO"): self.competencia_organizacao,
            ("CONTRATO", "LICITACAO"): self.contrato_licitacao,
            ("CPF", "PESSOA"): self.cpf,
            ("MASP", "PESSOA"): self.masp,
            ("CNPJ", "ORGANIZACAO"): self.cnpj,
            ("CNPJ", "MUNICIPIO"): self.cnpj,
            ("LICITACAO", "DATA"): self.licitacao_data,
            ("LICITACAO", "MUNICIPIO"): self.licitacao_municipio,
            ("ORGANIZACAO", "ENDERECO"): self.organizacao_endereco,
            ("PESSOA", "ENDERECO"): self.pessoa_endereco,
            ("PESSOA", "PESSOA"): self.pessoa_pessoa,
            ("PESSOA", "DATA"): self.pessoa_data
            # ...
        }

        self.extraction_functions_2nd_step = {
            ("VALOR_MONETARIO", "PESSOA", ): self.valor_pessoa,
            ("VALOR_MONETARIO", "ORGANIZACAO"): self.valor_organizacao,
            ("ORGANIZACAO", "ORGANIZACAO"): self.contratante_contratado,
            ("ORGANIZACAO", "PESSOA"): self.contratante_contratado,
            ("PESSOA", "PESSOA"): self.contratante_contratado
            # ...
        }

    def group_entities_by_type(self):
        self.type2entities = defaultdict(list)
        for ent in self.entities:
            self.type2entities[ent.label].append(ent)

    def extract_relations(self):
        self.group_entities_by_type()

        #1st step) Relacoes que nao dependem da identificacao de outras relacoes
        #2nd step) Relacoes que dependem da identificacao previa de outras relacoes

        for step_functions in (self.extraction_functions_1st_step, self.extraction_functions_2nd_step):
            for (type1, type2), relation_function in step_functions.items():
                for e1 in self.type2entities[type1]:
                    for e2 in self.type2entities[type2]:
                        if e1.idx != e2.idx:
                            relation_function(e1, e2)

        self.relations = []
        for ent in self.entities:
            for rel_type, candidates in ent.relation_candidates.items():
                for score, cand in sorted(candidates)[:1]:
                    self.relations.append(Relation([ent, cand], rel_type))

    # Numero de caracteres entre e1 e e2
    def dist(self, e1, e2):
        if e1.start < e2.start:
            a = e1
            b = e2
        else:
            a = e2
            b = e1
        return b.start - a.end

    # Score utilizado para priorizar entidades mais proximas e que ocorram antes (prioritize_e1_before_e2=True)
    # ou depois de uma dada entidade (prioritize_e1_before_e2=False)
    def proximity_score(self, e1, e2, context_size=30, prioritize_e1_before_e2=True):
        d = self.dist(e1, e2)
        if d > context_size:
            return None

        # Penalizar proximidade caso e1 ocorra depois de e2
        # Isto é, vai ser preferível pegar uma entidade mais distante, mas que apareça antes
        if (e1.start > e2.start) != (prioritize_e1_before_e2): #xor
            d += context_size
        return d

    # Se pelo menos uma das palavras em "words" estiver no contexto proximo a "head_entity", retorna True
    def is_in_context(self, words, head_entity, left_context_size=20, right_context_size=20):
        window_start = max(0, head_entity.start - left_context_size)
        window_end = min(len(self.lower_cased_text), head_entity.end + right_context_size)
        for word in words:
            if word in self.lower_cased_text[window_start:head_entity.start]:
                return True
            if word in self.lower_cased_text[head_entity.end:window_end]:
                return True
        return False

    def pattern_is_in_context(self, pattern, head_entity, left_context_size=20, right_context_size=20):
        window_start = max(0, head_entity.start - left_context_size)
        window_end = min(len(self.lower_cased_text), head_entity.end + right_context_size)
        if pattern.search(self.lower_cased_text[window_start:head_entity.start]):
            return True
        if pattern.search(self.lower_cased_text[head_entity.end:window_end]):
            return True
        return False


    def licitacao_processo(self, e1, e2, context_size=30):
        d = self.dist(e1, e2)
        if d < context_size:
            e1.add_candidate(e2, d, "licitacao-processo")
        if self.licitacao is None:
            self.licitacao = e1


    def competencia_pessoa(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=False)
        if d is not None:
            e1.add_candidate(e2, d, "competencia-pessoa")
            e2.has_competencia = True
            for ent in self.type2entities["PESSOA"]:
                if ent.lower_string == e2.lower_string:
                    ent.has_competencia = True

    def competencia_organizacao(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "competencia-organizacao")

    def contrato_licitacao(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=100, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "contrato-licitacao")

    def cpf(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=False)
        if d is not None:
            e1.add_candidate(e2, d, "cpf")

    def masp(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "masp")

    def cnpj(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=False)
        if d is not None:
            e1.add_candidate(e2, d, "cnpj")

    def licitacao_data(self, e1, e2):
        if self.is_in_context(["abert", "receb", "início", "partir", "inicia"], e2, left_context_size=40, right_context_size=0):
            self.data_abertura = e2
            d = self.proximity_score(e1, e2, context_size=400, prioritize_e1_before_e2=True)
            if d is not None:
                e1.add_candidate(e2, d, "data_abertura")

    def licitacao_municipio(self, e1, e2):
        if self.municipio == None: #Utilizar a primeira ocorrencia de MUNICIPIO
            self.municipio = e2
            d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=False)
            if d is not None:
                e1.add_candidate(e2, d, "licitacao-municipio")


    def valor_pessoa(self, e1, e2):
        if e2.has_competencia:  #Considerar que cargos publicos nao disputam uma licitacao
            return
        if e1.start < e2.end:
            return
        d = self.proximity_score(e1, e2, context_size=400, prioritize_e1_before_e2=False)
        if d is not None:
            e1.add_candidate(e2, d, "valor-proposta")

    def valor_organizacao(self, e1, e2):
        if e2.is_public_org():   #Considerar que orgaos publicos nao disputam uma licitacao
            return
        if e1.start < e2.end:
            return
        d = self.proximity_score(e1, e2, context_size=400, prioritize_e1_before_e2=False)
        if d is not None:
            e1.add_candidate(e2, d, "valor-proposta")


    def organizacao_endereco(self, e1, e2):
        d = self.proximity_score(e1, e2, context_size=30, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "localizado_em")

    def contratante_contratado(self, e1, e2):
        if not self.is_in_context(["partes", "firmad", "contratant", "celebrad", "estabelecid"],
                              e1, left_context_size=40, right_context_size=0):
            return
        if e1.start > e2.end:
            return
        d = self.proximity_score(e1, e2, context_size=100, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "contratante-contratado")

    def pessoa_pessoa(self, e1, e2):
        global p_pai
        global p_mae

        if e1.start > e2.end:
            return

        e2_is_pai = self.pattern_is_in_context(p_pai, e2, left_context_size=15, right_context_size=0)
        e2_is_mae = self.pattern_is_in_context(p_mae, e2, left_context_size=15, right_context_size=0)
        if not (e2_is_pai or e2_is_mae):
            return

        e1_is_pai = self.pattern_is_in_context(p_pai, e1, left_context_size=15, right_context_size=0)
        e1_is_mae = self.pattern_is_in_context(p_mae, e1, left_context_size=15, right_context_size=0)

        if e1_is_pai or e1_is_mae:
            return

        d = e2.start - e1.end
        if e2_is_pai:
            e1.add_candidate(e2, d, "pessoa-pai")
        elif e2_is_mae:
            e1.add_candidate(e2, d, "pessoa-mae")

    def pessoa_endereco(self, e1, e2):
        if not self.is_in_context(["reside", "mora", "domicil"],
                                  e2, left_context_size=40, right_context_size=0):
            return
        d = self.proximity_score(e1, e2, context_size=100, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "reside_em")

    def pessoa_data(self, e1, e2):
        if not self.is_in_context(["nasc"],
                                  e2, left_context_size=20, right_context_size=0):
            return

        e1_is_pai = self.pattern_is_in_context(p_pai, e1, left_context_size=15, right_context_size=0)
        e1_is_mae = self.pattern_is_in_context(p_mae, e1, left_context_size=15, right_context_size=0)

        if e1_is_pai or e1_is_mae:
            return

        d = self.proximity_score(e1, e2, context_size=200, prioritize_e1_before_e2=True)
        if d is not None:
            e1.add_candidate(e2, d, "data_nascimento")


