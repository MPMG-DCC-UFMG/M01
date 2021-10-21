#!/usr/bin/env bash
curr_dir=$(pwd)

mkdir -p data
mkdir -p data/datasets

wget -r -nH --cut-dirs=100 --reject "index.html*" --no-check-certificate --no-parent http://homepages.dcc.ufmg.br/~fmuniz/data/datasets/domg_clean/ -P ${curr_dir}/data/datasets/domg_clean

wget -r -nH --cut-dirs=100 --reject "index.html*" --no-check-certificate --no-parent http://homepages.dcc.ufmg.br/~fmuniz/data/datasets/domg_clean_regex_marked/ -P ${curr_dir}/data/datasets/domg_clean_regex_marked

wget -r -nH --cut-dirs=100 --reject "index.html*" --no-check-certificate --no-parent http://homepages.dcc.ufmg.br/~fmuniz/data/datasets/domg_v1/ -P ${curr_dir}/data/datasets/domg_v1


