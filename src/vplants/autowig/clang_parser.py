"""
"""

from path import path
import asciitree
from clang.cindex import Config, Index, TranslationUnit
from ConfigParser import ConfigParser

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


def parse_file(filepath, listflags=None, dictflags=None):
    """
    """
    if not isinstance(filepath, basestring):
        raise TypeError('`filepath` parameter')
    if not isinstance(filepath, path):
        filepath = path(filepath)
    if not filepath.exists():
        raise ValueError('`filepath` parameter')

    index = Index.create()

    if not isinstance(filepath, basestring):
        raise TypeError('`filepath` parameter')
    if not isinstance(filepath, path):
        filepath = path(filepath)

    clang = ['-x', 'c++']

    if not dictflags is None:
        if not isinstance(dictflags, dict):
            raise TypeError('`dictflags` parameter')
        clang.extend(['-'+i+'='+j for i, j in dictflags.iteritems()])

    if not listflags is None:
        if not isinstance(listflags, list):
            raise TypeError('`listflags` parameter')
        clang.extend(listflags)

    clang.append('-D__AUTOWIG__')
    clang.append('-Wdocumentation')

    return index.parse(filepath, clang)
