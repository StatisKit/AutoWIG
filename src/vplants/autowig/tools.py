import os
import re

def subclasses(cls, recursive=True):
    if recursive:
        subclasses = []
        front = [cls]
        while len(front) > 0:
            cls = front.pop()
            front.extend(cls.__subclasses__())
            subclasses.append(cls)
        return {subclass.__name__ : subclass for subclass in subclasses}.values()
    else:
        return cls.__subclasses__()

def remove_regex(name):
    for specialchar in ['.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '|']:
        name = name.replace(specialchar, '\\' + specialchar)
    return name

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
        elif name[current:current+2] == '::' and delimiter == 0:
            scopes.append(name[previous:current])
            current += 2
            previous = current
        else:
            current += 1
    scopes.append(name[previous:current])
    return scopes

def remove_templates(name):
    delimiter = name.endswith('>')
    index = -1
    while not delimiter == 0 and len(name)+index > 0:
        index -= 1
        if name[index] == '<':
            delimiter -= 1
        elif name[index] == '>':
            delimiter += 1
    if delimiter == 0:
        return name[0:index]
    else:
        return name

def lower(name):
    lowername = '_'
    index = 0
    while index < len(name):
        if name[index].islower():
            lowername += name[index]
            index += 1
        else:
            if lowername[-1] == '_':
                if not name[index] == '_':
                    lowername += name[index].lower()
            else:
                if not name[index] == '_':
                    lowername += '_' + name[index].lower()
                else:
                    lowername += '_'
            index += 1
            while index < len(name) and not name[index].islower():
                lowername += name[index].lower()
                index += 1
    lowername = lowername.lstrip('_')
    return lowername

def to_path(name, upper=False, directories=False):
    if name.startswith('enum '):
        name = name[5:]
    elif name.startswith('class '):
        name = name[5:]
    elif name.startswith('union '):
        name = name[5:]
    elif name.startswith('struct '):
        name = name[6:]
    name = re.sub('(\s|\(|\)|>)', '', name)
    if directories:
        path = re.sub(':+', os.sep, name)
        path.lstrip(os.sep)
    path = re.sub('[:<,]+', '_', name)
    path.lstrip('_')
    if not upper:
        return lower(path)
    else:
        return path
