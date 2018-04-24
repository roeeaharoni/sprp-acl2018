import codecs
import re
import os
import spacy
import uuid


# perform sentence level evaluation against multiple references for each predicted sentence and average scores
def evaluate_avg_concat_bleu(moses_path, sent_ids_file_path, predicted_sents_dir_path, predicted_sents_file_path,
                             ref_dirs_path_prefix):
    nlp = spacy.load('en')
    bleu_scores = []
    tokens_per_sent = []
    simple_sent_amount = 0

    # read each sent from test sents
    with codecs.open(predicted_sents_file_path, 'r', 'utf8') as predicted_sents:
        with codecs.open(sent_ids_file_path, 'r', 'utf8') as source_test_sent_ids:
            predicted_text = predicted_sents.readline()
            id = source_test_sent_ids.readline()
            while predicted_text:
                predicted_text = predicted_text.strip()

                # split sentences with spacy - only for counting amount of simple sentences per complex
                if len(predicted_text) > 0:
                    tokens = nlp(predicted_text)
                    sub_sents = [s.text for s in tokens.sents]
                else:
                    print 'EMPTY PREDICTION! id:{}'.format(id)
                    sub_sents = ['']

                non_empty = []
                for sub in sub_sents:
                    if len(sub.strip()) > 2:
                        non_empty.append(sub)

                sub_sents_amount = len(non_empty)
                simple_sent_amount += sub_sents_amount
                id = id.strip()
                sent_file_path = predicted_sents_dir_path + '{}.txt'.format(id)
                tokens_per_sent.append(len(predicted_text.split()))

                # write each sentence to a separate file to allow computing sentence level bleu
                with codecs.open(sent_file_path, 'w', 'utf8') as sent_file:
                    sent_file.write(predicted_text.strip() + '\n')

                test_dir_path = ref_dirs_path_prefix + id + '/reference'

                # compute sentence level bleu vs test dir
                bleu_str = multi_bleu(moses_path, test_dir_path, sent_file_path, lowercase=False)
                bleu_re = re.match(r'BLEU = ([0-9]*\.?[0-9]*), ', bleu_str)
                if bleu_re:
                    bleu_score = float(bleu_re.group(1))
                else:
                    bleu_score = 0
                bleu_scores.append(bleu_score)

                # read next sent
                predicted_text = predicted_sents.readline()

                # read next id from ids file
                id = source_test_sent_ids.readline()

    # average sent level bleu scores across the test set
    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    avg_tokens_per_sent = float(sum(tokens_per_sent)) / simple_sent_amount
    avg_simple_sents_per_complex = float(simple_sent_amount)/len(bleu_scores)
    return avg_bleu, avg_tokens_per_sent, avg_simple_sents_per_complex


# compute bleu using the moses multi-bleu script
def multi_bleu(moses_path, ref_path, output_path, lowercase=False):
    op_id = str(uuid.uuid4())
    tmp_file = '{}_{}.bleu'.format(output_path, op_id)
    if lowercase:
        lc = '-lc'
    else:
        lc = ''
    bleu_command = "{}/scripts/generic/multi-bleu.perl {} {} < {} > {}".format(
         moses_path, lc, ref_path, output_path, tmp_file)

    os.system(bleu_command)

    bleu_str = codecs.open(tmp_file, 'r', 'utf-8').read()

    os.system('rm {}'.format(tmp_file))
    return bleu_str