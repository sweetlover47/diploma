import random
from itertools import islice

import lxml.etree as etree

import modules.search.vocabulary as vc
from modules.search.word_form_package.word_form import WORD_FORM_RED_WORD_DISTANCE

INCORRECT_SYNONYMS = []
MAIN_WORD = None


# word-form: for each pair key-value construct graph of distance between positions and sort by asc if starts from the
# end words on first positions in list, which distanced from others > RED_DISTANCE, it stayed the same when distances
# started be <= RED_DISTANCE, need to correct mistake
# TODO: искать синонимы в сенсах медведь: мишка, топтыгин. При этом сохранить код для возможной хитрости
def find_synonyms_for_correct_mistake(word):
    voc = vc.build_vocabulary(word)
    pos = voc.get_node_by_key(word).tag
    sense_xml = 'rwn\\senses.' + pos + '.xml'
    sen_tree = etree.parse(sense_xml)
    entries = sen_tree.xpath("//sense[@name='" + word.upper() + "']")
    syn_xml = 'rwn\\synset_relations.' + pos + '.xml'
    syn_tree = etree.parse(syn_xml)
    if len(entries) == 0:
        return [word]
    result = [word]
    for entry in entries:
        synonyms = syn_tree.xpath("//relation[@parent_id='" + entry.attrib['synset_id'] + "'][@name='hypernym']")
        for synonym in synonyms:
            senses_of_synonym = sen_tree.xpath("//sense[@synset_id='" + synonym.attrib['child_id'] + "']")
            for s in senses_of_synonym:
                if len(s.attrib['name'].split()) == 1:
                    result.append(s.attrib['name'].lower())
    return [s for s in result if s not in INCORRECT_SYNONYMS]


def shuffle_except_first_word(synonyms):
    syn = list(synonyms)
    base_word = syn[0]
    syn = syn[1:]
    random.shuffle(syn)
    syn = [base_word] + syn
    return syn


def colorize_frame(frame_list, colorizing, synonyms):
    for frame in frame_list:
        if [frame] in colorizing:  # means that frame haven't got color now
            syn = shuffle_except_first_word(synonyms)
            for el in colorizing:
                if len(el) > 1 and el[0] in frame_list:  # -- it needs if we want minimize colorizing
                    syn.remove(el[1])
            i = colorizing.index([frame])
            colorizing[i] = [frame, syn[0]]
    return colorizing


def correction_word_form(k, v, refactoring):
    correction_synonyms = find_synonyms_for_correct_mistake(k)
    frame_start = -1
    frame_end = 0
    # print(v)
    colorizing_v = [[e] for e in v]
    while frame_end != len(v):
        frame_start = frame_start + 1
        stop_val = v[frame_start] + WORD_FORM_RED_WORD_DISTANCE
        if stop_val > v[-1]:
            frame_end = len(v)
        else:
            frame_end = v.index(list(filter(lambda x: x <= stop_val, v))[-1]) + 1
        frame_list = list(islice(v, frame_start, frame_end))
        if len(frame_list) > len(correction_synonyms):
            print('Измените предложение')
            refactoring.append(v)
            break  # continue # лучше break, тк хоть одна проблема должна вести к изменению всего сегмента
        # print('colorizing before', colorizing_v)
        colorizing_v = colorize_frame(frame_list, colorizing_v, correction_synonyms)
    print('colorizing: ', colorizing_v)
    return colorizing_v


def remove_incorrect_synonym(word, k, v, refactoring, is_another_word):
    global INCORRECT_SYNONYMS, MAIN_WORD
    if is_another_word:
        MAIN_WORD = k
        INCORRECT_SYNONYMS = []
    INCORRECT_SYNONYMS.append(word)
    return correction_word_form(k, v, refactoring)


