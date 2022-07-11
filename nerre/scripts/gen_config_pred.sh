
#!/bin/sh

dataset=$1
fold=$2

echo "[1]"
echo "model_type = spert"
echo "model_path = data/save/$dataset/final_model"
echo "tokenizer_path = data/save/$dataset/final_model"
echo "dataset_path = data/datasets/$dataset/test$fold.json"
echo "types_path = data/datasets/$dataset/types.json"
echo "predictions_path = data/datasets/$dataset/predictions$fold.json"
echo "eval_batch_size = 1"
echo "rel_filter_threshold = 0.4"
echo "size_embedding = 32"
echo "prop_drop = 0.1"
echo "max_span_size = 32"
#echo "no_overlapping = true"
echo "sampling_processes = 4"
echo "max_pairs = 128"

