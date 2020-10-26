# M02: Processamento de linguagem natural para reconhecimento, extração e classificação de entidades nomeadas e suas relações

Reconhecedor de entidades atual (mp-ufmg-ner.jar): Baseia-se em uma combinação de expressões regulares com o reconhecedor de entidades da biblioteca CoreNLP.

As expressões regulares estão sendo mantidas no arquivo rules.tsv, que contém uma expressão por linha, no formato: TIPO_ ENTIDADE \t EXPRESSÃO_REGULAR

# Pré-requisitos

- Python 3

- Java 8 ou superior



# Como utilizar

1) Baixar todo o código e ir para a pasta onde foi baixado

2) Instalar bibliotecas:

   sudo pip3 install requirements.txt

   Obs.: Se preferir, pode instalar dentro de um ambiente virtual (https://docs.python.org/3/tutorial/venv.html)

3) Baixar o modelo de reconhecimento de entidades e colocá-lo na pasta "models"

    wget https://drive.google.com/file/d/1e5PaQKkfs6x7wjhn_Np4o2xBJM8FuCI_/view?usp=sharing

4) Executar:

   java -cp mp-ufmg-ner.jar:lib/* Pipeline ENTRADA SAÍDA [#threads (opcional)] 2> /dev/null
   
   onde:

    - ENTRADA pode ser um diretório ou um arquivo texto, PDF, ou HTML. Se for um diretório, serão processados todos os arquivos texto/PDF/HTML do diretório. A mesma estrutura de diretórios da ENTRADA é reproduzida na SAÍDA.

    - SAÍDA é o nome do arquivo de saída (se ENTRADA for um arquivo) ou o nome do diretório de saída (se ENTRADA for um diretório).
    
    
    Também é possível passar o texto de entrada na própria linha de comando, utilizando a opção "-str", da seguinte maneira:
    
    java -cp mp-ufmg-ner.jar:lib/* Pipeline -str "texto de entrada"
    
    Nesse caso, o resultado será impresso na saída padrão


# Formato de entrada/saída

Formato de entrada: Arquivos de texto ou PDF ou HTML

Formato de saída: Arquivos JSON com a estrutura ilustrada no seguinte exemplo:

{

    "file": "data/teste.txt",
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
    ],
    "timestamp": "2020-09-24 19:09:29.387"
}


onde "file" é o arquivo de origem, "text" é o texto contido no arquivo de origem, "timestamp" contém a data e horário em que o arquivo foi processado e "entities" é a lista de entidades extraídas

Para cada entidade:

   - "start", "end": índices de início e fim da entidade no texto
   
   - "label": tipo de entidade
   
   - "entity": sequência de caracteres da entidade (corresponde a text[start:end])

 
