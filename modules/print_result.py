colors = [
    'd45bb3',
    'ffa1a1',
    'c4a6ff',
    'a6c5ff',
    'b5ff6b',
    '5bd483',
    'fff86e',
    'e38f5b',
    'e35b5b',
    'a80000',
    'a8009d',
    '1100a8',
    '0070a8',
    '00a89a',
    '00a85a',
    '84a800',
    'a89a00',
    'a85400',
    '7a5151',
    'd45bb3',
    'ffa1a1',
    'c4a6ff',
    'a6c5ff',
    'b5ff6b',
    '5bd483',
    'fff86e',
    'e38f5b',
    'e35b5b',
    'a80000',
    'a8009d',
    '1100a8',
    '0070a8',
    '00a89a',
    '00a85a',
    '84a800',
    'a89a00',
    'a85400',
    '7a5151'
]

def print_html(dir_path, filename, smr, wf, syn):
    word_color = fill_word_color(smr, syn, wf)

    i = 0
    text = ''
    with open(dir_path + '\\in.txt', 'rb') as file:
        for line in file:
            for word in line.decode(encoding='utf-8').split():
                if i in word_color:
                    text += f'<span style="background-color: #{word_color[i]}">{word}</span>'
                else:
                    text += word
                text += ' '
                i += 1
        text += '\n'

    with open(dir_path + '\\' + filename, 'wb') as file:
        file.write(
            '<html><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type"></head><body>'.encode(
                'utf-8'))
        t = text.encode(encoding='utf-8')
        file.write(t)
        file.write('</body></html>'.encode('utf-8'))


def fill_word_color(smr, syn, wf):
    word_color = dict()
    i = 0
    for t in smr.keys():
        l = list(t)
        for el in l:
            word_color[el] = colors[i % 15]
        i += 1
    for t in wf.keys():
        l = list(t)
        for el in l:
            word_color[el] = colors[i % 15]
        i += 1
    for t in syn.keys():
        l = list(t)
        for el in l:
            word_color[el] = colors[i % 15]
        i += 1
    return word_color
