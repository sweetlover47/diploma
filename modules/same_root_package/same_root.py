import collections
import time

import lxml.etree as etree

poses = ['A', 'N', 'V']


def construct_table(voc):
    same_root_table = dict()
    for n in voc.nodes:
        same_root_table[n.key] = {i.key: 0 for i in voc.nodes}
    start = time.time()
    derived_str = 'rwn\\derived_from.xml'
    tree = etree.parse(derived_str)
    for pos in poses:
        for node1 in voc.nodes:
            entries = tree.xpath("sense[@name='" + node1.key.upper() + "']/derived_from/*")
            entries = set(entries)
            if len(entries) == 0:
                continue
            # entries_without_duplicates = set()
            # remove repeated entries if id equals
            entries_without_duplicates = collections.OrderedDict()
            for obj in entries:
                # eliminate this check if you want the last item
                if obj.attrib['name'] not in entries_without_duplicates:
                    entries_without_duplicates[obj.attrib['name']] = obj
            entries_without_duplicates = [*entries_without_duplicates.values()]
            #
            for entry in entries_without_duplicates:
                if entry.attrib['name'].lower() in same_root_table[node1.key]:
                    same_root_table[node1.key][str(entry.attrib['name']).lower()] = 1
    print("Прошло времени: " + str(time.time() - start))
    return same_root_table
