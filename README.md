# M01: Processamento de linguagem natural para reconhecimento, extração e classificação de entidades nomeadas e suas relações

Reconhecedor de entidades atual (mp-ufmg-ner.jar): Baseia-se em uma combinação de expressões regulares com o reconhecedor de entidades da biblioteca CoreNLP.

As expressões regulares estão sendo mantidas no arquivo rules.tsv, que contém uma expressão por linha, no formato: TIPO_ ENTIDADE \t EXPRESSÃO_REGULAR

# Pré-requisitos

- Python 3

- Java 8 ou superior

# Tipos de entidade reconhecidos (rótulos)

- PESSOA, ORGANIZAÇÃO, LOCAL, TEMPO, LEGISLAÇÃO e JURISPRUDÊNCIA, por meio do modelo treinado pelo método CoreNLP;

- VALOR MONETÁRIO, CPF, CNPJ, CEP, MASP, TELEFONE e LICITAÇÃO (incluindo os seguintes atributos de licitação: número (NUM_LICIT_OU_MODALID), ANO, MODALIDADE, TIPO, OBJETO, DOTAÇÃO_ORÇAMENTÁRIA, por meio de expressões regulares.


# Instalação

1) Baixar todo o código e ir para a pasta onde foi baixado


2) Baixar o modelo de reconhecimento de entidades e colocá-lo na pasta "models"

    wget https://drive.google.com/file/d/1e5PaQKkfs6x7wjhn_Np4o2xBJM8FuCI_/view?usp=sharing
    

# Como executar:

   java -jar mp-ufmg-ner.jar ENTRADA SAÍDA [-segmented (opcional)]
   
   onde:

    - ENTRADA pode ser um diretório ou um arquivo texto, PDF, ou HTML. Se for um diretório, serão processados todos os arquivos texto/PDF/HTML do diretório, e a mesma estrutura de diretórios da ENTRADA será reproduzida na SAÍDA.

    - SAÍDA é o nome do arquivo de saída (se ENTRADA for um arquivo) ou o nome do diretório de saída (se ENTRADA for um diretório).
    
    - segmented: opção para dividir o texto em partes ("sentences") na saída


# Formato de entrada/saída

Formato de entrada: Arquivos de texto ou PDF ou HTML

Formato de saída (segmented): Arquivos JSON com a estrutura ilustrada no seguinte exemplo:

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


# Extrator de licitações

É uma aplicação que utiliza como entrada a saída (.json) do reconhecedor de entidades e produz como saída uma linha de csv contendo os seguintes atributos básicos de uma licitação:

Número_Licitação, Ano, Modalidade, Município, Tipo, Data de recebimento

Ex.:

26,2017,Pregão Presencial,Varginha,Menor Preço,2017-06-23


# Como executar o extrator de licitações:

    python3 -m data_extraction.licitacao ENTRADA SAIDA
    
    onde:
    
    - ENTRADA: Arquivo de entidades (.json definido acima, com texto segmentado)
   
    - SAIDA: Nome do arquivo que conterá a linha csv definida acima
    
    
    
    
    





 
