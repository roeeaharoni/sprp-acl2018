#!/usr/bin/env bash

base_path=/home/nlp/aharonr6/

model_name=sprp_onmt_baseline_256

python $base_path/git/OpenNMT-py/train.py \
-save_model $base_path/git/phrasing/models/${model_name}/${model_name} \
-data $base_path/git/Split-and-Rephrase/baseline-seq2seq/baseline \
-global_attention mlp \
-word_vec_size 256 \
-rnn_size 256 \
-layers 1 \
-encoder_type brnn \
-epochs 20 \
-seed 777 \
-batch_size 64 \
-max_grad_norm 2 \
-share_embeddings \
-gpuid 0 \
-start_checkpoint_at 1 \
-start_epoch 13 \
-train_from $base_path/git/phrasing/models/${model_name}/sprp_onmt_baseline_256_acc_88.65_ppl_1.79_e12.pt


#-copy_attn \
#-copy_attn_force \

