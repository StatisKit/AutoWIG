"""
"""

from openalea.core.path import path
from index import index
from ConfigParser import ConfigParser
from types import ModuleType
import asciitree
from clang.cindex import TranslationUnit

def __repr__(self):
    """
    """

    def node_children(node):
        """
        """
        return (c for c in node.get_children() if c.location.file.name == self.spelling)

    def print_node(node):
        """
        """
        text = node.spelling or node.displayname
        kind = str(node.kind)[str(node.kind).index('.')+1:]
        return '{} {}'.format(kind, text)

    return asciitree.draw_tree(self.cursor, node_children, print_node)

TranslationUnit.__repr__ = __repr__

#def parse_mod(mod):
#    """
#    """
#    if not isinstance(mod, ModuleType):
#        raise TypeError('`mod` parameter')
#    modpath = mod.modpath
#    if isinstance(modpath, Sequence):
#        if len(modpath) > 1:
#            raise ValueError('`mod` parameter')
#        modpath = modpath[0]
#    if not isinstance(modpath, basestring):
#        raise ValueError('`mod` parameter')
#    modpath = path(modpath)
#
#    clang = ['-x', 'c++']
#
#    configparser = ConfigParser()
#    configparser.read(modpath/'metainfo.ini')
#    try:
#        config = dict(configparser.items('CXXFLAGS'))
#
#        if 'std' in config:
#            clang.append('-std='+config['std'])
#    except:
#        pass
#
#    clang.append('-D__CODE_GENERATOR__')
#    for i in (modpath/'src'/'cpp').walkfiles('*.h'):
#        yield index.parse(str(i), clang)
#

def parse(filepath, listflags=None, dictflags=None):
    """
    """

    if not isinstance(filepath, basestring):
        raise ValueError('`filepath` parameter')
    if not isinstance(filepath, path):
        filepath = path(filepath)

    clang = ['-x', 'c++']

    if not dictflags is None:
        if not isinstance(dictflags, dict):
            raise TypeError('`dictflags` parameter')
        clang.extend(['-'+i+'='+j for i, j in cxxflags.iteritems()])

    if not listflags is None:
        if not isinstance(listflags, list):
            raise TypeError('`listflags` parameter')
        clang.extend(listflags)

    clang.append('-D__CODE_GENERATOR__')
    clang.append('-Wdocumentation')

    return index.parse(filepath, clang)
