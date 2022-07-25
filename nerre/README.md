# MP-UFMG-NERRE

Reconhecedor de entidades e relações baseado em uma combinação de expressões regulares com o método SpERT[1]

As expressões regulares estão sendo mantidas no arquivo rules_do.tsv, que contém uma expressão por linha, no formato: TIPO_ ENTIDADE \t EXPRESSÃO_REGULAR

# Pré-requisitos

Python 3

# Tipos de entidade reconhecidos
PESSOA, ORGANIZAÇÃO, LOCAL, DATA, LEGISLAÇÃO, COMPETÊNCIA,
ATO, VALOR MONETÁRIO, CPF, CNPJ, CEP, MASP, TELEFONE

# Tipos de relação reconhecidos
competência, localizado_em, local_residência, data_início,
ato_administrativo, cpf, cnpj, masp, nos_termos_lei, lotado

# Instalação

1) Baixar todo o código e ir para a pasta "nerre"

2) Instalar bibliotecas necessárias:
```
    pip install -r requirements.txt
    python3 -m spacy download pt_core_news_sm
```

3) Baixar e descompactar o modelo de reconhecimento de entidades do link abaixo e colocá-lo na pasta "nerre/models":
```
    gdown https://drive.google.com/u/1/uc?id=1YpHt99AqFoxHMNoXPzR4N6W2Bgg46hJO
```  

# Como executar:

1) Iniciar o servidor local de NER+RE (executado apenas uma vez):
``` 
python spert.py server > server.log 2> server.err &
disown
```

( O trecho de comando "> server.log 2> server.err &" é opcional, e serve para rodar o serviço em background (&) e armazenar a saída padrão (mensagens do terminal) e de erro nos arquivos "server.log" e "server.err", respectivamente. O "disown" serve para desatrelar a execução do terminal, permitindo o seu funcionamento mesmo após o fechamento do terminal )

2) Enviar requisições de NER+RE para servidor. Cada requisição é feita através da seguinte linha de comando:
```
python client.py ENTRADA SAÍDA
```

onde:

ENTRADA: caminho do arquivo contendo texto livre

SAÍDA: caminho do arquivo de saída, que será gerado no formato descrito abaixo.

# Formato de saída

Formato de saída: Arquivos JSON com a estrutura ilustrada no seguinte exemplo:
```
{
    "timestamp": "2022-07-12 13:31:44.996617",
    "src_file": "data/datasets/domg/toy_example.txt",
    "file": "data/datasets/domg/toy_predictions.json"
    "sentences": [
        {
            "text": "Jo\u00e3o da Silva mora em Belo Horizonte",
            "entities": [
                {
                    "entity": "Jo\u00e3o da Silva",
                    "start": 0,
                    "end": 13,
                    "label": "PESSOA"
                },
                {
                    "entity": "Belo Horizonte",
                    "start": 22,
                    "end": 36,
                    "label": "LOCAL"
                }
            ],
            "relations": [
                {
                    "head": "Jo\u00e3o da Silva",
                    "tail": "Belo Horizonte",
                    "label": "local_residencia"
                }
            ]
        }
    ],
}
```
onde:

- "src_file": arquivo de origem

- "file": arquivo de saida

- "sentences": texto contido no arquivo de origem, separado em partes

- "text": cada parte do texto

- "timestamp" contém a data e horário em que o arquivo foi processado

- "entities": é a lista de entidades extraídas

- "relations": é a lista de relações extraídas

Para cada entidade:

- "start", "end": índices de início e fim da entidade no texto

- "label": tipo de entidade

- "entity": sequência de caracteres da entidade (corresponde a text[start:end])


Para cada relação:

- "head" e "tail": strings das entidades que estão sendo relacionadas. No exemplo, a
 entidade "João da Silva" está relacionada à entidade "Belo Horizonte"
 
- "label": tipo da relação


# Referências:

[1] Markus Eberts, Adrian Ulges. Span-based Joint Entity and Relation Extraction with Transformer Pre-training.
       24th European Conference on Artificial Intelligence, 2020.
