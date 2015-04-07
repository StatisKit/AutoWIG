from clang.cindex import Config, conf, Index, TranslationUnit, Cursor, CursorKind
from ConfigParser import ConfigParser
import os
from tempfile import NamedTemporaryFile
from path import path
import asciitree
from itertools import chain, imap

if not Config.loaded:
    configpath = path(__file__)
    while len(configpath) > 0 and not str(configpath.name) == 'src':
        configpath = configpath.parent
    configpath = configpath.parent
    configparser = ConfigParser()
    configparser.read(configpath/'metainfo.ini')
    config = dict(configparser.items('libclang'))
    if 'path' in config:
            Config.set_library_path(config['path'])
    elif 'file' in config:
        Config.set_library_file(config['file'])
    else:
        raise IOError('cannot find libclang path or file')

def is_virtual_method(self):
    """Returns True if the cursor refers to a C++ member function that
    is declared 'virtual'.
    """
    return conf.lib.clang_CXXMethod_isVirtual(self)

Cursor.is_virtual_method = is_virtual_method
del is_virtual_method

def is_pure_virtual_method(self):
    """Returns True if the cursor refers to a C++ member function that
    is declared pure 'virtual'.
    """
    return conf.lib.clang_CXXMethod_isPureVirtual(self)

Cursor.is_pure_virtual_method = is_pure_virtual_method
del is_pure_virtual_method

class AbstractSyntaxTree(object):
    """
    """

    def __init__(self, *filepaths, **kwargs):
        """
        """
        tempfilehandler = NamedTemporaryFile(delete=False)
        if any(not isinstance(filepath, basestring) for filepath in filepaths):
            raise TypeError('`filepaths` parameter')
        filepaths = [filepath if isinstance(filepath, path) else path(filepath) for filepath in filepaths]
        for filepath in filepaths:
            if not filepath.exists() or not filepath.isfile():
                raise ValueError('`filepaths` parameter')
            tempfilehandler.write('#include \"' + filepath.abspath() + '\"\n')
        tempfilehandler.close()

        flags = kwargs.get('flags', ['-x', 'c++', '-Wdocumentation'])
        options = kwargs.get('options', TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

        index = Index.create()
        self.translation_unit = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=options)
        os.unlink(tempfilehandler.name)

    @property
    def cursors(self):
        """
        """
        front = [self.translation_unit.cursor]
        back = []
        while len(front) != 0:
            back.append(front.pop())
            front.extend(reversed(list(back[-1].get_children())))
        return back

    def __repr__(self):
        """
        """
        print_node.node_id = -1
        return asciitree.draw_tree(self.translation_unit.cursor, node_children, print_node)

def node_children(node):
    return node.get_children()

def print_node(node):
    text = node.spelling or node.displayname
    kind = str(node.kind)[str(node.kind).index('.')+1:]
    access = node.access_specifier
    print_node.node_id += 1
    return '{} {} ({})'.format(kind, text, str(print_node.node_id))
