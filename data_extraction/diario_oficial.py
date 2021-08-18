import sys
import json
import pandas
from math import floor
import re
from operator import itemgetter
from unicodedata import normalize
from nltk.metrics.distance import edit_distance
from nltk.corpus import stopwords
from preprocessing.casing import title_case
from preprocessing.text_cleaner import tokenize, remover_acentos, clear_special_chars


STOPWORDS = set(stopwords.words('portuguese'))

DATE_PATTERN = re.compile("(\d\d?\s?/\s?\d\d?/\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\-\s?\d\d?\-\s?\d\s?\.?\s?\d(\d\d)?)")
WSIZE = 300
INF = 999999999
ACAO = re.compile("(\\n[\w\u00C0-\u00FF\,\-% ]+)?\\n([\w\u00C0-\u00FF\,\-% ]+)(?=\s*nos\s*termos)", flags=re.IGNORECASE)

context_start = None
context_end = None

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

def remove_repetitions(text):
    spl = tokenize(text)
    res = []
    words = set()
    for w in spl:
        if w not in words:
            res.append(w)
            words.add(w)
    return " ".join(res)

def filter_text(doc):	
    doc = normalize('NFKD', doc).encode('ascii', 'ignore').decode('utf8')
    return re.sub('[^a-zA-Z0-9 \/\\n]', '', doc)

#Retorna o valor em attr_values mais similar a string
def extract_by_edit_distance(string, attr_values):
    m = INF
    res = ""
    for value in attr_values:
        d = edit_distance(string, value)
        #print("D =", d, value)
        if d < m:
            m = d
            res = value
    return res

def last_alpha_chars(text, pointer, n=2, max_previous=8):
    chars = ""
    i = 0
    while len(chars) < n and i < max_previous:
        i += 1
        c =  text[pointer]
        if c.isalpha():
            chars = c + chars
        pointer -= 1
        if pointer < 0:
            break
    return chars


#Extrai lista de servidores-alvo da acao, lei em que ela se baseia e datas
def extract_after(match_acao, entities, index, text):
    global context_end
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
            pointer = entities[ind][0]
            previous_chars = last_alpha_chars(text, pointer - 1, n=2)
            if previous_chars != "EE":
                pessoas.append(ent_string)
            else:
                print("Escola detected:", previous_chars + " " + ent_string)
                pessoas = [] #Pessoas sao mencionadas depois no nome da escola
        elif label == "LEGISLACAO":
            leis.append(ent_string)
            lei_pos = entities[ind][0]
        elif label == "TEMPO":
            if DATE_PATTERN.match(ent_string) != None and entities[ind][0] - char_pos > 60:
                datas.append(ent_string)
                context_end = entities[ind][1]["end"]
        ind += 1
        if ind >= len(entities):
            break
    return masps, pessoas, leis, datas


#Extrai COMPETENCIA, numero do ATO e/ou ORGAO responsavel
def extract_before(match_acao, entities, index, text):
    global context_start
    ato = None
    org = None
    comp = None
    char_pos = match_acao.end()
    ind = find_closest_ent(char_pos, index, entities)
    if ind == -1:
        return comp, ato, org

    while entities[ind][0] > char_pos - 80:
        label = entities[ind][1]["label"]
        ent_string = entities[ind][1]["entity"]
        if label == "ATO":
            ato = ent_string
            if context_start == None:
                context_start = entities[ind][0]
        elif label == "ORGANIZACAO":
            org = ent_string
            context_start = entities[ind][0]
        elif label == "COMPETENCIA":
            comp_start = 1
            vec = ent_string.split()
            if vec[0].lower().startswith("ato"):
                comp_start = 2
            comp = " ".join(vec[comp_start:])
            context_start = entities[ind][0]
        ind -= 1
        if ind < len(entities):
            break
    return comp, ato, org


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file (entities.json)> <outfile>" % sys.argv[0])
        sys.exit(-1)

    entities, index, text = load_entities_from_json(sys.argv[1])
    outfile = open(sys.argv[2], "w", encoding="utf-8")
    atos_file = open("data/dicionario_atos.txt", encoding="utf-8")

    atos_list = [line.strip().lower() for line in atos_file]
    atos_file.close()

    if len(entities) == 0:
        print("Nao foram detectadas entidades no arquivo", file=sys.stderr)
        exit(-1)

    rows = []
    ato_id = 1
    for match in ACAO.finditer(text):
        acao = match.string[match.start():match.end()].replace("\n", " ").lower()
        #acao_words = filter_text(acao.strip().lower()).split()
        #acao_words = [x for x in acao_words if x not in STOPWORDS]
        #rel = "_".join(acao_words)

        context_start = None
        context_end = None
        #context = text[ max(0, match.start() - 80) : match.end()+WSIZE ]
        masps, pessoas, leis, datas = extract_after(match, entities, index, text)
        masps_match_pessoas = len(masps) == len(pessoas)
        comp, ato, org = extract_before(match, entities, index, text)
        leis_str = "|".join(leis)

        if len(masps) == 0:
            continue

        acao = remove_repetitions(acao)
        rel = extract_by_edit_distance(acao, atos_list)
        print(acao)
        print(rel)
        print("=========")


        d = 0
        p = 0
        data = ""
        pessoa = "[preencher]"

        if context_start == None:
            context_start = match.start()
        if context_end == None:
            context_end = match.end()+WSIZE

        context = text[ context_start : context_end ]
        if comp == None and ato == None:
            ato = "ATO A" + str(ato_id)
            ato_id += 1
            context = ato + " " + context

        for j,masp in enumerate(masps):
            if len(datas) > d:
                data = datas[d]
                d += 1
            if len(pessoas) > p:
                pessoa = pessoas[p]
                p += 1
            if comp != None:
                rows.append([comp, masp, "COMPETENCIA", "MASP", rel, leis_str, data, context])
            if org != None:
                rows.append([org, masp, "ORGANIZACAO", "MASP", rel, leis_str, data, context])

            rows.append([ato, masp, "ATO", "MASP", rel, leis_str, data, context])
            rows.append([pessoa, masp, "PESSOA", "MASP", "masp", "", "", context])

    df = pandas.DataFrame(rows, columns="ENTIDADE_1 ENTIDADE_2 TIPO_ENTIDADE_1 TIPO_ENTIDADE_2 TIPO_RELACAO LEIS DATA FRASE".split())
    df.to_csv(outfile, index=False)


