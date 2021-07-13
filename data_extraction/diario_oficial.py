import sys
import json
import pandas
from math import floor
import re
from operator import itemgetter
from unicodedata import normalize

from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words('portuguese'))

DATE_PATTERN = re.compile("(\d\d?\s?/\s?\d\d?/\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\-\s?\d\d?\-\s?\d\s?\.?\s?\d(\d\d)?)")
WSIZE = 300

ACAO = re.compile("\\n([\w ]+)(?=\s*[Nn]os\s*[Tt]ermos)", flags=re.IGNORECASE)


def load_entities_from_json(filename):
    index = {} #mapeia a posicao de um bloco do texto na lista de entidades contidas no bloco
    infile = open(filename, encoding="utf-8")
    data = json.load(infile)
    infile.close()

   # entities: vetor de entidades na ordem que elas aparecem no texto
   # Cada elemento desse vetor eh um par (start_position, entity)

    entities = sorted([ (ent["start"], ent) for ent in data["entities"] ], key=itemgetter(0))
    for ind, pair in enumerate(entities):
        start, ent = pair
        dicpos = int(start / WSIZE)
        if dicpos not in index:
            index[dicpos] = []
        index[dicpos].append(ind)
    return entities, index, data["text"]


#Encontra indice (referente a lista "entities") da entidade mais proxima da posicao "char_pos" no texto de entrada
def find_closest_ent(char_pos, index, entities):
    dicpos = int(char_pos / WSIZE)
    if dicpos not in index:
        return -1   #Not found
    i = index[dicpos][0]

    while entities[i][0] < char_pos:
        i += 1
        if i >= len(entities):
            return -1
    return i


def filter_text(doc):	
    doc = normalize('NFKD', doc).encode('ascii', 'ignore').decode('utf8')
    return re.sub('[^a-zA-Z0-9 \/\\n]', '', doc)


#Extrai lista de servidores-alvo da acao, lei em que ela se baseia e datas
def extract_after(match_acao, entities, index):
    masps = []
    pessoas = []
    leis = []
    datas = []
    char_pos = match_acao.end()
    ind = find_closest_ent(char_pos, index, entities)
    if ind == -1:
        return masps, pessoas, leis, datas

    lei_pos = -1

    while entities[ind][0] < char_pos + WSIZE:
        label = entities[ind][1]["label"]
        ent_string = entities[ind][1]["entity"]
        if label == "MASP":
            masps.append(ent_string)
        elif label == "PESSOA":
            pessoas.append(ent_string)
        elif label == "LEGISLACAO":
            leis.append(ent_string)
            lei_pos = entities[ind][0]
        elif label == "TEMPO":
            if DATE_PATTERN.match(ent_string) != None and entities[ind][0] - lei_pos > 15:
                datas.append(ent_string)
        ind += 1
        if ind >= len(entities):
            break
    return masps, pessoas, leis, datas


#Extrai ATO e ORGAO responsavel
def extract_before(match_acao, entities, index):
    ato = None
    org = None
    char_pos = match_acao.start()
    ind = find_closest_ent(char_pos, index, entities)
    if ind == -1:
        return ato, org

    while entities[ind][0] > char_pos - 80:
        label = entities[ind][1]["label"]
        ent_string = entities[ind][1]["entity"]
        if label == "ATO":
            ato = ent_string
        elif label == "ORGANIZACAO":
            org = ent_string
        ind += 1
        if ind >= len(entities):
            break
    return ato, org


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file (entities.json)> <outfile>" % sys.argv[0])
        sys.exit(-1)

    entities, index, text = load_entities_from_json(sys.argv[1])
    outfile = open(sys.argv[2], "w", encoding="utf-8")

    if len(entities) == 0:
        print("Nao foram detectadas entidades no arquivo", file=sys.stderr)
        exit(-1)

    rows = []
    for match in ACAO.finditer(text):
        acao = match.string[match.start():match.end()].replace("\n", " ")
        if True: #if has_at_least_one(acao.lower(), ACAO_WORDS):
            acao_words = filter_text(acao.strip().lower()).split()
            acao_words = [x for x in acao_words if x not in STOPWORDS]
            rel = "_".join(acao_words)
            context = text[ max(0, match.start() - 80) : match.end()+WSIZE ]
            masps, pessoas, leis, datas = extract_after(match, entities, index)
            masps_match_pessoas = len(masps) == len(pessoas)
            data = None
            if len(datas) > 0:
                data = datas[0]
            ato, org = extract_before(match, entities, index)
            leis_str = "|".join(leis)

            for j,masp in enumerate(masps):
                rows.append(["[preencher]", masp, "COMPETENCIA", "MASP", rel, leis_str, data, context])
                if ato != None:
                    rows.append([ato, masp, "ATO", "MASP", rel, leis_str, data, context])
                if org != None:
                    rows.append([org, masp, "ORGANIZACAO", "MASP", rel, leis_str, data, context])
                if masps_match_pessoas:
                    rows.append([pessoas[j], masp, "PESSOA", "MASP", "masp", "", "", context])
                else:
                    rows.append(["[preencher]", masp, "PESSOA", "MASP", "masp", "", "", context])

    df = pandas.DataFrame(rows, columns="ENTIDADE_1 ENTIDADE_2 TIPO_ENTIDADE_1 TIPO_ENTIDADE_2 TIPO_RELACAO LEIS DATA FRASE".split())
    df.to_csv(outfile, index=False)


