import itertools

SYNONYM_RED_DISTANCE = 10 #5


def construct_synonym_graph(voc, relation_nodes):
    synonym_graph = dict()
    # relation_nodes member is list of word in uppercase, ex: ['TO BE', 'TO GROW']
    for node in relation_nodes:
        dist_list = []
        key_tuple = []
        for word in node:
            w = voc.get_node_by_key(str(word).lower())
            print(w.key, w.pos)
            tmp = []
            # add all positions of w (pos[0] because i need distance in words, not in sentences)
            for p in w.pos:
                tmp.append(p[0])
            dist_list.append(tmp)
            key_tuple.append(w.key)
        key_tuple = tuple(key_tuple)
        # iterate all relations (w1, w2, w3) as pairs (w1, w2), (w1, w3), (w2, w3), where wi is member of list of position
        # prod is (w1, w2, w3)
        synonym_graph[key_tuple] = []
        for prod in itertools.product(*dist_list):
            for pair in itertools.combinations(prod, 2):
                if abs(pair[0] - pair[1]) < SYNONYM_RED_DISTANCE:
                    if not pair[0] in synonym_graph[key_tuple]:
                        synonym_graph[key_tuple].append(pair[0])
                    if not pair[1] in synonym_graph[key_tuple]:
                        synonym_graph[key_tuple].append(pair[1])
        synonym_graph[key_tuple].sort()
        if key_tuple in synonym_graph and len(synonym_graph[key_tuple]) == 0:
            del synonym_graph[key_tuple]
    return synonym_graph