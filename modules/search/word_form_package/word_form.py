WORD_FORM_RED_WORD_DISTANCE = 10 # 4
WORD_FORM_RED_SENTENCE_DISTANCE = 0


def construct_word_form_graph(voc):
    word_form_graph = dict()
    for node in voc.nodes:
        i = 0
        for i in range(len(node.pos) - 1):
            if abs(node.pos[i][1] - node.pos[i + 1][1]) < WORD_FORM_RED_SENTENCE_DISTANCE \
                    or abs(node.pos[i][0] - node.pos[i + 1][0]) < WORD_FORM_RED_WORD_DISTANCE:
                if not node.key in word_form_graph:
                    word_form_graph[node.key] = []
                if not node.pos[i][0] in word_form_graph[node.key]:
                    word_form_graph[node.key].append(node.pos[i][0])
                if not node.pos[i + 1][0] in word_form_graph[node.key]:
                    word_form_graph[node.key].append(node.pos[i + 1][0])
    return word_form_graph
