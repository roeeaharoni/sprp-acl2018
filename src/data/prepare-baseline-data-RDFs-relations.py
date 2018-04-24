import random
import json
import re
import os

# this script creates the data directories for the new split, using the 'Split-RDFs-relations.json' file
# make sure the base_path variable is changed to point on the relevant directory
# it is based on the prepare-baseline-data script from the original "split and rephrase" repository

def process_sentdata_baseline(data, datasplit, 
                              f_src_s2s_train, f_src_s2s_val, f_src_s2s_test, 
                              f_trg_s2s_train, f_trg_s2s_val, f_trg_s2s_test,
                              f_src_s2smsrc_train, f_src_s2smsrc_val, f_src_s2smsrc_test,
                              f_srcsem_s2smsrc_train, f_srcsem_s2smsrc_val, f_srcsem_s2smsrc_test,
                              f_trg_s2smsrc_train, f_trg_s2smsrc_val, f_trg_s2smsrc_test):
    non_dot_end = 0
    data = data.strip().split("\n\n")
    
    complexsentdata = data[0].strip().split("\n")
    complexid = int(complexsentdata[0].split("-")[1].strip())
    complexsent = complexsentdata[1].strip()
    
    mr_dict = {}
    # Collect all complex mrs
    for item in data[1:]:
        if re.match('COMPLEX-'+str(complexid)+':MR-[0-9]*\n', item):
            # print item
            mrdata = item.strip().split("\n")
            mrid = mrdata[0]
            mr = mrdata[1]
            mr_dict[mrid] = [mr, {}]
    # print mr_dict
    
    simpsents = {}
    for item in data[1:]:
        if re.match('COMPLEX-'+str(complexid)+':MR-[0-9]*:SIMPLE-[0-9]*\n', item):
            # print item
            
            mrid = ":".join(item.strip().split("\n")[0].split(":")[:2])
            # print mrid

            sents = ("\n".join(item.strip().split("\n")[1:])).strip()
            sents_sep = item.strip().split("\n")[1:]
            for s in sents_sep:
                if s[-1] != '.':
                    print (s)

            
            if sents not in simpsents:
                simpsents[sents] = 1

            if sents not in mr_dict[mrid][1]:
                mr_dict[mrid][1][sents] = 1
                
    print (complexid, len(simpsents), len(mr_dict))

    # simpsents = {}
    # for item in data[1:]:
    #     if re.match('COMPLEX-'+str(complexid)+':MR-[0-9]*:SIMPLE-[0-9]*\n', item):
    #         # print item
    #         sents = ("\n".join(item.strip().split("\n")[1:])).strip()
    #         # print sents
    #         if sents not in simpsents:
    #             simpsents[sents] = 1
    # print complexid, len(simpsents)

    # splitter = " _SPLIT_ "
    splitter = " "
    if complexid in datasplit["TEST"]:
        # Test example
        for sents in simpsents:
            f_src_s2s_test.write(complexsent+"\n")
            f_trg_s2s_test.write(sents.replace("\n", splitter)+"\n")
            
        for mrid in mr_dict:
            mrcinfo = mr_dict[mrid][0]
            for sents in mr_dict[mrid][1]:
                f_src_s2smsrc_test.write(complexsent+"\n")
                f_srcsem_s2smsrc_test.write(mrcinfo+"\n")
                f_trg_s2smsrc_test.write(sents.replace("\n", splitter)+"\n")

    elif complexid in datasplit["VALIDATION"]:
        # Validation 
        for sents in simpsents:
            f_src_s2s_val.write(complexsent+"\n")
            f_trg_s2s_val.write(sents.replace("\n", splitter)+"\n")
            
        for mrid in mr_dict:
            mrcinfo = mr_dict[mrid][0]
            for sents in mr_dict[mrid][1]:
                f_src_s2smsrc_val.write(complexsent+"\n")
                f_srcsem_s2smsrc_val.write(mrcinfo+"\n")
                f_trg_s2smsrc_val.write(sents.replace("\n", splitter)+"\n")
    else:
        # Train
        for sents in simpsents:
            f_src_s2s_train.write(complexsent+"\n")
            f_trg_s2s_train.write(sents.replace("\n", splitter)+"\n")
            
        for mrid in mr_dict:
            mrcinfo = mr_dict[mrid][0]
            for sents in mr_dict[mrid][1]:
                f_src_s2smsrc_train.write(complexsent+"\n")
                f_srcsem_s2smsrc_train.write(mrcinfo+"\n")
                f_trg_s2smsrc_train.write(sents.replace("\n", splitter)+"\n")

    print (non_dot_end)
    print ('simple sents: {}'.format(len(simpsents)))

if __name__ == "__main__":
    # directory containing the Split-and-Rephrase github repository
    base_path = '/home/nlp/aharonr6/'

    # data directories (created if needed)
    seq2seq_split_dir_name = base_path + "/git/Split-and-Rephrase/baseline-seq2seq-RDFs-relations"
    seq2seq_multisrc_split_dir_name = base_path + "/git/Split-and-Rephrase/baseline-seq2seq-multisrc-RDFs-relations"
    
    os.system("mkdir -p {}".format(seq2seq_split_dir_name))
    os.system("mkdir -p {}".format(seq2seq_multisrc_split_dir_name))
    
    with open(base_path + '/git/Split-and-Rephrase/benchmark/Split-RDFs-relations.json') as data_file:
        datasplit = json.load(data_file)
        
    print (len(datasplit["TEST"]), len(datasplit["VALIDATION"]), len(datasplit["TRAIN"]))
    
    # Parse Simplification-Full Pairs and prepare baseline system
    f_src_s2s_train = open("{}/train.complex".format(seq2seq_split_dir_name), "w")
    f_src_s2s_val = open("{}/validation.complex".format(seq2seq_split_dir_name), "w")
    f_src_s2s_test = open("{}/test.complex".format(seq2seq_split_dir_name), "w")
    f_trg_s2s_train = open("{}/train.simple".format(seq2seq_split_dir_name), "w")
    f_trg_s2s_val = open("{}/validation.simple".format(seq2seq_split_dir_name), "w")
    f_trg_s2s_test = open("{}/test.simple".format(seq2seq_split_dir_name), "w")
    
    f_src_s2smsrc_train = open("{}/train.complex".format(seq2seq_multisrc_split_dir_name), "w")
    f_src_s2smsrc_val = open("{}/validation.complex".format(seq2seq_multisrc_split_dir_name), "w")
    f_src_s2smsrc_test = open("{}/test.complex".format(seq2seq_multisrc_split_dir_name), "w")
    f_srcsem_s2smsrc_train = open("{}/train.complex-semantics".format(seq2seq_multisrc_split_dir_name), "w")
    f_srcsem_s2smsrc_val = open("{}/validation.complex-semantics".format(seq2seq_multisrc_split_dir_name), "w")
    f_srcsem_s2smsrc_test = open("{}/test.complex-semantics".format(seq2seq_multisrc_split_dir_name), "w")
    f_trg_s2smsrc_train = open("{}/train.simple".format(seq2seq_multisrc_split_dir_name), "w")
    f_trg_s2smsrc_val = open("{}/validation.simple".format(seq2seq_multisrc_split_dir_name), "w")
    f_trg_s2smsrc_test = open("{}/test.simple".format(seq2seq_multisrc_split_dir_name), "w")

    with open(base_path + "/git/Split-and-Rephrase/benchmark/final-complexsimple-meanpreserve-intreeorder-full.txt") as f:
        
        sentdata = []

        for line in f:
            if len(sentdata) == 0:
                print (line)
                sentdata.append(line)
            else:
                if re.match('COMPLEX-[0-9]*\n', line):
                    process_sentdata_baseline("".join(sentdata), datasplit, 
                                              f_src_s2s_train, f_src_s2s_val, f_src_s2s_test, 
                                              f_trg_s2s_train, f_trg_s2s_val, f_trg_s2s_test, 
                                              f_src_s2smsrc_train, f_src_s2smsrc_val, f_src_s2smsrc_test,
                                              f_srcsem_s2smsrc_train, f_srcsem_s2smsrc_val, f_srcsem_s2smsrc_test,
                                              f_trg_s2smsrc_train, f_trg_s2smsrc_val, f_trg_s2smsrc_test)

                    print (line)
                    sentdata = [line]
                else:
                    sentdata.append(line)
            
        # Process last sentdata
        process_sentdata_baseline("".join(sentdata), datasplit, 
                                  f_src_s2s_train, f_src_s2s_val, f_src_s2s_test, 
                                  f_trg_s2s_train, f_trg_s2s_val, f_trg_s2s_test, 
                                  f_src_s2smsrc_train, f_src_s2smsrc_val, f_src_s2smsrc_test,
                                  f_srcsem_s2smsrc_train, f_srcsem_s2smsrc_val, f_srcsem_s2smsrc_test,
                                  f_trg_s2smsrc_train, f_trg_s2smsrc_val, f_trg_s2smsrc_test)
        
    f_src_s2s_train.close()
    f_src_s2s_val.close()
    f_src_s2s_test.close()
    f_trg_s2s_train.close()
    f_trg_s2s_val.close()
    f_trg_s2s_test.close()
    
    f_src_s2smsrc_train.close()
    f_src_s2smsrc_val.close()
    f_src_s2smsrc_test.close()
    f_srcsem_s2smsrc_train.close()
    f_srcsem_s2smsrc_val.close()
    f_srcsem_s2smsrc_test.close() 
    f_trg_s2smsrc_train.close()
    f_trg_s2smsrc_val.close()
    f_trg_s2smsrc_test.close()

    os.system('cat {}/validation.complex | uniq > \
    {}/validation.complex.unique'.format(seq2seq_split_dir_name, seq2seq_split_dir_name))

    os.system('cat {}/test.complex | uniq > \
        {}/test.complex.unique'.format(seq2seq_split_dir_name, seq2seq_split_dir_name))

    print ('done')


