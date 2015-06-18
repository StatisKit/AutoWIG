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

from vplants.autowig import autowig

from .config import Cursor

__all__ = ['AbstractSyntaxTree']

def __str__(self):
    text = self.spelling or self.displayname
    kind = str(self.kind)[str(self.kind).index('.')+1:]
    return '{} {}'.format(kind, text)

Cursor.__str__ = __str__
del __str__

class AbstractSyntaxTree(object):
    """
    """

    def __init__(self, *args, **kwargs):
        self._nodes = dict()
        self._children = dict()
        flags = dict.pop(kwargs, 'flags', None)
        if flags is None:
            language = kwargs.pop('language')
            if language == 'c++':
                flags = ['-x', 'c++', '-std=c++11', '-Wdocumentation']
            elif language == 'c':
                flags = ['-x', 'c', '-std=c11', '-Wdocumentation']
        libclang = kwargs.pop('libclang', False)
        if libclang:
            index = Index.create()
            tempfilehandler = NamedTemporaryFile(delete=False)
            for arg in args:
                tempfilehandler.write('#include \"' + str(path(arg).abspath()) + '\"\n')
            tempfilehandler.close()
            tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
            os.unlink(tempfilehandler.name)
        else:
            content = ""
            for arg in args:
                content += '#include \"' + str(path(arg).abspath()) + '\"\n'
            tu = autowig.clang.tooling.build_ast_from_code_with_args(content, flags)
        self._read_translation_unit(tu, libclang)

    def __getitem__(self, key):
        return self._nodes[key]

    def _read_translation_unit(self, tu, libclang):
        """
        """
        self._node = 0

        if libclang:
            node = self._node
            self._nodes[node] = tu.cursor
            self._children[node] = []
            self._node += 1
            for child in tu.cursor.get_children():
                self._children[node].append(self._read_decl(child, libclang))
        else:
            node = self._node
            self._nodes[node] = tu
            self._children[node] = []
            self._node += 1
            for child in tu.get_children():
                self._children[node].append(self._read_decl(child, libclang))

        del self._node

    def _read_decl(self, decl, libclang):
        """
        """
        if libclang:
            node = self._node
            self._nodes[node] = decl
            self._children[node] = []
            self._node += 1
            for child in decl.get_children():
                self._children[node].append(self._read_decl(child, libclang))
            return node
        else:
            node = self._node
            self._nodes[node] = decl
            self._children[node] = []
            self._node += 1
            if hasattr(decl, 'get_children'):
                for child in decl.get_children():
                    self._children[node].append(self._read_decl(child, libclang))
            return node

    def __str__(self):

        def node_children(node):
            return self._children[node]

        def print_node(node):
            return '[' + str(node) + '] ' + self._nodes[node].__str__()

        return asciitree.draw_tree(0, node_children, print_node)

#    text = node.spelling or node.displayname
#    kind = str(node.kind)[str(node.kind).index('.')+1:]
#    access = node.access_specifier
#    print_node.node_id += 1
#    return '{} {} ({})'.format(kind, text, str(print_node.node_id))
#class CursorProxy(object):
#
#    def __init__(self, cursor):
#        self.cursor = cursor
#
#    def __str__(self):
#        filehandler = open(str(self.cursor.location.file), 'r')
#        string = [line for index, line in enumerate(filehandler.readlines()) if self.cursor.extent.start.line <= index+1 <= self.cursor.extent.end.line]
#        filehandler.close()
#        if len(string) == 1:
#            return string[0][self.cursor.extent.start.column-1:self.cursor.extent.end.column]
#        else:
#            string[0] = string[0][self.cursor.extent.start.column-1:]
#            string[-1] = string[-1][:self.cursor.extent.end.column]
#            string = "".join(string)
#            return string
#
#    def _repr_html_(self):
#        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))
#
#class AbstractSyntaxTree(object):
#    """
#    """
#
#    def __init__(self, *includes, **kwargs):
#        """
#        """
#        tempfilehandler = NamedTemporaryFile(delete=False)
#        if any(not isinstance(include, basestring) for include in includes):
#            raise TypeError('`includes` parameter')
#        includes = [include if isinstance(include, path) else path(include) for include in includes]
#
#        self.language = dict.pop(kwargs, 'language', 'c++')
#        if not isinstance(self.language, basestring):
#            raise TypeError('\'language\' parameter')
#
#        self.includes = []
#        for include in includes:
#            if not include.exists() or not include.isfile():
#                raise ValueError('`includes` parameter')
#            self.includes.append(str(include.abspath()))
#        for include in self.includes:
#            tempfilehandler.write('#include \"' + include + '\"\n')
#        tempfilehandler.close()
#
#        if self.language == 'c':
#            flags = ['-x', 'c', '-std=c11']
#        elif self.language == 'c++':
#            flags = ['-x', 'c++', '-std=c++11']
#        else:
#            raise ValueError('\'language\' parameter')
#        flags.append('-Wdocumentation')
#        flags = kwargs.get('flags', flags)
#
#        options = kwargs.get('options', TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
#
#        index = Index.create()
#        self.translation_unit = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=options)
#        os.unlink(tempfilehandler.name)
#
#    @property
#    def cursors(self):
#        """
#        """
#        front = [self.translation_unit.cursor]
#        back = []
#        while len(front) != 0:
#            back.append(front.pop())
#            front.extend(reversed(list(back[-1].get_children())))
#        return [CursorProxy(cursor) for cursor in back]
#
#    def __getitem__(self, item):
#        return self.cursors[item]
#
#    def __repr__(self):
#        """
#        """
#        print_node.node_id = -1
#        return asciitree.draw_tree(self.translation_unit.cursor, node_children, print_node)
#
#def node_children(node):
#    return node.get_children()
#
#def print_node(node):
#    text = node.spelling or node.displayname
#    kind = str(node.kind)[str(node.kind).index('.')+1:]
#    access = node.access_specifier
#    print_node.node_id += 1
#    return '{} {} ({})'.format(kind, text, str(print_node.node_id))
