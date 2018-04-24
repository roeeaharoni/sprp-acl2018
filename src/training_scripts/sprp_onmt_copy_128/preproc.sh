#!/usr/bin/env bash

base_path=/home/nlp/aharonr6/

python $base_path/git/OpenNMT-py/preprocess.py \
-train_src $base_path/git/Split-and-Rephrase/baseline-seq2seq/train.complex \
-train_tgt $base_path/git/Split-and-Rephrase/baseline-seq2seq/train.simple \
-valid_src $base_path/git/Split-and-Rephrase/baseline-seq2seq/validation.complex \
-valid_tgt $base_path/git/Split-and-Rephrase/baseline-seq2seq/validation.simple \
-save_data $base_path/git/Split-and-Rephrase/baseline-seq2seq/baseline \
-src_seq_length 10000 \
-tgt_seq_length 10000 \
-src_seq_length_trunc 999 \
-tgt_seq_length_trunc 999 \
-dynamic_dict \
-share_vocab
