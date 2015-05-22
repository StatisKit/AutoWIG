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

def lower(name):
    lowername = ''
    index = 0
    while index < len(name):
        if name[index].islower():
            lowername += name[index]
            index += 1
        else:
            lowername += '_' + name[index].lower()
            index += 1
            while index < len(name) and not name[index].islower():
                lowername += name[index].lower()
                index += 1
    if not name.startswith('_'):
        return lowername.lstrip('_')
    else:
        return lowername

def to_path(name, upper=False, directories=False):
    scopes = split_scopes(name)
    for index, scope in enumerate(scopes):
        for delimiter in ['<', '(', '[', ']', ')', '>']:
            scope = scope.replace(delimiter, '_')
        scopes[index] = scope.replace(' ', '_')
    if directories:
        path = os.sep.join(scopes)
    else:
        path = '_'.join(scopes)
    if not upper:
        return lower(path)
    else:
        return path
