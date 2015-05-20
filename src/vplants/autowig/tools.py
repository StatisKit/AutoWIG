import os

def split_scopes(name):
    scopes = []
    current = 0
    previous = 0
    delimiter = 0
    if name.startswith('::'):
        name = name[2:]
    while current < len(name):
        if name[current] in ['<', '(', '[']:
            delimiter += 1
            current += 1
        elif name[current] in ['>', ')', ']']:
            delimiter -= 1
            current += 1
        elif name[current:current+2] == '::':
            scopes.append(name[previous:current])
            current += 2
            previous = current
        else:
            current += 1
    scopes.append(name[previous:current])
    return scopes

def to_path(name, lower=True, directories=False):
    scopes = split_scopes(name)
    for index, scope in enumerate(scopes):
        for delimiter in ['<', '(', '[', ']', ')', '>']:
            scope = scope.replace(delimiter, '_')
        scopes[index] = scope.replace(' ', '_')
    if directories:
        path = os.sep.join(scopes)
    else:
        path = '_'.join(scopes)
    if lower:
        lowerpath = ''
        index = 0
        while index < len(path):
            if path[index].islower():
                lowerpath += path[index]
                index += 1
            else:
                lowerpath += '_' + path[index].lower()
                index += 1
                while index < len(path) and not path[index].islower():
                    lowerpath += path[index].lower()
                    index += 1
        return lowerpath.lstrip('_')
    else:
        return path
