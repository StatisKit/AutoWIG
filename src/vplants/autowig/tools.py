"""
"""
from IPython.display import HTML
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
import asciitree
from clang.cindex import Config, Index, TranslationUnit
from ConfigParser import ConfigParser
from path import path

if not Config.loaded:
    _path_ = path(__file__)
    while len(_path_) > 0 and not str(_path_.name) == 'src':
        _path_ = _path_.parent
    _path_ = _path_.parent
    configparser = ConfigParser()
    configparser.read(_path_/'metainfo.ini')
    config = dict(configparser.items('libclang'))

    if 'path' in config:
            Config.set_library_path(config['path'])
    elif 'file' in config:
        Config.set_library_file(config['file'])
    else:
        raise IOError('cannot find libclang path or file')

class AST(object):
    """
    """

    def __init__(self, *translation_units):
        """
        """
        if any(not isinstance(translation_unit, TranslationUnit) for translation_unit in translation_units):
            raise TypeError('`translation_units` parameter')
        self._translation_units = translation_units

    def function(self, child):
        return not child.location.file is None and child.location.file.name == child.translation_unit.cursor.spelling

    def __repr__(self):
        """
        """

        def node_children(node):
            return filter(self.function, node.get_children())

        def print_node(node):
            text = node.spelling or node.displayname
            kind = str(node.kind)[str(node.kind).index('.')+1:]
            access = node.access_specifier
            return '{} {}'.format(kind, text)

        return "\n".join(asciitree.draw_tree(translation_unit.cursor, node_children, print_node) for translation_unit in self._translation_units)

def parse_file(filepath, flags=None):
    """
    """
    if not isinstance(filepath, basestring):
        raise TypeError('`filepath` parameter')
    if not isinstance(filepath, path):
        filepath = path(filepath)
    if not filepath.exists():
        print filepath
        raise ValueError('`filepath` parameter')

    index = Index.create()

    if not isinstance(filepath, basestring):
        raise TypeError('`filepath` parameter')
    if not isinstance(filepath, path):
        filepath = path(filepath)
    if flags is None: flags = []
    flags.extend(['-x', 'c++', '-Wdocumentation'])

    return index.parse(filepath, flags)

def lower(string):
    return ''.join('_' + c.lower() if c.isupper() else c for c in string).lstrip('_')

def indent(lines, tabsize=4, level=1):
    return "\n".join(" "*tabsize*level+line for line in lines.splitlines())

def H(obj, **kwargs):
    return HTML(highlight(obj.interface(), CppLexer(), HtmlFormatter(full = True)), **kwargs)

def CPP(obj, **kwargs):
    return HTML(highlight(obj.implementation(), CppLexer(), HtmlFormatter(full = True)), **kwargs)
