# MP-UFMG-NER

Reconhecedor de entidades baseado em uma combinação de expressões regulares com o reconhecedor de entidades da biblioteca CoreNLP.

As expressões regulares estão sendo mantidas no arquivo rules.tsv, que contém uma expressão por linha, no formato: TIPO_ ENTIDADE \t EXPRESSÃO_REGULAR

# Pré-requisitos

Java 8 ou superior

# Tipos de entidade reconhecidos (rótulos)
PESSOA, ORGANIZAÇÃO, LOCAL, TEMPO, LEGISLAÇÃO e JURISPRUDÊNCIA, por meio do modelo treinado pelo método CoreNLP;

VALOR MONETÁRIO, CPF, CNPJ, CEP, MASP, TELEFONE e LICITAÇÃO (incluindo os seguintes atributos de licitação: número (NUM_LICIT_OU_MODALID), ANO, MODALIDADE, TIPO, OBJETO, DOTAÇÃO_ORÇAMENTÁRIA, por meio de expressões regulares.

# Instalação

Baixar todo o código e ir para a pasta "ner"

Baixar o modelo de reconhecimento de entidades do link abaixo e colocá-lo na pasta "ner/models":

   ```
      https://drive.google.com/u/0/uc?id=1e5PaQKkfs6x7wjhn_Np4o2xBJM8FuCI_
   ```
# Como executar:

O programa pode ser executado em dois modos: (1) modo "servidor-cliente" e (2) modo "uma-execução".
O modo "servidor-cliente" é indicado para carregar o modelo uma única vez e fazer quantas requisições quiser, sob demanda.
O modo "uma-execução" executa o ner para um unico par entrada-saída e carrega novamente o modelo toda vez que é chamado.

# Como executar (modo "servidor-cliente")

1. Iniciar o servidor (uma única vez)
```
java -Dfile.encoding=UTF-8 -jar mp-ufmg-ner.jar
```

2. Fazer chamadas ao cliente. Cada chamada é feita através do comando:

```
java -Dfile.encoding=UTF-8 -cp mp-ufmg-ner.jar Client [ENTRADA] [SAÍDA]
```

onde ENTRADA e SAIDA são argumentos opcionais e indicam os arquivos de entrada e saída, respectivamente.
Caso não forem fornecidos esses argumentos, serão utilizados a entrada e a saída padrão


# Como executar (modo "uma-execução")


```
java -Dfile.encoding=UTF-8 -jar mp-ufmg-ner.jar ENTRADA SAÍDA
```

onde:

- ENTRADA pode ser um diretório ou um arquivo texto, PDF, ou HTML. Se for um diretório, serão processados todos os arquivos texto/PDF/HTML do diretório, e a mesma estrutura de diretórios da ENTRADA será reproduzida na SAÍDA.

- SAÍDA é o nome do arquivo de saída (se ENTRADA for um arquivo) ou o nome do diretório de saída (se ENTRADA for um diretório).
Configurações do NER


# Configurações

O arquivo config.txt apresenta algumas opções para executar o reconhecedor de entidades, entre elas a opção "segmented = true", que serve para dividir o texto em partes na saída. Normalmente não é necessário alterar nenhuma opção, mas em algumas situações isto pode ser útil. A lista de opções encontra-se abaixo:

- removeNewLines: Remover (true) ou não (false) quebras de linha do texto

- segmented: Segmentar (true) ou não (false) o texto

- aproxSegmentSize: tamanho aproximado do segmento (em número de caracteres). Ignorado se segmented=false.

- minSegmentSize: tamanho mínimo de um segmento de texto (ignorado se segmented=false)

- model: arquivo contendo o modelo de reconhecimento de entidades (arquivo binário produzido pelo CoreNLP)

- regexFile: arquivo contendo as expressões regulares


# Formato de entrada/saída

Formato de entrada: Arquivos de texto ou PDF ou HTML

Formato de saída (segmented): Arquivos JSON com a estrutura ilustrada no seguinte exemplo:

```
{

"src_file": "data/teste.txt",
"file": "data/teste.json",
"sentences": [
    {
        "text": "João da Silva nasceu em Teresópolis."
        "entities": [
            {
                "start": 0,  
                "end": 13,   
                "label": "PESSOA", 
                "entity": "João da Silva" 
            },
            {
                "start": 24,
                "end": 36,
                "label": "LOCAL",
                "entity": "Teresópolis"
            }
        ]
    }
],
"timestamp": "2020-09-24 19:09:29.387"
}
```

onde:

 - "src_file": arquivo de origem

 - "file": arquivo de saida

 - "sentences": texto contido no arquivo de origem, separado em partes

 - "text": cada parte do texto

- "timestamp" contém a data e horário em que o arquivo foi processado

- "entities": é a lista de entidades extraídas

Para cada entidade:

- "start", "end": índices de início e fim da entidade no texto

- "label": tipo de entidade

- "entity": sequência de caracteres da entidade (corresponde a text[start:end])

Formato de saida (sem a opção -segmented):

Similar ao formato descrito acima, porém o texto do arquivo de origem não é dividido em "sentences"
