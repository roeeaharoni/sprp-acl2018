from src import evaluate
import os
import codecs

def main():

    # run dev evaluation on all checkpoints to choose the best model for test
    model_name = 'sprp_onmt_copy_512'

    base_path = '/home/nlp/aharonr6'

    moses_path = base_path + '/git/mosesdecoder'

    models = ['sprp_copy_attn_acc_85.43_ppl_2.02_e1.pt',
              'sprp_copy_attn_acc_85.83_ppl_1.96_e2.pt',
              'sprp_copy_attn_acc_86.47_ppl_1.85_e3.pt',
              'sprp_copy_attn_acc_85.95_ppl_2.02_e4.pt',
              'sprp_copy_attn_acc_87.00_ppl_2.11_e5.pt',
              'sprp_copy_attn_acc_86.98_ppl_2.16_e6.pt',
              'sprp_copy_attn_acc_87.23_ppl_2.17_e7.pt',
              'sprp_copy_attn_acc_87.33_ppl_2.20_e8.pt',
              'sprp_copy_attn_acc_87.38_ppl_2.21_e9.pt',
              'sprp_copy_attn_acc_87.35_ppl_2.22_e10.pt',
              'sprp_copy_attn_acc_87.35_ppl_2.24_e11.pt',
              'sprp_copy_attn_acc_87.34_ppl_2.23_e12.pt',
              'sprp_copy_attn_acc_87.34_ppl_2.24_e13.pt',
              'sprp_copy_attn_acc_87.36_ppl_2.24_e14.pt',
              'sprp_copy_attn_acc_87.35_ppl_2.24_e15.pt']

    test_dirs_path_prefix = base_path + '/git/Split-and-Rephrase/evaluation-directories/validation/'

    # the file containing the ids of the test sentences
    test_sent_ids_path = base_path + '/git/Split-and-Rephrase/benchmark/complex-sents/validation.id'

    # a directory that will hold single sentence files for the hypotheses
    test_hypothesis_sents_dir = base_path + '/git/phrasing/models/{}/validation_complex_output_sents/'.format(
        model_name)

    if not os.path.exists(test_hypothesis_sents_dir):
        os.mkdir(test_hypothesis_sents_dir)

    results_file_path = base_path + '/git/phrasing/models/{}/overtime_dev_sprp_eval.txt'.format(
        model_name)

    results_file = codecs.open(results_file_path, 'w','utf8')

    for model in models:
        command = 'python {}/git/forks/OpenNMT-py/translate.py \
                    -gpu 1 \
                    -batch_size 1 \
                    -model {}/git/phrasing/models/{}/{} \
                    -src {}/git/Split-and-Rephrase/baseline-seq2seq/validation.complex.unique \
                    -output {}/git/phrasing/models/{}/validation.complex.unique.output \
                    -beam_size 12 \
                    -verbose \
                    -attn_debug \
                    -replace_unk'

        os.system(command.format(base_path, base_path, model_name, model, base_path, base_path, model_name))

        test_target = base_path + '/git/phrasing/models/{}/validation.complex.unique.output'.format(model_name)

        print 'starting multi-ref evaluation...'
        avg_bleu, avg_tokens_per_sent, avg_simple_sents_per_complex = evaluate.evaluate_avg_concat_bleu(moses_path,
                                                                                                        test_sent_ids_path,
                                                                                                        test_hypothesis_sents_dir,
                                                                                                        test_target,
                                                                                                        test_dirs_path_prefix,
                                                                                                        splitter='. ')

        results_file.write('{}\t{}\t{}\t{}\n'.format(model, avg_bleu, avg_tokens_per_sent,
                                                                     avg_simple_sents_per_complex))
    return

if __name__ == '__main__':
    main()