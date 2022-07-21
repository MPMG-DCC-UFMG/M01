import argparse
import json
import socket
from args import train_argparser, eval_argparser, predict_argparser
from config_reader import process_configs
from spert import input_reader
from spert.spert_trainer import SpERTTrainer
from spert.evaluator import Evaluator
from pipeline import Pipeline
from preprocessing.json_formater import to_char_level_format
from postprocessing.merge_spans import merge_spans

def my_config_parser(config_filename):
    config_file = open(config_filename)
    dic = {}
    for line in config_file:
        lin = line.strip()
        if lin.startswith("#"):
            continue
        spl = lin.split("=")
        dic[spl[0].strip()] = spl[1].strip()
    config_file.close()
    return dic



def _train():
    arg_parser = train_argparser()
    process_configs(target=__train, arg_parser=arg_parser)


def __train(run_args):
    trainer = SpERTTrainer(run_args)
    trainer.train(train_path=run_args.train_path, valid_path=run_args.valid_path,
                  types_path=run_args.types_path, input_reader_cls=input_reader.JsonInputReader)


def _eval():
    arg_parser = eval_argparser()
    process_configs(target=__eval, arg_parser=arg_parser)

def _eval_pred():
    arg_parser = predict_argparser()
    process_configs(target=__eval_pred, arg_parser=arg_parser)


def __eval(run_args):
    trainer = SpERTTrainer(run_args)
    trainer.eval(data_or_path=run_args.dataset_path, types_path=run_args.types_path,
                 input_reader_cls=input_reader.JsonInputReader)

def __eval_pred(run_args):
    evaluator = Evaluator(run_args)
    evaluator.compute_scores()

def _predict():
    arg_parser = predict_argparser()
    process_configs(target=__predict, arg_parser=arg_parser)


def __predict(run_args):
    trainer = SpERTTrainer(run_args)
    data_arg = run_args.dataset_path
    if not data_arg.endswith(".json"):
        pipeline = Pipeline()
        infile = open(data_arg, encoding="utf-8")
        text = infile.read()
        infile.close()
        jdata,data_arg = pipeline.process(text)
    predictions = trainer.predict(data_or_path=data_arg, types_path=run_args.types_path,
                    input_reader_cls=input_reader.JsonPredictionInputReader)
    with open(run_args.predictions_path, "w", encoding="utf-8") as outfile:
        json.dump(predictions, outfile, indent=4)

def _test():
    arg_parser = predict_argparser()
    process_configs(target=__test, arg_parser=arg_parser)


def __test(run_args):
    trainer = SpERTTrainer(run_args)
    print("Dataset_path:", run_args.dataset_path)
    data = [
             {
               "tokens":["João", "Silva", "mora", "na", "Rua", "dos", "Milagres", "."]
               #"entities": [{"start":0, "end":2, "type": "PESSOA"}, {"start":4, "end":7, "type": "LOCAL"}],
               #"relations": [{"head":0, "tail":1, "type": "local_residencia"}]
             }
           ]

    predictions = trainer.predict(data_or_path=data, types_path=run_args.types_path,
                    input_reader_cls=input_reader.JsonPredictionInputReader)
    with open(run_args.predictions_path, "w", encoding="utf-8") as outfile:
        json.dump(predictions, outfile, indent=4)



#Carrega modelo na memoria 1 unica vez e espera por requisicoes de "predict"
def _requests():
    arg_parser = predict_argparser()
    process_configs(target=__requests, arg_parser=arg_parser)

def __requests(run_args):
    print("Starting MP-UFMG NERRE server")
    trainer = SpERTTrainer(run_args)
    #trainer._load_model() #Ja chama na primeira vez que faz o predict
    pipeline = Pipeline()
    config = my_config_parser("configs/ner_service.conf")
    port = int(config["port"])

    server = socket.socket()
    server.bind(('', port))
    #print("socket binded to %s" % (port))
    server.listen()
    print("MP-UFMG NERRE server is listening")

    while True:
        c, addr = server.accept()
        #print('Got connection from', addr)
        msg = c.recv(1024)
        try:
            request = json.loads(msg.decode("utf-8"))
        except:
            request = {}
        c.close()
        print(request)
        if "input" in request:
            infile = open(request["input"], encoding="utf-8")
            text = infile.read()
            infile.close()
            run_args.predictions_path = request["output"]
            jdata, jdata_marked = pipeline.process(text) #Converte texto no formato de entrada do SpERT

            predictions = trainer.predict(data_or_path=jdata, types_path=run_args.types_path,
                             input_reader_cls=input_reader.JsonPredictionInputReader)

            #Adicionar entidades identificadas por regex
            for i, pred in enumerate(predictions):
                pred["entities"] += jdata[i]["entities"]

            #Post-processing
            predictions = merge_spans(predictions)

            #Conversao de formato de saida
            predictions = to_char_level_format(predictions,
                                               source_file=request["input"],
                                               dest_file=run_args.predictions_path)

            with open(run_args.predictions_path, "w", encoding="utf-8") as outfile:
                json.dump(predictions, outfile, indent=4)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.add_argument('mode', type=str, help="Mode: 'train' or 'predict' or 'server'")
    args, _ = arg_parser.parse_known_args()

    if args.mode == 'train':
        _train()
    elif args.mode == 'eval':
        _eval()
    elif args.mode == 'predict':
        print("INFERENCIA")
        _predict()
    elif args.mode == 'server':
        _requests()
    else:
        raise Exception("Mode not in ['train', 'eval', 'predict', 'server'], e.g. 'python spert.py train ...'")
