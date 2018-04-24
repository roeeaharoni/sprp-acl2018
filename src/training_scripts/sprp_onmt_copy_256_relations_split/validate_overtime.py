from src import evaluate
import os
import codecs
import glob

def main():
    model_name = 'sprp_onmt_copy_256_relations_split'

    base_path = '/home/nlp/aharonr6'

    moses_path = base_path + '/git/mosesdecoder'

    model_files = filter(os.path.isfile, glob.glob(base_path + '/git/phrasing/models/{}/*.pt'.format(model_name)))
    model_files.sort(key=lambda x: os.path.getmtime(x))

    test_dirs_path_prefix = base_path + '/git/Split-and-Rephrase/evaluation-directories-RDFs-relations/validation/'

    # the file containing the ids of the test sentences
    test_sent_ids_path = base_path + '/git/Split-and-Rephrase/benchmark/complex-sents/validation-rdfs-relations.id'

    # a directory that will hold single sentence files for the hypotheses
    test_hypothesis_sents_dir = base_path + '/git/phrasing/models/{}/validation_complex_output_sents/'.format(
        model_name)

    if not os.path.exists(test_hypothesis_sents_dir):
        os.mkdir(test_hypothesis_sents_dir)

    results_file_path = base_path + '/git/phrasing/models/{}/overtime_dev_sprp_eval.txt'.format(model_name)

    results_file = codecs.open(results_file_path, 'w','utf8')

    for model in model_files:
        command = 'python {}/git/forks/OpenNMT-py/translate.py \
                    -gpu 3 \
                    -batch_size 1 \
                    -model {} \
                    -src {}/git/Split-and-Rephrase/baseline-seq2seq-RDFs-relations/validation.complex.unique \
                    -output {}/git/phrasing/models/{}/validation.complex.unique.output \
                    -beam_size 12 \
                    -verbose \
                    -attn_debug \
                    -replace_unk'

        os.system(command.format(base_path, model, base_path, base_path, model_name))

        test_target = base_path + '/git/phrasing/models/{}/validation.complex.unique.output'.format(model_name)

        print 'starting multi-ref evaluation...'
        avg_bleu, avg_tokens_per_sent, avg_simple_sents_per_complex = evaluate.evaluate_avg_concat_bleu(moses_path,
                                                                                                        test_sent_ids_path,
                                                                                                        test_hypothesis_sents_dir,
                                                                                                        test_target,
                                                                                                        test_dirs_path_prefix)

        results_file.write('{}\t{}\t{}\t{}\n'.format(model, avg_bleu, avg_tokens_per_sent,
                                                                     avg_simple_sents_per_complex))
    return

if __name__ == '__main__':
    main()