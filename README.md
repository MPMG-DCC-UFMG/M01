# M02
 Processamento de linguagem natural para reconhecimento, extração e classificação de entidades nomeadas e suas relações.


Reconhecedor de entidades atual (mp-ufmg-ner.jar): Baseia-se em uma combinação de expressões regulares com o reconhecedor de entidades da biblioteca CoreNLP.

As expressões regulares estão sendo mantidas no arquivo rules.tsv, que contém uma expressão por linha, no formato: TIPO_ ENTIDADE \t EXPRESSÃO_REGULAR


Pre-requisitos:

    - Python 3

    - Java 8 ou superior


Como utilizar:

1) Baixar todo o código e ir para a pasta onde foi baixado

2) Instalar bibliotecas:

     sudo pip3 install requirements.txt

     Obs.: Se preferir, pode instalar dentro de um ambiente virtual (https://docs.python.org/3/tutorial/venv.html)


3) Baixar o modelo de reconhecimento de entidades:

    wget https://drive.google.com/file/d/1e5PaQKkfs6x7wjhn_Np4o2xBJM8FuCI_/view?usp=sharing


4) Executar:

    java -cp mp-ufmg-ner.jar:lib/* Pipeline <diretorio de entrada> <diretorio de saida> [#threads (opcional)] 2> /dev/null
 
