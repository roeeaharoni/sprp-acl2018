import json
import re
import os


# this script creates the evaluation directories for the new split, using the 'Split-RDFs-relations.json' file
# make sure the base_path variable is changed to point on the relevant directory
# it is based on the prepare-evaluation-directories script from the original "split and rephrase" repository

def process_sentdata(data, datasplit):
    
    data = data.strip().split("\n\n")
    
    complexsentdata = data[0].strip().split("\n")
    complexid = int(complexsentdata[0].split("-")[1].strip())
    print complexid
    
    simpsents = {}
    for item in data[1:]:
        if re.match('COMPLEX-'+str(complexid)+':MR-[0-9]*:SIMPLE-[0-9]*\n', item):
            # print item
            sents = (" ".join(item.strip().split("\n")[1:]))
            # .lower()
            # print sents
            if sents not in simpsents:
                simpsents[sents] = 1
    print len(simpsents)

    directory = ""
    if complexid in datasplit["TEST"]:
        # Test example
        directory = base_path + "/git/Split-and-Rephrase/evaluation-directories-RDFs-relations/test/" + str(complexid)
    else:
        if complexid in datasplit["VALIDATION"]:
            # Test example
            directory = base_path + "/git/Split-and-Rephrase/evaluation-directories-RDFs-relations/validation/" + str(complexid)
    #     directory = "evaluation-directories/test-lowercased/"+str(complexid)
        else:
            return


    # Build directory
    os.system("mkdir -p " + directory)
    count = 0
    for sents in simpsents:
        fopen = open(directory+"/reference"+str(count), "w")
        fopen.write(sents+"\n")
        fopen.close()
        count += 1

if __name__ == "__main__":

    base_path = '/home/nlp/aharonr6/'

    with open(base_path + '/git/Split-and-Rephrase/benchmark/Split-RDFs-relations.json') as data_file:
        datasplit = json.load(data_file)
        
    print len(datasplit["TEST"]), len(datasplit["VALIDATION"]), len(datasplit["TRAIN"])
    
    # Parse Simplification-Full Pairs    
    with open(base_path + "/git/Split-and-Rephrase/benchmark/final-complexsimple-meanpreserve-intreeorder-full.txt") as f:
        
        sentdata = []

        for line in f:
            if len(sentdata) == 0:
                sentdata.append(line)
            else:
                if re.match('COMPLEX-[0-9]*\n', line):
                    process_sentdata("".join(sentdata), datasplit)

                    print line
                    sentdata = [line]
                else:
                    sentdata.append(line)
            
        # Process last sentdata
        process_sentdata("".join(sentdata), datasplit)
    
