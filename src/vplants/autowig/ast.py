from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from clang.cindex import Index, TranslationUnit, CursorKind
from ConfigParser import ConfigParser
import os
from tempfile import NamedTemporaryFile
from path import path
import asciitree
from itertools import chain, imap

from .config import Cursor

__all__ = ['AbstractSyntaxTree']

class CursorProxy(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def __str__(self):
        filehandler = open(str(self.cursor.location.file), 'r')
        string = [line for index, line in enumerate(filehandler.readlines()) if self.cursor.extent.start.line <= index+1 <= self.cursor.extent.end.line]
        filehandler.close()
        if len(string) == 1:
            return string[0][self.cursor.extent.start.column-1:self.cursor.extent.end.column]
        else:
            string[0] = string[0][self.cursor.extent.start.column-1:]
            string[-1] = string[-1][:self.cursor.extent.end.column]
            string = "".join(string)
            return string

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

class AbstractSyntaxTree(object):
    """
    """

    def __init__(self, *includes, **kwargs):
        """
        """
        tempfilehandler = NamedTemporaryFile(delete=False)
        if any(not isinstance(include, basestring) for include in includes):
            raise TypeError('`includes` parameter')
        includes = [include if isinstance(include, path) else path(include) for include in includes]

        self.language = dict.pop(kwargs, 'language', 'c++')
        if not isinstance(self.language, basestring):
            raise TypeError('\'language\' parameter')

        self.includes = []
        for include in includes:
            if not include.exists() or not include.isfile():
                raise ValueError('`includes` parameter')
            self.includes.append(str(include.abspath()))
        for include in self.includes:
            tempfilehandler.write('#include \"' + include + '\"\n')
        tempfilehandler.close()

        if self.language == 'c':
            flags = ['-x', 'c', '-std=c11']
        elif self.language == 'c++':
            flags = ['-x', 'c++', '-std=c++11']
        else:
            raise ValueError('\'language\' parameter')
        flags.append('-Wdocumentation')
        flags = kwargs.get('flags', flags)

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
        return [CursorProxy(cursor) for cursor in back]

    def __getitem__(self, item):
        return self.cursors[item]

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
