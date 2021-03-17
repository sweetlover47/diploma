import math
import multiprocessing

import lxml.etree as etree
from joblib import Parallel, delayed

poses = ['A', 'N', 'V']

def create_synsets_dict(a, n, v):
    synsets_dict = {'A': dict(), 'N': dict(), 'V': dict()}
    words_dict = {'A': dict(), 'N': dict(), 'V': dict()}
    for pos in poses:
        l = []
        if pos == 'A':
            l = a
        elif pos == 'N':
            l = n
        elif pos == 'V':
            l = v
        synset_str = 'rwn\\synsets.' + pos + '.xml'
        sense_str = 'rwn\\senses.' + pos + '.xml'
        tree = etree.parse(sense_str)
        root = tree.getroot()
        for node in l:
            entries = tree.xpath("//sense[@name='" + node.key.upper() + "']")
            for entry in entries:
                synset_id = entry.attrib['synset_id']
                word = entry.attrib['name']
                if not synset_id in synsets_dict[pos]:
                    synsets_dict[pos][synset_id] = []
                synsets_dict[pos][synset_id].append(word)
                if not word in words_dict[pos]:
                    words_dict[pos][word] = []
                words_dict[pos][word].append(synset_id)
                # print(word + '\t' + synset_id)
    return synsets_dict


def find_synonyms_for_table_slice(params, synsets_list, synsets_dict, synsets_table):
    _pos = params['pos']
    synset_relat = 'rwn\\synset_relations.' + _pos + '.xml'
    tree = etree.parse(synset_relat)
    root = tree.getroot()
    print(root)
    for i in range(params['start'], params['end']):
        for j in range(i, params['end']):
            entries = tree.xpath(
                "//relation[@parent_id='" + synsets_list[_pos][i] + "'][@child_id='" + synsets_list[_pos][
                    j] + "'][@name='hyponym']")
            if len(entries) == 0:
                continue
            if synsets_dict[_pos][synsets_list[_pos][i]] == synsets_dict[_pos][synsets_list[_pos][j]]:
                continue
            smrt = etree.parse('rwn\\derived_from.xml')
            smrt_entries = smrt.xpath("sense[@synset_id='" + synsets_list[_pos][i] + "']/derived_from/*")
            is_contains = False
            for e in smrt_entries:
                if e.attrib['synset_id'] == synsets_list[_pos][j]:
                    print(synsets_list[_pos][i], '   ', synsets_list[_pos][j])
                    is_contains = True
                    break
            if is_contains:
                continue
            synsets_table[i][j] = 1
    return synsets_table


def parallel_fill_synonym_table(synsets_list, synsets_dict, synsets_table):
    core_num = multiprocessing.cpu_count()
    for pos in poses:
        params = []
        for i in range(core_num):
            tmp = {
                'pos': pos,
                'start': math.ceil(len(synsets_list[pos]) * i / core_num),
                'end': math.ceil(len(synsets_list[pos]) * (i + 1) / core_num)
            }
            params.append(tmp)
        print(params)
        [t1, t2, t3, t4] = Parallel(n_jobs=core_num)(
            delayed(find_synonyms_for_table_slice)(params[_pos], synsets_list, synsets_dict, synsets_table[pos]) for _pos in range(core_num))

        for i in range(len(synsets_list[pos])):
            for j in range(i, len(synsets_list[pos])):
                if t1[i][j] + t2[i][j] + t3[i][j] + t4[i][j] == 1:
                    synsets_table[pos][i][j] = 1


def construct_synset_objects(voc):
    [a, n, v] = voc.get_synsets_by_tag()

    synsets_dict = create_synsets_dict(a, n, v)

    synsets_list = {
        'A': [*synsets_dict['A']],
        'N': [*synsets_dict['N']],
        'V': [*synsets_dict['V']]
    }

    synsets_table = dict()
    synsets_table['A'] = [[0 for x in range(len(synsets_list['A']))] for x in range(len(synsets_list['A']))]
    synsets_table['N'] = [[0 for x in range(len(synsets_list['N']))] for x in range(len(synsets_list['N']))]
    synsets_table['V'] = [[0 for x in range(len(synsets_list['V']))] for x in range(len(synsets_list['V']))]

    parallel_fill_synonym_table(synsets_list, synsets_dict, synsets_table)

    return synsets_list, synsets_dict, synsets_table


def construct_relations(synsets_list, synsets_dict, synsets_table):
    relation_nodes = []
    for pos in poses:
        name_list = synsets_list[pos]
        for i in range(len(synsets_list[pos])):
            relations_i = []
            synset_id_i = name_list[i]
            word_i = synsets_dict[pos][synset_id_i]
            for j in range(i, len(synsets_list[pos])):
                if (synsets_table[pos][i][j] != 0):
                    synset_id_j = name_list[j]
                    word_j = synsets_dict[pos][synset_id_j]
                    if len(relations_i) == 0:
                        relations_i.append(word_i[0])
                    if not word_j[0] in relations_i:
                        relations_i.append(word_j[0])
            if len(relations_i) != 0:
                relation_nodes.append(relations_i)
    return relation_nodes
