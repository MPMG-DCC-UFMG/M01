import sys
import json
from nltk.metrics.distance import edit_distance
from preprocessing.casing import title_case
from preprocessing.text_cleaner import extract_digits
from inout import read_lower_cased_strings
import re

DATE_PATTERN = re.compile("(\d\d?\s?/\s?\d\d?/\s?\d\s?\.?\s?\d(\d\d)?)|(\d\d?\s?\-\s?\d\d?\-\s?\d\s?\.?\s?\d(\d\d)?)")

FILENAME_MUNIC = "data/municipios.txt"
MUNICIPIOS = read_lower_cased_strings("data/municipios.txt")
WSIZE = 100
MODALIDADES = ["convite", "tomada de preços", "concorrência", "concurso", "pregão presencial", "pregão eletrônico", "leilão"]
TIPOS = ["melhor técnica", "menor preço", "maior lance ou oferta", "técnica e preço"]
INF = 999999999


#Carrega saida ".aux" do reconhecedor de entidades
def load_entities(filename):
    entities = {}
    infile = open(filename, encoding="utf-8")
    for line in infile:
        spl = line.strip().split("\t")
        ent_type = spl[0].strip()
        if ent_type not in entities:
            entities[ent_type] = []
        entities[ent_type].append(spl[1:])
    filename.close()
    return entities


def load_entities_from_json2(filename):
    entities = {}
    infile = open(filename, encoding="utf-8")
    data = json.load(infile)
    infile.close()
    text = data["text"]
    for ent in data["entities"]:
        ent_type = ent["label"]
        start = ent["start"]
        end = ent["end"]
        ent_string = ent["entity"]
        prev_context = text[max(0, start-WSIZE):start]
        next_context = text[end:end+WSIZE]
        if ent_type not in entities:
            entities[ent_type] = []
        entities[ent_type].append( [ent_string, prev_context, next_context] )
    return entities, text



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



def extract_num_processo(entities):

    modalid = None

    if "NUM_LICIT_OU_MODALID" not in entities:
        return "", "", None

    #Formato de codigos[i]: [string_entidade, contexto_anterior, contexto_posterior]
    codigos = entities["NUM_LICIT_OU_MODALID"]

    #Verifica os dois primeiros codigos de licitacao extraidos,
    #dando prioridade ao que eh precedido pelo nome da modalidade
    ind = 0
    ind_verificado = -1
    okok = False
    for cod in codigos[:2]:
        ok = False
        previous_window = cod[1].lower()
        for modalidade in MODALIDADES:
            if modalidade in previous_window:
                ok = True
                okok = True
                modalid = title_case(modalidade)
        if ok:
            part1, part2 = cod[0].split("/")
            ind_verificado = ind
        ind += 1

    print("Indice do processo", ind_verificado)

    if not okok:
        print("Nenhum codigo precedido de modalidade")
        ind = 1
        if len(codigos) == 1:
            ind = 0
        part1, part2 = codigos[ind][0].split("/")
        ind_verificado = ind

    print("Indice do processo", ind_verificado)
    part1 = str(int(extract_digits(part1)))
    part2 = str(extract_digits(part2))
    if len(part2) == 2:
        part2 = "20" + part2
    print("BEFORE:", codigos[ind_verificado][0], "AFTER: %s/%s" % (part1, part2))

    return part1, part2, modalid




def extract_municipio(entities):
    res = ""
    if "MUNICIPIO" not in entities:
        return ""
    ents = entities["MUNICIPIO"]

    #Extrai nome da primeira entidade detectada como municipio
    string = ents[0][0].strip()
    before = string
    string = string.lower()
    spl = string.split()

    #Elimima "Municipio de" do nome, se houver
    if "município de" in string or "municipal de" in string:
        spl = spl[2:]

    n = len(spl)
    for cutoff in range(n):
        string = " ".join(spl[:n-cutoff])
        if string in MUNICIPIOS:
            res = title_case(string)
            break
    print("BEFORE:", before, "AFTER:", res)

    return title_case(string)


def extract_modalidade(entities):
    if "MODALIDADE_LICITACAO" not in entities:
        return ""
    ents = entities["MODALIDADE_LICITACAO"]

    #Extrai nome da primeira entidade detectada como modalidade
    before = ents[0][0].strip()
    string = before.lower()

    #Elimima "modalidade" do nome, se houver
    if "modalidade" in string:
        string = " ".join(string.split()[1:])

    res = title_case(extract_by_edit_distance(string, MODALIDADES))
    print("BEFORE:", before, "AFTER:", res)
    return res


def extract_tipo(entities):
    if "TIPO_LICITACAO" not in entities:
        return ""
    ents = entities["TIPO_LICITACAO"]

    #Extrai nome da primeira entidade detectada como modalidade
    before = ents[0][0].strip()
    string = before.lower()

    #Elimima "modalidade" do nome, se houver
    if "tipo" in string:
        string = " ".join(string.split()[1:])

    res = title_case(extract_by_edit_distance(string, TIPOS))
    print("BEFORE:", before, "AFTER:", res)
    return res


#Faz casamento exato dos tipos no texto original
def extract_tipo_from_orig_text(orig_text):
    if len(orig_text) == 0:
        return ""
    orig_text_low = orig_text.lower()

    for tipo in TIPOS:
        if tipo in orig_text_low:
            return title_case(tipo)
    return ""


def valid_date(yyyy, mm, dd):
    return len(yyyy) == 4 and int(mm) > 0 and int(mm) < 13 and int(dd) > 0 and int(dd) < 32

#ano: pode ter sido extraido anteriormente pelo numero do processo
def extract_data_rec_doc(entities, ano):

    if "TEMPO" not in entities:
        return ""

    #Formato de codigos[i]: [string_entidade, contexto_anterior, contexto_posterior]
    tempos = entities["TEMPO"]

    #Verifica as N primeiras entidades detectadas como TEMPO,
    #dando prioridade a que tenha "receb" na string do contexto anterior

    N = 10
    ind_verificado = -1
    ok = False
    valid_times = []
    valid_inds = []
 
    for ind,tempo in enumerate(tempos):
        if ind > N:
            break
        if not DATE_PATTERN.match(tempo[0]): #not ("/" in tempo[0] or "-" in tempo[0]):
            continue
        valid_times.append(tempo[0])
        valid_inds.append(ind)
        previous_window = tempo[1].lower()
        if "rece" in previous_window or "abert" or "public" in previous_window:
            ok = True
            ind_verificado = ind
            break

    if len(valid_times) == 0:
        return ""

    if ok:
        print("Indice da data de recebimento", ind_verificado)
    else:
        print("Nenhuma das strings \"rece\", \"abert\" ou \"public\" aparece no contexto de alguma data")
        ind = valid_inds[0]


    date_string = tempos[ind][0]
    if ("/" in date_string):
        spl = date_string.split("/")
    elif ("-" in date_string):
        spl = date_string.split("-")
    else:
        return ""

    dd = "%02d" % ( int(extract_digits(spl[0])) )
    mm = "%02d" % ( int(extract_digits(spl[1])) )

    if len(spl) == 3:
        yyyy = extract_digits(spl[2])
        if len(yyyy) == 2:
            yyyy = "20" + yyyy
    else:
        yyyy = ano
    if valid_date(yyyy, mm, dd):
        res = "-".join( [yyyy, mm, dd] )
    else:
        res = ""
    print("BEFORE:", date_string, "AFTER:", res)
    return res


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file (entities.json)> <outfile>" % sys.argv[0])
        sys.exit(-1)

    ents,orig_text = load_entities_from_json2(sys.argv[1])
    outfile = open(sys.argv[2], "w", encoding="utf-8")

    if len(ents) == 0:
        print("Nao foram detectadas entidades no arquivo")
        exit(-1)

    #mod (modalidade) pode ser descoberta ao extrair o numero do processo,
    #sendo obtida da janela de texto que o antecede
    num, ano, mod = extract_num_processo(ents)

    if mod == None:
        mod = extract_modalidade(ents)

    mun = extract_municipio(ents)
    tipo = extract_tipo_from_orig_text(orig_text)
    data = extract_data_rec_doc(ents, ano)

    row = ["%%%s%%" % num, ano, mod, mun, tipo, data]
    to_print = ",".join(row)
    if len(to_print) > len(row) + 1:
        print(to_print, file=outfile)
        print(to_print)
    print()
    outfile.close()



