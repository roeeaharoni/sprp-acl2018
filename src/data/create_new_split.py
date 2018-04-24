from src import tools
from src.preprocessing import tree_plans
import codecs
import os
from collections import defaultdict
import re
import json
import random

# directory containing the current github repository
base_path = '/home/nlp/aharonr6'

# directory containing the split and rephrase github repository
sprp_root = "/home/nlp/aharonr6"

def main():

    # split the raw data according to RDFs. will create a json file containing the example ids for the new split
    split_data()

    # create the files for training and evaluating a seq2seq model, according to the new split
    os.system('python {}/sprp/src/split_and_rephrase/prepare-baseline-data-RDFs-relations.py'.format(base_path))
    os.system('python {}/sprp/src/split_and_rephrase/prepare-evaluation-directories-RDFs-relations.py'.format(
        base_path))

    return


def split_data():

    # read the raw data file, parse it, create a new data split according to entities/domains
    complex_counter = 0
    raw_data_file_path = "{}/Split-and-Rephrase/benchmark/final-complexsimple-meanpreserve-intreeorder-full.txt".format(sprp_root)
    group_to_sent_ids = defaultdict(set)
    group_to_rdfs = defaultdict(set)
    domain_to_sent_ids = defaultdict(set)
    entity_to_sent_id = defaultdict(set)
    relation_to_sent_id = defaultdict(set)
    domain_triples2eids2rdfs, all_entities_distinct, all_relations_distinct = parse_RDF_xmls()
    group_counter = 0
    complex_sents = []

    # go through the raw data in final-complexsimple-meanpreserve-intreeorder-full.txt
    with open(raw_data_file_path) as f:
        line = f.readline()
        while line:
            # if complex sentence
            if re.match('COMPLEX-[0-9]*\n', line):
                complex_counter += 1
                if complex_counter % 100 == 0:
                    print 'went through {} complex sents'.format(complex_counter)
                sentence_id = int(line.split("-")[1].strip())
                complex_sent = f.readline()
                complex_sents.append(complex_sent.strip())

                # read two blank rows
                f.readline()
                f.readline()

                # read and parse code row, for example: "category=WrittenWork eid=Id26 size=1"
                category_RDF_id = f.readline()
                split = category_RDF_id.split()
                sent_domain = split[0].split('=')[1].strip()
                sent_eid = split[1].split('=')[1].strip()
                sent_triples_amount = split[2].split('=')[1].strip()
                domain_to_sent_ids[sent_domain].add(sentence_id)

                # get the RDFs of the sentence using the xml file
                RDF_triples_in_sent = domain_triples2eids2rdfs[sent_domain + '_' + sent_triples_amount][sent_eid]
                for rdf in RDF_triples_in_sent:
                    entity_to_sent_id[rdf[0]].add(sentence_id)
                    relation_to_sent_id[rdf[1]].add(sentence_id)
                    entity_to_sent_id[rdf[2]].add(sentence_id)


                # check if any of the entities are already in a group
                candidate_groups = set()
                for g in group_to_rdfs:
                    for rdf in RDF_triples_in_sent:
                        rdf_str = '_'.join(rdf)
                        if rdf_str in group_to_rdfs[g]:
                            candidate_groups.add(g)

                # if they are in one group - add the sentence there
                if len(candidate_groups) == 1:
                    chosen_group = list(candidate_groups)[0]

                # if they are in more than one group - merge the groups and add the sentence there
                if len(candidate_groups) > 1:
                    candidate_groups_list = list(candidate_groups)
                    chosen_group = candidate_groups_list[0]

                    # merge rdfs
                    for g in candidate_groups_list[1:]:
                        for e in group_to_rdfs[g]:
                            group_to_rdfs[chosen_group].add(e)
                        del group_to_rdfs[g]

                    # merge sentences
                    for g in candidate_groups_list[1:]:
                        for s in group_to_sent_ids[g]:
                            group_to_sent_ids[chosen_group].add(s)
                        del group_to_sent_ids[g]

                # if they are in no group - create a new group and add the sentence there
                if len(candidate_groups) == 0:
                    chosen_group = 'group_{}'.format(group_counter)
                    group_counter += 1

                # add sent id and entities to chosen group
                group_to_sent_ids[chosen_group].add(sentence_id)
                for rdf in RDF_triples_in_sent:
                    rdf_str = '_'.join(rdf)
                    group_to_rdfs[chosen_group].add(rdf_str)

                # read the next line
                line = f.readline()
            else:
                line = f.readline()
    print 'formed {} groups'.format(len(group_to_rdfs))
    for g in group_to_rdfs:
        print 'group {}: {} sents, {} RDFs'.format(g, len(group_to_rdfs[g]), len(group_to_sent_ids[g]))
    print 'avg sents per group: {}'.format(sum([len(group_to_sent_ids[g]) for g in group_to_sent_ids])/
                                           len(group_to_sent_ids))

    print 'complex counter: {}'.format(complex_counter)
    print 'allocated sentences in groups: {}'.format(sum([len(group_to_sent_ids[g]) for g in group_to_sent_ids]))
    print 'complex sents: {}'.format(len(complex_sents))
    print 'distinct complex sents: {}'.format(len(set(complex_sents)))

    # create relation_based_split
    print '\n\ncreating rdf-relation split...'
    random.seed(777)
    choices = ['TRAIN', 'VALIDATION', 'TEST']
    RDFs_relations_split = defaultdict(list)
    relation_to_groups = defaultdict(set)
    allocated_groups = set()

    # go through each relation
    for relation in relation_to_sent_id:

        # map relations to groups
        for group in group_to_sent_ids:
            if len(relation_to_sent_id[relation].intersection(group_to_sent_ids[group])) > 0:
                relation_to_groups[relation].add(group)

    # go through each relation, make sure at least one is in train
    for relation in relation_to_groups:
        # check if its already covered
        covered = False
        for group in relation_to_groups[relation]:
            if group in allocated_groups:
                covered = True
                break

        # not covered, add random group
        if not covered:
            choice = random.choice(list(relation_to_groups[relation]))
            RDFs_relations_split['TRAIN'] += group_to_sent_ids[choice]
            allocated_groups.add(choice)

    # and the rest randomly
    for group in group_to_sent_ids:
        if group not in allocated_groups:
            if len(group_to_sent_ids[group]) > 100:
                choice = 'TRAIN'
            else:
                choice = random.choice(choices)
            RDFs_relations_split[choice] += group_to_sent_ids[group]
            allocated_groups.add(group)

            # make sure the dev and test are not too large
            if len(RDFs_relations_split['VALIDATION']) > 500 and 'VALIDATION' in choices:
                choices.remove('VALIDATION')
            if len(RDFs_relations_split['TEST']) > 500 and 'TEST' in choices:
                choices.remove('TEST')

    # create json file with sent ids
    with codecs.open(base_path + '/git/Split-and-Rephrase/benchmark/Split-RDFs-relations.json', 'w',
                     'utf8') as fp:
        json.dump(RDFs_relations_split, fp)

    # create text files with sent ids
    for s in ['train', 'validation', 'test']:
        codecs.open(base_path + '/git/Split-and-Rephrase/benchmark/complex-sents/{}-rdfs-relations.id'.format(s), 'w',
                    'utf8').writelines(
            [str(n) + '\n' for n in sorted(RDFs_relations_split[s.upper()])]
        )

    # relations split stats
    print 'RDFs_relations split:'
    for s in RDFs_relations_split:
        print '{} has {} sents'.format(s, len(RDFs_relations_split[s]))

    relations_split_stats(RDFs_relations_split, relation_to_sent_id)

    entities_split_stats(RDFs_relations_split, entity_to_sent_id)

    return


def relations_split_stats(data_split, relation_to_sent_id):
    dev_relations = 0
    test_relations = 0
    test_relations_in_train = 0
    dev_relations_in_train = 0
    for relation in relation_to_sent_id:
        count_train = 0
        count_dev = 0
        count_test = 0
        for sent_id in relation_to_sent_id[relation]:
            if sent_id in data_split['VALIDATION']:
                count_dev += 1

            if sent_id in data_split['TRAIN']:
                count_train += 1

            if sent_id in data_split['TEST']:
                count_test += 1

        if count_dev > 0 and count_train > 0:
            dev_relations_in_train += 1
        if count_dev > 0:
            dev_relations += 1

        if count_test > 0 and count_train > 0:
            test_relations_in_train += 1
        if count_test > 0:
            test_relations += 1
    print '{} dev relations in train out of {} ({}%)'.format(dev_relations_in_train, dev_relations,
                                                             float(dev_relations_in_train) / dev_relations * 100)
    print '{} test relations in train out of {} ({}%)'.format(test_relations_in_train, test_relations,
                                                              float(test_relations_in_train) / test_relations * 100)


def entities_split_stats(data_split, entity_to_sent_id):
    dev_entities_in_train = 0
    test_entities_in_train = 0
    dev_entities = 0
    test_entities = 0
    for e in entity_to_sent_id:
        count_train = 0
        count_dev = 0
        count_test = 0
        for sent_id in entity_to_sent_id[e]:
            if sent_id in data_split['VALIDATION']:
                count_dev += 1

            if sent_id in data_split['TRAIN']:
                count_train += 1

            if sent_id in data_split['TEST']:
                count_test += 1

        if count_dev > 0 and count_train > 0:
            dev_entities_in_train += 1
        if count_dev > 0:
            dev_entities += 1

        if count_test > 0 and count_train > 0:
            test_entities_in_train += 1
        if count_test > 0:
            test_entities += 1
    print '{} dev entities in train out of {} ({}%)'.format(dev_entities_in_train, dev_entities,
                                                            float(dev_entities_in_train) / dev_entities * 100)
    print '{} test entities in train out of {} ({}%)'.format(test_entities_in_train, test_entities,
                                                             float(test_entities_in_train) / test_entities * 100)


def parse_RDF_xmls():

    # return a dictionary from triples+domain to eids to RDFs
    domain_triples2eids2rdfs = defaultdict(dict)
    all_entities = []
    all_relations = []

    domains = ['Building', 'WrittenWork', 'Astronaut', 'SportsTeam', 'Monument', 'University']
    raw_dirs_path_format = base_path + '/git/Split-and-Rephrase/benchmark/benchmark_verified_simplifcation/{}triples/'
    for triples in range(1,8):

        # loop through files
        xml_files = os.listdir(raw_dirs_path_format.format(triples))
        for file_path in xml_files:

            current_domain = [d for d in domains if d in file_path][0]
            xml_id = current_domain + '_' + str(triples)

            # open xml file, read all rows
            rows = codecs.open(raw_dirs_path_format.format(triples) + file_path).readlines()
            for row in rows:
                if 'eid=' in row:
                    current_eid = row.split()[2].split('=')[1].replace("\"","").strip()
                if '<mtriple>' in row:
                    rdf_parts = row.strip().replace('<mtriple>','').replace('</mtriple>','').strip().split('|')
                    rdf_parts = [item.strip() for item in rdf_parts]
                    if current_eid not in domain_triples2eids2rdfs[current_domain + '_' + str(triples)]:
                        domain_triples2eids2rdfs[xml_id][current_eid] = []
                    domain_triples2eids2rdfs[xml_id][current_eid].append(rdf_parts)
                    all_entities.append(rdf_parts[0])
                    all_relations.append(rdf_parts[1])
                    all_entities.append(rdf_parts[2])

    return domain_triples2eids2rdfs, set(all_entities), set(all_relations)


if __name__ == '__main__':
    main()