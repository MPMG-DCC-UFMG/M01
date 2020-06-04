from inout import *
import sys
import spacy
import random
from tqdm import tqdm
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("usage: %s <input file (annotated data)> <outdir (model)> " % sys.argv[0])
        sys.exit(-1)

    nlp = spacy.blank('pt')
    n_iter = 50
    #TRAIN_DATA = load_2col_annotated_data(sys.argv[1])

    filename = sys.argv[1]
    if filename.endswith(".conll"):
        TRAIN_DATA = conll2spacy_train_data(filename)
        outaux = open("aux.tmp", "w", encoding="utf-8")
        for text, annotations in TRAIN_DATA:
            for ent in annotations.get('entities'):
                print(ent[2], "\t", text[ent[0]:ent[1]], file=outaux)
    else:
        TRAIN_DATA = json2spacy_train_data(filename)
    output_dir = Path(sys.argv[2])
    if not output_dir.exists():
        output_dir.mkdir()

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels

    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in tqdm(TRAIN_DATA):
                nlp.update(
                    [text],  # batch of texts
                    [annotations],  # batch of annotations
                    drop=0.5,  # dropout 
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)
    
    nlp.meta["name"] = "lener"  # rename model
    "Small test:"
    print(text)
    text = "MARIA DO CARMO TEIXEIRA, MASP 130234-7, foi passear no parque e viu seus colegas de trabalho da empresa SOLUCOES EM INFORMATICA LTDA. ANA PAULA montou um micro empreendimento e o nomeou ANA PAULA ME. Esta empresa fica localizada no estado de Minas Gerais, na cidade de Belo Horizonte. Outro negocio similar fica em Juiz de Fora."
    doc = nlp(text)
    for ent in doc.ents:
        print("%s\t%s" % (ent.label_, ent.text))

    # save model to output directory
    nlp.to_disk(output_dir)
    print("Saved model to", output_dir)


