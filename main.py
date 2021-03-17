import modules.lemmatize as lm
import modules.vocabulary as vb
import modules.same_root_package.same_root as smr
import modules.same_root_package.same_root_graph as smr_graph
import modules.print_result as pr_res
import modules.word_form_package.word_form as wf
import modules.synonym_package.synonym as syn
import modules.synonym_package.synonym_graph as syn_graph

path = 'D:\\Programms\\python programms\\diplom_module2'
file_name = 'in.txt'
text = lm.lemmatize(path, file_name)
print('lemmatize done')
print(text)

voc = vb.build_vocabulary(text)
vb.print_vocabulary(voc, 'out.html.txt')
voc.sort()
vb.print_vocabulary(voc, 'out_sort.txt')
voc.simplify()
vb.print_vocabulary(voc, 'out_sort_simplified.txt')
print('print voc done')

same_root_table = smr.construct_table(voc)
print('construct same root table done')
same_root_graph = smr_graph.construct_same_root_graph(voc, same_root_table)
same_root_graph_swapped = {tuple(value): list(key) for key, value in same_root_graph.items()}
print('construct same root fraph swapped done')

word_form_graph = wf.construct_word_form_graph(voc)
print('construct word form graph done')
word_form_graph_swapped = {tuple(value): list(key) for key, value in word_form_graph.items()}
print('construct word form graph swapped done')

synsets_list, synsets_dict, synsets_table = syn.construct_synset_objects(voc)
print('construct synset objects for synonym done')
relation_nodes = syn.construct_relations(synsets_list, synsets_dict, synsets_table)
print('construct relation nodes done')
synonym_graph = syn_graph.construct_synonym_graph(voc, relation_nodes)
synonym_graph_swapped = {tuple(value): list(key) for key, value in synonym_graph.items()}
print('construct synonym graph swapped done')

pr_res.print_html(
    path,
    'out.html',
    same_root_graph_swapped,
    word_form_graph_swapped,
    synonym_graph_swapped
)
print('print to html done')





import json
tmp = json.dumps(list(same_root_graph.items()))
with open(path + '\\' + 'same_root_graph.json', 'w') as f:
    f.write(tmp)
tmp = json.dumps(list(synonym_graph.items()))
with open(path + '\\' + 'synonym_graph.json', 'w') as f:
    f.write(tmp)
tmp = json.dumps(list(word_form_graph.items()))
with open(path + '\\' + 'word_form_graph.json', 'w') as f:
    f.write(tmp)