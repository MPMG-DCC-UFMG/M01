import argparse

from args import train_argparser, eval_argparser, predict_argparser
from config_reader import process_configs
from spert import input_reader
from spert.spert_trainer import SpERTTrainer
from spert.evaluator import Evaluator
from pipeline import Pipeline

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
    trainer.eval(dataset_path=run_args.dataset_path, types_path=run_args.types_path,
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
    trainer.predict(dataset_path=data_arg, types_path=run_args.types_path,
                    input_reader_cls=input_reader.JsonPredictionInputReader)

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

    trainer.predict(dataset_path=data, types_path=run_args.types_path,
                    input_reader_cls=input_reader.JsonPredictionInputReader)



#Carrega modelo na memoria 1 unica vez e espera por requisicoes de "predict"
def _requests():
    arg_parser = predict_argparser()
    process_configs(target=__requests, arg_parser=arg_parser)

def __requests(run_args):
    trainer = SpERTTrainer(run_args)
    #trainer._load_model() #Ja chama na primeira vez que faz o predict
    pipeline = Pipeline()

    while True:
        text = input("Digite o texto: ")
        jdata, jdata_marked = pipeline.process(text) #Converte texto no formato de entrada do SpERT

        trainer.predict(dataset_path=jdata, types_path=run_args.types_path,
                    input_reader_cls=input_reader.JsonPredictionInputReader)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.add_argument('mode', type=str, help="Mode: 'train' or 'eval'")
    args, _ = arg_parser.parse_known_args()

    if args.mode == 'train':
        _train()
    elif args.mode == 'eval':
        _eval()
    elif args.mode == 'eval_prediction':
        _eval_pred() #TODO
    elif args.mode == 'test':
        _test()
    elif args.mode == 'predict':
        print("INFERENCIA")
        _predict()
    elif args.mode == 'requests':
        _requests()
    else:
        raise Exception("Mode not in ['train', 'eval', 'predict', 'eval_prediction'], e.g. 'python spert.py train ...'")
