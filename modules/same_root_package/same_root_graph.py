import itertools

SAME_ROOT_RED_DISTANCE = 10 # 3 + 1
IS_SAME_ROOT = 1


def is_col_in_same_root_graph(col, same_root_graph):
    for exists_tuples in same_root_graph.keys():
        if col in exists_tuples:
            return True
    return False


def construct_same_root_graph(voc, same_root_table):
    i, j = 0, 0
    same_root_graph = dict()

    for col in same_root_table:
        if is_col_in_same_root_graph(col, same_root_graph):
            continue
        j = 0
        key_list = [col]  # key_list is list of same_root_package words which is distanced closely
        dist_list = []

        col_pos = []
        for el in voc.get_node_by_key(col).pos:
            col_pos.append(el[0])

        for row in same_root_table[col]:
            if j <= i:  # search in upper triangle matrix
                j += 1
                continue
            if same_root_table[col][row] == IS_SAME_ROOT:
                row_pos = []
                for el in voc.get_node_by_key(row).pos:
                    row_pos.append(el[0])
                for pair in itertools.product(col_pos, row_pos):  # for each cartesian product of col_pos and row_pos
                    if abs(pair[0] - pair[1]) < SAME_ROOT_RED_DISTANCE:  # if product is close
                        key_list.append(row)  # then add to key_list word `row` and add product in dist_list
                        if not pair[0] in dist_list:
                            dist_list.append(pair[0])
                        if not pair[1] in dist_list:
                            dist_list.append(pair[1])
                dist_list.sort()
            j += 1
        if len(key_list) > 1:  # if key_list contains not only col then we have same_root_graph vertex
            same_root_graph[tuple(key_list)] = dist_list
        i += 1

    # print same_root_graph
    # for v in same_root_graph:
    #     print(v)
    #     print(same_root_graph[v])

    return same_root_graph
