import re

import chardet
import pymorphy2
import regex as re


def lemmatize(current_dir, f):
    # os.path.dirname(os.path.abspath(__file__))
    words = parse_text_from_file(current_dir, f)
    # lemmatext = ' '.join(line.split(sep=' ')for line in lines)
    # text = ' '.join(word.lower() for word in text.split())  # lowercasing and removing short words
    # text = re.sub('\s\r\n\s{1,}|\s\r\n|\r\n', '', text)  # deleting newlines and line-breaks
    # text = re.sub('[,:;%©*@#$^&()\d]|[+=]|[[]|[]]|[/]|"|\s{2,}', ' ', text)  # deleting symbols
    # text = re.sub('[.]', ' .', text)
    # text = re.sub('[!]', ' !', text)
    # text = re.sub('[?]', ' ?', text)
    print(words)
    lemmatext = ''
    for word_line in words:
        for word in word_line:
            lemmatext += pymorphy2.MorphAnalyzer().parse(str(word))[0].normal_form + ' '
    return lemmatext


def parse_text_from_file(current_dir, f, without_symbols=True):
    with open(current_dir + "\\" + f, mode='rb') as file:
        text = file.read()
    codepage = chardet.detect(text)['encoding']
    text = text.decode(codepage)
    lines = re.split(r'[~\r\n]+', text)
    if without_symbols:
        pattern = r'[\p{L}]*[\-]*[\p{L}]+'
        lines = [line.lower() for line in lines]
    else:
        pattern = r'[\p{L}0-9,.!?:;-–"\'\[\]{}()]*[\-]*[\p{L}0-9,.!?:;"\'\[\]{}()]+'
    words = [list(filter(None, re.findall(pattern, line))) for line in lines]
    return words
