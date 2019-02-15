**Data and source code accompanying the paper "Split and Rephrase: Better Evaluation and a Stronger Baseline".**

https://arxiv.org/abs/1805.01035

Roee Aharoni and Yoav Goldberg, ACL 2018 

The data and some of the scripts are based on the repository by Narayan et al.: https://github.com/shashiongithub/Split-and-Rephrase

This repository includes: 

- The proposed data split, under `data/baseline-seq2seq-split-RDFs-relations.zip`.

- The original data split, under `data/baseline-seq2seq.zip`.

- The raw sentences and .id files required in the `test.py` and `validate.py` scripts, under `data/complex-sents.zip`.
  
  - Additional files required by the `test.py` and `validate.py` scripts of our models (i.e. `.../benchmark/...` and `.../evaluation-directories.../...` are available [here](https://drive.google.com/open?id=1KagOaUv1hlAK8ONYiyH6rXJHjGANk8Qj).

- Scripts for: 

  - Training our proposed models using openNMT-py (under `src/training_scripts`)

  - Evaluating the models as proposed by Narayan et al., 2017 (under `src/evaluate.py`)

  - Creating the RDF-based data split to reduce overlap between the development and test set found in the original split (under `src/data/create_new_split.py`)

Prerequisits:

- PyTorch

- openNMT-py

Feel free to reach out in `roee.aharoni@gmail.com` if you have any further questions! 
