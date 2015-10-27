
import re
import inspect
import uuid


class FactoryDocstring(object):

    def __init__(self, method):
        self.method = method

    def __str__(self):
        docstring = 'This method is controlled by the following identifiers:'
        for name, method in inspect.getmembers(self.method.im_class, predicate=inspect.ismethod):
            if re.match('^_(.*)_' + self.method.im_func.__name__+'$', name):
                docstring += '\n - \"' + re.sub('^_(.*)_' + self.method.im_func.__name__+'$', r'\1', name) + '\"'
        return docstring

    @staticmethod
    def as_factory(method):
        method.im_func.func_doc = FactoryDocstring(method)

    def expandtabs(self, tabsize):
        return str(self).expandtabs(tabsize)

inspect.types.StringTypes += (FactoryDocstring,)


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


def to_path(node, upper=False, offset=0, dirpath='.'):
    path = compute_path(node).lstrip('_')
    if not upper:
        path = lower(path)
    maxlength = 100#os.pathconf(dirpath, 'PC_NAME_MAX')
    if len(path) > maxlength-offset:
        offset += 36
        alt_path = path[:maxlength-offset]
        if not alt_path.endswith('_'):
            alt_path += '_'
            offset += 1
        return alt_path + str(uuid.uuid5(uuid.NAMESPACE_X500, path[maxlength-offset:])).replace('-', '_')
    else:
        return path


def compute_path(node):
    if node.localname == '':
        return ''
    elif node.localname.endswith('>'):
        return compute_path(node.parent) + '_' + remove_templates(node.localname) + '_' + node.hash
    else:
        return compute_path(node.parent) + '_' + node.localname
