#!/usr/bin/env bash

base_path=/home/nlp/aharonr6/

model_name=sprp_onmt_baseline_512

model_file=sprp_onmt_baseline_512_acc_88.95_ppl_2.02_e11.pt
#model_file=sprp_onmt_baseline_512_acc_88.95_ppl_2.03_e21.pt

python $base_path/git/forks/OpenNMT-py/translate.py \
-gpu 1 \
-batch_size 1 \
-model $base_path/git/phrasing/models/${model_name}/${model_file} \
-src $base_path/git/Split-and-Rephrase/baseline-seq2seq/test.complex.unique \
-output $base_path/git/phrasing/models/${model_name}/test.complex.unique.output \
-beam_size 12 \
-replace_unk

python ${base_path}/git/phrasing/src/nmt_scripts/opennmt-py/${model_name}/test.py



