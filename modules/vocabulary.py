import operator
import re
from builtins import list as type_list
from dataclasses import dataclass, field

import pymorphy2


@dataclass
class VocNode:
    key: str
    tag: str
    pos: type_list
    dist: type_list = field(default_factory=type_list)

    def get_key(self):
        return self.key


@dataclass()
class Voc:
    nodes: type_list = field(default_factory=type_list)

    def contains_key(self, key):
        for n in self.nodes:
            if n.get_key() == key:
                return True
        return False

    def get_node_by_key(self, key) -> VocNode:
        for n in self.nodes:
            if n.get_key() == key:
                return n

    def sort(self):
        self.nodes.sort(key=operator.attrgetter('tag', 'key'))

    def simplify(self):
        self.nodes = [n for n in self.nodes if not n.tag == "O"]

    def get_synsets_by_tag(self):
        _a = []
        _n = []
        _v = []
        for node in self.nodes:
            if node.tag == 'A':
                _a.append(node)
            elif node.tag == 'N':
                _n.append(node)
            elif node.tag == 'V':
                _v.append(node)
        return [_a, _n, _v]


def build_vocabulary(text):
    voc = Voc()
    words = text.split()
    sent = 0
    for i in range(len(words)):
        if re.compile(r'[.!?]').search(words[i]):
            sent += 1
            continue
        if not voc.contains_key(words[i]):
            word = words[i]
            p = pymorphy2.MorphAnalyzer().parse(word)[0]
            tag = 'O'  # o - other
            if 'NOUN' in p.tag:
                tag = 'N'
            elif 'INFN' in p.tag:
                tag = 'V'
            elif 'ADJF' in p.tag:
                tag = 'A'
            voc.nodes.append(VocNode(words[i], tag, [[i - sent, sent]]))
        else:
            node = voc.get_node_by_key(words[i])
            node.pos.append([i - sent, sent])
    return voc


def print_vocabulary(_voc, _filename):
    with open('output\\' + _filename, 'w') as out:
        for node in _voc.nodes:
            out.write(node.key + "," + node.tag + "=" + str(node.pos) + "&" + str(node.dist) + "\n")
    return
