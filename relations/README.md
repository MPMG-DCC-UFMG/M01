# Extrator de Relações Baseado em Regras
Gera, a partir de um arquivo com entidades já identificadas, uma lista de relações existentes entre essas entidades

# Pré-requisitos
 - Python 3
 - NER (https://github.com/MPMG-DCC-UFMG/M01/tree/master/ner) atualizado
 - Não é necessária a instalação de nenhuma biblioteca

# Como executar

Linha de comando:
```
python main.py ENTRADA SAÍDA [--use-indices]
```
onde:
 - ENTRADA: caminho do arquivo de entrada (que é a saída do NER)
 - SAÍDA: caminho do arquivo onde será produzida a saída
 - --use-indices (opcional): na lista de relações, especificar as entidades através de índices em vez de strings

# Entrada
Arquivo .json gerado pelo extrator de entidades NER (https://github.com/MPMG-DCC-UFMG/M01/tree/master/ner)


# Saída
Arquivo contendo todos os dados gerados pelo NER acrescidos da lista de relações identificadas.

Formato do arquivo: mesmo formato do NERRE (vide https://github.com/MPMG-DCC-UFMG/M01/tree/master/nerre#formato-de-sa%C3%ADda)


# Tipos de entidades e relações reconhecidos

A Figura abaixo mostra os tipos de entidades(retângulos) e relação (setas) extraídos:

![Tipos de Entidade e Relação reconhecidos](https://user-images.githubusercontent.com/28352865/182921480-1fc333c8-d8e0-4bde-81ce-cb19a8ad7a37.png)


