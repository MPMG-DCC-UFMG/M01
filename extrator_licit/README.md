# Extrator de licitações

É uma aplicação que utiliza como entrada a saída (.json) do reconhecedor de entidades MP-UFMG-NER e produz como saída uma linha de csv contendo os seguintes atributos básicos de uma licitação:

Número_Licitação, Ano, Modalidade, Município, Tipo, Data de recebimento

Ex.:

26,2017,Pregão Presencial,Varginha,Menor Preço,2017-06-23

# Requisitos
 - Python3

# Instalação
    pip install -r requirements.txt
    python3 -m spacy download pt_core_news_sm

# Como executar
    python3 -m data_extraction.licitacao ENTRADA SAIDA

    onde:

    - ENTRADA: Arquivo de entidades (aceita ambos os formatos .json definidos acima)

    - SAIDA: Nome do arquivo que conterá a linha csv definida acima
