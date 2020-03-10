# M02
 Processamento de linguagem natural para reconhecimento, extração e classificação de entidades nomeadas e suas relações.
 

Reconhecedor de entidades atual (rule_based_ner.py): Baseia-se em uma combinação de expressões regulares com o extrator de nomes (de pessoas e organizações) da biblioteca spaCy.

As expressões regulares estão sendo mantidas no arquivo rules.tsv, que contém uma expressão por linha, no formato: <TIPO_ ENTIDADE> \t <EXPRESSÃO_REGULAR> 


Como utilizar:

1) Baixar todo o código e ir para a pasta onde foi baixado

2) Instalar bibliotecas:
     pip3 install requirements.txt

     Obs.: Se preferir, pode instalar dentro de um ambiente virtual (https://docs.python.org/3/tutorial/venv.html)

3) Rodar o script:
      python3 -m rule_based_ner entrada saida
 
     onde entrada é um arquivo contendo texto livre qualquer e saída é o arquivo de saída, que está no seguinte formato: uma entidade por linha e três colunas separadas por \t: tipo da entidade, string da entidade, e janela de texto onde ela apareceu. Também é gerado um arquivo .json no formato aceito pelo doccano (interface gráfica para rotulação de texto)


4) Testes rápidos:

    Para testar se o reconhecedor está funcionando bem, por exemplo para entidades do tipo "LOCAL", digite:

      grep -x -e "LOCAL.*" <saida>

    Assim, imprimem-se todas as linhas do arquivo <saida> que começam com a string LOCAL

