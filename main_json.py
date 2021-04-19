import json
import re
from functools import reduce

import pymorphy2
import regex

import modules.correction.word_form_correction as wfc
import modules.search.lemmatize as lm

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

def correction_same_root(graph, text, response):
    removing = []
    morph = pymorphy2.MorphAnalyzer()
    for k, v in graph.items():
        pos = []
        for el in k:
            morph_word = morph.parse(el)[0]
            pos.append(morph_word.tag.POS)
        if 'ADJF' in pos:
            removing = k[pos.index('ADJF')]
        # elif 'NOUN' in pos:
        #     removing = k[pos.index('NOUN')]
        for position in v:
            outer_index, inner_index = get_indices_by_position(position)
            w = text[outer_index][inner_index]
            without_noise = regex.search(r'[\p{L}]*[\-]*[\p{L}]+', w)[0]
            wn_normal = morph.parse(without_noise)[0].normal_form
            if removing == wn_normal:
                response[position] = [w, '']
    return response


# synonym:
# I can't correct this mistake, that's why I'll ask for user to reconstruct the sentence.
# Mistake will be mark all sentence and hint will be 'Reconstruct the sentence, please'
def synonym_raise(graph, l):
    for positions in graph.values():
        l = l + positions
    return l


word_form_graph, same_root_graph, synonym_graph = init_graphs()
refactoring = []
# word-form: colorize
colorize = []
for k, v in word_form_graph.items():
    colorize.append(wfc.correction_word_form(k, v, refactoring))

# read text for replacement
text = lm.parse_text_from_file(path, 'in.txt', without_symbols=False)
words = list(text)
line_word_length = [len(word_line) for word_line in words]
stop_value_line_word = [0]
for i in range(len(line_word_length)):
    stop_value_line_word.append(sum(line_word_length[:i + 1]))

response = dict()


def get_indices_by_position(word_position):
    nearest_value = nearest(stop_value_line_word, word_position)
    outer = stop_value_line_word.index(nearest_value)
    inner = word_position - nearest_value
    return outer, inner


def correct_mistakes():
    global chain, replacement
    for chain in colorize:
        for replacement in chain:
            outer_index, inner_index = get_indices_by_position(replacement[0])
            wrong_word = words[outer_index][inner_index]
            word_without_noise = regex.search(r'[\p{L}]*[\-]*[\p{L}]+', wrong_word)[0]
            agree_replacement = word_agreement(word_without_noise)
            correct_word = wrong_word.replace(word_without_noise, agree_replacement)
            if correct_word != wrong_word:
                response[replacement[0]] = [wrong_word, correct_word]
                words[outer_index][inner_index] = correct_word  # wrong_word + ' (correct: ' + correct_word + ')'


# word-form: each replacement need to agreement in sentence
correct_mistakes()
words_with_newline = reduce(lambda a, b: a + ['\n'] + b, words)

# same-root
removing_words = correction_same_root(same_root_graph, text, response)

# synonym
refactoring = synonym_raise(synonym_graph, refactoring)

# write to json
with open('response.json', 'w') as file_json:
    json.dump(response, file_json)
with open('raising.json', 'w') as raise_file:
    json.dump(refactoring, raise_file)

# write correct text
text = ' '.join(words_with_newline)
text = re.sub(r'\s+\n+\s+', '\n', text)
with open(path + '\\out_replacement.txt', mode='w', encoding='utf-8') as f:
    f.write(text)


# TODO: нужно пробрасывать исключение о недостатке цветов раскраски
incorrect_position = int(input())
while incorrect_position != -1:
    cur_chain = []
    word = ''
    for k, v in word_form_graph.items():
        if incorrect_position in v:
            for chain in colorize:
                for color in chain:
                    if incorrect_position == color[0]:
                        word = color[1]
                        cur_chain = chain
                        break
            isAnother = (wfc.MAIN_WORD != k)
            new_colorize_chain = wfc.remove_incorrect_synonym(word, k, v, refactoring, isAnother)
            colorize = [new_colorize_chain if cur_chain == chain else chain for chain in colorize]
            break
    correct_mistakes()
    words_with_newline = reduce(lambda a, b: a + ['\n'] + b, words)
    incorrect_position = int(input())

with open('response.json', 'w') as file_json:
    json.dump(response, file_json)
with open('raising.json', 'w') as raise_file:
    json.dump(refactoring, raise_file)

# write correct text
text = ' '.join(words_with_newline)
text = re.sub(r'\s+\n+\s+', '\n', text)
with open(path + '\\output\\out_replacement.txt', mode='w', encoding='utf-8') as f:
    f.write(text)
