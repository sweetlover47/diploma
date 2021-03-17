import itertools
import json
import random
import re
from functools import reduce
from itertools import islice

import lxml.etree as etree
import pymorphy2
import regex

import modules.lemmatize as lm
import modules.vocabulary as vc
from modules.word_form_package.word_form import WORD_FORM_RED_WORD_DISTANCE

path = 'D:\\Programms\\python programms\\diplom_module2'


def init_graphs():
    with open(path + '\\' + 'same_root_graph.json', 'r') as f:
        tmp = f.read()
    _same_root_graph = dict(map(tuple, kv) for kv in json.loads(tmp))
    _same_root_graph = {k: list(v) for k, v in _same_root_graph.items()}
    print(_same_root_graph)
    with open(path + '\\' + 'synonym_graph.json', 'r') as f:
        tmp = f.read()
    _synonym_graph = dict(map(tuple, kv) for kv in json.loads(tmp))
    _synonym_graph = {k: list(v) for k, v in _synonym_graph.items()}
    print(_synonym_graph)
    with open(path + '\\' + 'word_form_graph.json', 'r') as f:
        tmp = f.read()
    _word_form_graph = {k: v for k, v in json.loads(tmp)}
    print(_word_form_graph)
    return _word_form_graph, _same_root_graph, _synonym_graph


# word-form: for each pair key-value construct graph of distance between positions and sort by asc if starts from the
# end words on first positions in list, which distanced from others > RED_DISTANCE, it stayed the same when distances
# started be <= RED_DISTANCE, need to correct mistake


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
    return result


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


def correction_word_form():
    correction_synonyms = find_synonyms_for_correct_mistake(k)
    frame_start = -1
    frame_end = 0
    print(v)
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
            break  # continue # лучше break, тк хоть одна проблема должна вести к изменению всего сегмента
        print('colorizing before', colorizing_v)
        colorizing_v = colorize_frame(frame_list, colorizing_v, correction_synonyms)
        print('colorizing after', colorizing_v)
    return colorizing_v


# word-form: agreement of correction
def nearest(list, v):
    remembered = None
    for el in list:
        if v < el:
            return remembered
        else:
            remembered = el
    raise NameError('replacement position not from text')


def word_agreement(word_without_noise):
    morph = pymorphy2.MorphAnalyzer()
    morph_word = morph.parse(word_without_noise)[0]
    tag = morph_word.tag
    pos = tag.POS
    form = None
    if pos == 'NOUN':
        form = {tag.case, tag.number, tag.gender}
    elif pos == 'VERB':
        form = {tag.aspect, tag.mood, tag.number, tag.tense, tag.transitivity}
    elif pos == 'INFN':
        form = {}
    else:  # add form for ADJF
        print(tag)
        pass
    morph_replacement = morph.parse(replacement[1])[0]
    return morph_replacement.inflect(form).word


# same-root:
# in tuple see for weakest word, ex. старый старик
# 'старый' is weaker then 'старик', therefore delete 'старый' in this pair
# weak-scale: ADJF < NOUN < VERB/INFN

def correction_same_root():
    pass


# synonym:
# I can't correct this mistake, that's why I'll ask for user to reconstruct the sentence.
# Mistake will be mark all sentence and hint will be 'Reconstruct the sentence, please'
def correction_synonym():
    pass


word_form_graph, same_root_graph, synonym_graph = init_graphs()

# word-form: colorize
colorize = []
for k, v in word_form_graph.items():
    colorize = itertools.chain(colorize, correction_word_form())
colorize = list(colorize)

# word-form: read text for replacement
words = lm.parse_text_from_file(path, 'in.txt', without_symbols=False)
line_word_length = [len(word_line) for word_line in words]
stop_value_line_word = [0]
for i in range(len(line_word_length)):
    stop_value_line_word.append(sum(line_word_length[:i + 1]))

response = dict()

# word-form: each replacement need to agreement in sentence
for replacement in colorize:
    nearest_value = nearest(stop_value_line_word, replacement[0])
    outer_index = stop_value_line_word.index(nearest_value)
    inner_index = replacement[0] - nearest_value

    wrong_word = words[outer_index][inner_index]
    word_without_noise = regex.search(r'[\p{L}]*[\-]*[\p{L}]+', wrong_word)[0]
    agree_replacement = word_agreement(word_without_noise)
    correct_word = wrong_word.replace(word_without_noise, agree_replacement)
    if correct_word != wrong_word:
        response[replacement[0]] = [wrong_word, correct_word]
        words[outer_index][inner_index] = correct_word  # wrong_word + ' (correct: ' + correct_word + ')'
words = reduce(lambda a, b: a + ['\n'] + b, words)

# write to json
with open('response.json', 'w') as file_json:
    json.dump(response, file_json)

# write correct text
text = ' '.join(words)
text = re.sub(r'\s+\n+\s+', '\n', text)
with open(path + '\\out_replacement.txt', mode='w', encoding='utf-8') as f:
    f.write(text)
