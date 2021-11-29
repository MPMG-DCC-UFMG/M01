
#!/bin/sh

dataset=$1
fold=$2
lang=$3

model="bert-base-cased"

if [ $lang == "pt" ]
then
    model="neuralmind/bert-base-portuguese-cased"
fi


echo "[1]"
echo "label = $dataset"
echo "model_type = spert"
echo "model_path = $model"
echo "tokenizer_path = $model"
echo "train_path = data/datasets/$dataset/train$fold.json"
echo "valid_path = data/datasets/$dataset/test$fold.json"
echo "types_path = data/datasets/$dataset/types.json"
echo "train_batch_size = 8"
echo "eval_batch_size = 1"
echo "neg_entity_count = 100"
echo "neg_relation_count = 100"
echo "epochs = 20"
echo "lr = 5e-5"
echo "lr_warmup = 0.1"
echo "weight_decay = 0.01"
echo "max_grad_norm = 1.0"
echo "rel_filter_threshold = 0.4"
echo "size_embedding = 32"
echo "prop_drop = 0.1"
echo "max_span_size = 32"
echo "store_predictions = true"
echo "store_examples = true"
echo "sampling_processes = 4"
echo "max_pairs = 128"
#echo "no_overlapping = true"
echo "final_eval = true"
echo "log_path = data/log/"
echo "save_path = data/save/"


