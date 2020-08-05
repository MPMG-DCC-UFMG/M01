# M02
 Processamento de linguagem natural para reconhecimento, extração e classificação de entidades nomeadas e suas relações.


Reconhecedor de entidades atual (rule_based_ner.py): Baseia-se em uma combinação de expressões regulares com o extrator de nomes (de pessoas e organizações) da biblioteca spaCy.

As expressões regulares estão sendo mantidas no arquivo rules.tsv, que contém uma expressão por linha, no formato: TIPO_ ENTIDADE \t EXPRESSÃO_REGULAR


Como utilizar:

1) Baixar todo o código e ir para a pasta onde foi baixado

2) Instalar bibliotecas:
     sudo pip3 install requirements.txt

     Obs.: Se preferir, pode instalar dentro de um ambiente virtual (https://docs.python.org/3/tutorial/venv.html)

3) Baixar o modelo CoreNLP:
    wget https://drive.google.com/file/d/1e5PaQKkfs6x7wjhn_Np4o2xBJM8FuCI_/view?usp=sharing

4) Rodar o script:
      ./run_pipeline.sh ENTRADA SAIDA

     onde ENTRADA é um arquivo contendo texto livre qualquer e SAIDA é o nome que será dado aos arquivos de saída. São gerados quatro arquivos de saída em diferentes formatos:
     a) .json: formato utilizado pelo MPMG
     b) _doccano.json: formato utilizado pela aplicação Doccano
     c) .conll: https://universaldependencies.org/format.html
     d) .aux: uma entidade por linha e três colunas separadas por \t: tipo da entidade, string da entidade, e janela de texto onde ela apareceu.


5) Testes rápidos:

    Para testar se o reconhecedor está funcionando bem, por exemplo para entidades do tipo "LOCAL", digite:

      grep -x -e "LOCAL.*" SAIDA.aux

    Assim, imprimem-se todas as linhas do arquivo SAIDA.aux que começam com a string LOCAL
