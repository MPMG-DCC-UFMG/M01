
train=$1
serialize=$2

echo "trainFile = $train"
echo "serializeTo = $serialize"

echo "map = word=0,answer=1"
echo ""
echo "useClassFeature=true"
echo "useWord=true"
echo "useNGrams=true"
echo "noMidNGrams=true"
echo "maxNGramLeng=6"
echo "usePrev=true"
echo "useNext=true"
echo "useSequences=true"
echo "usePrevSequences=true"
echo "maxLeft=1"
echo "useTypeSeqs=true"
echo "useTypeSeqs2=true"
echo "useTypeySequences=true"
echo "wordShape=chris2useLC"
echo "useDisjunctive=true"
