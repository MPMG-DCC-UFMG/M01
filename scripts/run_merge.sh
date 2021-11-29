
#!/bin/sh

dataset=$1
lang=$2

for fold in `seq 0 9`
do
    #scripts/gen_config_train.sh $dataset $fold $lang > configs/train.conf
    #venv/bin/python spert.py train --config configs/train.conf

    #scripts/gen_config_pred.sh $dataset $fold > configs/pred.conf
    #venv/bin/python spert.py predict --config configs/pred.conf


    python postprocessing/merge_spans_score.py data/datasets/$dataset/predictions$fold.json data/datasets/$dataset/predictions_merged$fold.json

    python spert/json_evaluator.py data/datasets/$dataset/predictions_merged$fold.json data/datasets/$dataset/test$fold.json > data/datasets/$dataset/merged_eval$fold

    python spert/json_evaluator_no_overlap.py data/datasets/$dataset/predictions_merged$fold.json data/datasets/$dataset/test$fold.json > data/datasets/$dataset/merged_no_overlap_eval$fold

done
