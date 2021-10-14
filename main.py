import argparse

from args import train_argparser, eval_argparser, predict_argparser
from config_reader import process_configs
from spert import input_reader
from spert.spert_trainer import SpERTTrainer
from regex_ner import RegexNER
from ..preprocessing.text_cleaner import merge_sentences

import spacy

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


def __eval(run_args):
    trainer = SpERTTrainer(run_args)
    trainer.eval(dataset_path=run_args.dataset_path, types_path=run_args.types_path,
                 input_reader_cls=input_reader.JsonInputReader)


def _predict():
    arg_parser = predict_argparser()
    process_configs(target=__predict_text, arg_parser=arg_parser)


def __predict_text(run_args):
#    trainer = SpERTTrainer(run_args)
    tokenizer = spacy.load("pt_core_news_sm")
#    regex_ner = RegexNER("../rules.tsv")
    
#    trainer.predict(dataset_path=run_args.dataset_path, types_path=run_args.types_path,
#                    input_reader_cls=input_reader.JsonPredictionInputReader)


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
    elif args.mode == 'predict':
        _predict()
    else:
        raise Exception("Mode not in ['train', 'eval', 'predict'], e.g. 'python spert.py train ...'")
