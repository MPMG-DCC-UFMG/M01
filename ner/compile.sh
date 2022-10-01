#!/bin/sh

# Gerar o arquivo que contem o caminho das fontes .java

find -name "*.java" > sources.txt

# Gerar os .class na pasta bin, utilizando as bibliotecas utilizadas no projeto, no caminho lib

echo "javac -d bin @sources.txt -cp  \"lib/*\""
javac -d bin @sources.txt -cp  "lib/*"

# Navegar atá a pasta classes
cd bin

# Criar 1 arquivo manifest.txt no diretório classes com a linha. (após o :, é caminho do pacote até a classe que deseja definir como principal)
echo "Main-Class: Pipeline" > manifest.txt

# Gerar o arquivo que contém o caminho dos .class
find -name "*.class" > sources_class.txt

# Gerar jar

echo "jar cfm ../mp-ufmg-ner.jar manifest.txt @sources_class.txt"

jar cfm ../mp-ufmg-ner.jar manifest.txt @sources_class.txt

cd ..

