# Extrator de Relações Baseado em Regras
Gera, a partir de um arquivo com entidades já identificadas, uma lista de relações existentes entre essas entidades

# Pré-requisitos
 - Python 3
 - Não é necessária a instalação de nenhuma biblioteca

# Como executar
```
python main.py ENTRADA SAÍDA [--use-indices]
```
onde:
 - ENTRADA: caminho do arquivo de entrada (que é a saída do NER)
 - SAÍDA: caminho do arquivo onde será produzida a saída

# Entrada
Arquivo .json gerado pelo extrator de entidades NER (https://github.com/MPMG-DCC-UFMG/M01/tree/master/ner)


# Saida
Arquivo contendo todos os dados gerados pelo NER acrescidos da lista de relações identificadas
Formato do arquivo: mesmo formato do NERRE (vide https://github.com/MPMG-DCC-UFMG/M01/tree/master/nerre#formato-de-sa%C3%ADda)

