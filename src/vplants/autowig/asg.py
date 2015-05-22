from pygments import highlight
from pygments.lexers import CLexer, CppLexer, PythonLexer
from pygments.formatters import HtmlFormatter
from clang.cindex import Index, TranslationUnit, CursorKind, Type, TypeKind
import uuid
from mako.template import Template
from path import path
from matplotlib import pyplot
import networkx
from IPython.core import pylabtools
from IPython.html.widgets import interact
import itertools
import os
from tempfile import NamedTemporaryFile
from abc import ABCMeta
from fnmatch import fnmatch
import re
import warnings
import hashlib

from .config import Cursor
try:
    import autowig
except:
    warnings.warn('\'vplants.autowig.autowig\' import failed: only \'libclang\' can be used to parse C/C++ source files', ImportWarning)
from .tools import split_scopes

__all__ = ['AbstractSemanticGraph']

class NodeProxy(object):
    """
    """

    def __init__(self, asg, node):
        self._asg = asg
        self._node = node

    @property
    def id(self):
        return self._node

    @property
    def hash(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self._node)).replace('-', '_')

    def __repr__(self):
        return self._node

    def __dir__(self):
        return sorted([key for key in self._asg._nodes[self._node].keys() if not key.startswith('_')])

    def __getattr__(self, attr):
        try:
            return self._asg._nodes[self._node][attr]
        except:
            raise #AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')

    def _clean_default(self):
        return True

def get_clean(self):
    if not hasattr(self, '_clean'):
        return self._clean_default()
    else:
        return self._clean

def set_clean(self, clean):
    self._asg._nodes[self._node]['_clean'] = clean

def del_clean(self):
    self._asg._nodes[self._node].pop('_clean', False)

NodeProxy.clean = property(get_clean, set_clean, del_clean)
del get_clean, set_clean, del_clean

def get_traverse(self):
    if not '_traverse' in self._asg._nodes[self._node]:
        return True
    else:
        return self._asg._nodes[self._node]['_traverse']

def set_traverse(self, traverse):
    if not traverse:
        self._asg._nodes[self._node]['_traverse'] = traverse

def del_traverse(self):
    self._asg._nodes[self._node].pop('_traverse')

NodeProxy.traverse = property(get_traverse, set_traverse, del_traverse)
del get_traverse, set_traverse, del_traverse

class EdgeProxy(object):
    """
    """

class DirectoryProxy(NodeProxy):
    """
    """

    @property
    def globalname(self):
        return self._node

    @property
    def localname(self):
        return self.globalname[self.globalname.rfind(os.sep, 0, -1)+1:]

    @property
    def parent(self):
        parent = os.sep.join(self.globalname.split(os.sep)[:-2]) + os.sep
        if parent == '':
            parent = os.sep
        return self._asg[parent]

    @property
    def depth(self):
        if self.globalname == os.sep:
            return 0
        else:
            return self.parent.depth+1

    def glob(self, pattern='*', on_disk=False, sort=False):
        if sort:
            return sorted(self.glob(pattern=pattern, on_disk=on_disk), key=lambda node: node.localname)
        else:
            if on_disk:
                dirname = path(self.globalname)
                for name in dirname.glob(pattern=pattern):
                    if name.isdir():
                        self._asg.add_directory(str(name.abspath()))
                    if name.isfile():
                        self._asg.add_file(str(name.abspath()))
            nodes = [self._asg[node] for node in self._asg._syntax_edges[self.id]]
            return [node for node in nodes if fnmatch(node.localname, pattern) and node.traverse]

    def walkdirs(self, pattern='*', on_disk=False, sort=False):
        if sort:
            return sorted(self.walkdirs(pattern=pattern, on_disk=on_disk), key=lambda node: node.localname)
        else:
            if on_disk:
                dirname = path(self.globalname)
                for name in dirname.glob(pattern=pattern):
                    if name.isdir():
                        self._asg.add_directory(str(name.abspath()))
            nodes = [node for node in self.glob(pattern=pattern) if isinstance(node, DirectoryProxy)]
            return nodes+list(itertools.chain(*[node.walkdirs(pattern, on_disk=on_disk) for node in nodes]))

    def walkfiles(self, pattern='*', on_disk=False, sort=False):
        if sort:
            return sorted(self.walkfiles(pattern=pattern, on_disk=on_disk), key=lambda node: node.localname)
        else:
            nodes = itertools.chain(*[node.glob(on_disk=on_disk) for node in self.walkdirs(on_disk=on_disk)])
            return [node for node in self.glob(pattern=pattern) if isinstance(node, FileProxy)]+[node for node in nodes if isinstance(node, FileProxy) and fnmatch(node.globalname, pattern)]

    def makedirs(self):
        if not self.on_disk:
            os.makedirs(self.globalname)
            self._asg._nodes[self.id]['on_disk'] = True

    def remove(self, recursive=False, force=False):
        if self.on_disk:
            if recursive:
                for dirnode in reversed(sorted(self.walkdirs(), key=lambda node: node.depth)):
                    dirnode.remove(False, force=force)
            for filenode in self.glob():
                filenode.remove(force=force)
            os.rmdir(self.globalname)
            self._asg._nodes[self.id]['on_disk'] = False

    def parse(self,  pattern='*.h', flags=None, libclang=False, **kwargs):
        includes = self.walkfiles(pattern=pattern)
        for include in includes:
            include.clean = False
        if flags is None:
            language = kwargs.pop('language')
            if language == 'c++':
                flags = ['-x', 'c++', '-std=c++11', '-Wdocumentation']
            elif language == 'c':
                flags = ['-x', 'c', '-std=c11', '-Wdocumentation']
            else:
                raise ValueError('\'language\' parameter')
        if 'c' in flags:
            for include in includes:
                self._asg._nodes[include.id]['language'] = 'c'
            self._asg._language = 'c'
        if 'c++' in flags:
            for include in includes:
                self._asg._nodes[include.id]['language'] = 'c++'
            self._asg._language = 'c++'
        if libclang:
            index = Index.create()
            tempfilehandler = NamedTemporaryFile(delete=False)
            for include in includes:
                if include.on_disk:
                    tempfilehandler.write('#include \"' + include.globalname + '\"\n')
                else:
                    tempfilehandler.write('\n' + str(include) + '\n')
            tempfilehandler.close()
            tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
            os.unlink(tempfilehandler.name)
        else:
            content = ""
            for include in includes:
                if include.on_disk:
                    content += '#include \"' + include.globalname + '\"\n'
                else:
                    content += '\n' + str(include) + '\n'
            tu = autowig.clang.tooling.build_ast_from_code_with_args(content, flags)
        self._asg._read_translation_unit(tu, libclang)
        del self._asg._language

class FileProxy(NodeProxy):
    """
    """

    @property
    def globalname(self):
        return self._node

    @property
    def localname(self):
        return self.globalname[self.globalname.rfind(os.sep)+1:]

    @property
    def suffix(self):
        return self.localname[self.localname.rfind('.'):]

    def write(self, force=False):
        if not self.is_protected or force:
            parent = self.parent
            if not parent.on_disk:
                parent.makedirs()
            filehandler = open(self.globalname, 'w')
            try:
                filehandler.write(str(self))
            except:
                filehandler.close()
                raise
            else:
                filehandler.close()
        else:
            raise IOError('Protected file on dis on disk')

    def remove(self, force=False):
        if not self.is_protected or force:
            os.remove(self.globalname)
            self._asg._nodes[self.id]['on_disk'] = False

    def __str__(self):
        return self.content

    def md5(self):
        return hashlib.md5(str(self)).hexdigest()

    def _repr_html_(self):
        if hasattr(self, 'language'):
            if self.language == 'c':
                lexer = CLexer()
            elif self.language == 'c++':
                lexer = CppLexer()
            elif self.language == 'py':
                lexer = PythonLexer()
            else:
                raise NotImplementedError('\'language\': '+str(self.language))
            return highlight(str(self), lexer, HtmlFormatter(full = True))
        else:
            raise NotImplementedError()

    @property
    def parent(self):
        return self._asg[os.sep.join(self.globalname.split(os.sep)[:-1]) + os.sep]

    def parse(self, flags=None, libclang=False, **kwargs):
        self.clean = False
        if flags is None:
            language = kwargs.pop('language')
            if language == 'c++':
                flags = ['-x', 'c++', '-std=c++11', '-Wdocumentation']
            elif language == 'c':
                flags = ['-x', 'c', '-std=c11', '-Wdocumentation']
            else:
                raise ValueError('\'language\' parameter')
        if 'c' in flags:
            self._asg._nodes[self.id]['language'] = 'c'
            self._asg._language = 'c'
        if 'c++' in flags:
            self._asg._nodes[self.id]['language'] = 'c++'
            self._asg._language = 'c++'
        if libclang:
            index = Index.create()
            tempfilehandler = NamedTemporaryFile(delete=False)
            if self.on_disk:
                tempfilehandler.write('#include \"' + self.globalname + '\"\n')
            else:
                tempfilehandler.write('\n' + str(self) + '\n')
            tempfilehandler.close()
            tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
            os.unlink(tempfilehandler.name)
        else:
            content = ""
            if include.on_disk:
                content += '#include \"' + include.globalname + '\"\n'
            else:
                content += '\n' + str(include) + '\n'
            tu = autowig.clang.tooling.build_ast_from_code_with_args(content, flags)
        self._asg._read_translation_unit(tu, libclang)
        del self._asg._language

def get_is_protected(self):
    if hasattr(self, '_is_protected'):
        return self._is_protected
    else:
        return self.on_disk

def set_is_protected(self, is_protected):
    self._asg._nodes[self.id]['_is_protected'] = is_protected

def del_is_protected(self):
    self._asg._nodes[self.id].pop('_is_protected', True)

FileProxy.is_protected = property(get_is_protected, set_is_protected, del_is_protected)
del get_is_protected, set_is_protected, del_is_protected

def get_content(self):
    if not hasattr(self, '_content'):
        filepath = path(self.globalname)
        if filepath.exists():
            return "".join(filepath.lines())
        else:
            return ""
    else:
        return self._content

def set_content(self, content):
    self._asg._nodes[self.id]['_content'] = content

def del_content(self):
    self._asg._nodes[self._id].pop('_content', False)

FileProxy.content = property(get_content, set_content, del_content)
del get_content, set_content, del_content

class CodeNodeProxy(NodeProxy):

    @property
    def header(self):
        try:
            return self._asg[self._header]
        except:
            try:
                return self.parent.header
            except:
                return None

    def _clean_default(self):
        header = self.header
        return header is None or header.clean

    @property
    def ancestors(self):
        ancestors = [self.parent]
        while not ancestors[-1].globalname == '::':
            ancestors.append(ancestors[-1].parent)
        return reversed(ancestors)

def get_export(self):
    if not hasattr(self, '_export'):
        return True
    else:
        return self._export

def set_export(self, export):
    if export:
        del self._export
    else:
        self._asg._nodes[self.id]['_export'] = export

def del_export(self):
    self._asg._nodes[self._id].pop('_export', False)

CodeNodeProxy.export = property(get_export, set_export, del_export)
del get_export, set_export, del_export

class FundamentalTypeProxy(CodeNodeProxy):
    """
    http://www.cplusplus.com/doc/tutorial/variables/
    """

    @property
    def globalname(self):
        return self._node.lstrip('::')

    @property
    def localname(self):
        return self.globalname

    def __str__(self):
        return self._node

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

    def __getitem__(self, node):
        if node.startswith('::'):
            return self._asg[node]
        else:
            return self._asg['::'+node]

    @property
    def parent(self):
        return self._asg['::']

class UnexposedTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = '::unexposed'

class CharacterFundamentalTypeProxy(FundamentalTypeProxy):
    """
    """

class CharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    _node = '::char'

class UnsignedCharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    _node = '::unsigned char'

class SignedCharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    _node = '::signed char'

class Char16TypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    _node = "::char16_t"

class Char32TypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    _node = "::char32_t"

class WCharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    _node = "::wchar_t"

class SignedIntegerTypeProxy(FundamentalTypeProxy):
    """
    """

class SignedShortIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::short"

class SignedIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::int"

class SignedLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::long"

class SignedLongLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::long long"

class UnsignedIntegerTypeProxy(FundamentalTypeProxy):
    """
    """

class UnsignedShortIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned short"

class UnsignedIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned int"

class UnsignedLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned long"

class UnsignedLongLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned long long"

class SignedFloatingPointTypeProxy(FundamentalTypeProxy):
    """
    """

class SignedFloatTypeProxy(SignedFloatingPointTypeProxy):
    """
    """

    _node = "::float"

class SignedDoubleTypeProxy(SignedFloatingPointTypeProxy):
    """
    """

    _node = "::double"

class SignedLongDoubleTypeProxy(SignedFloatingPointTypeProxy):
    """
    """

    _node = "::long double"

class BoolTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = "::bool"

class ComplexTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = "::_Complex float"

class NullPtrTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = "::null_ptr"

class VoidTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = "::void"

class TypeSpecifiersProxy(EdgeProxy):
    """
    http://en.cppreference.com/w/cpp/language/declarations
    """

    def __init__(self, asg, source):
        self._asg = asg
        self._source = source

    @property
    def target(self):
        return self._asg[self._asg._type_edges[self._source]["target"]]

    @property
    def specifiers(self):
        return self._asg._type_edges[self._source]["specifiers"]

    @property
    def globalname(self):
        return self.target.globalname + self.specifiers

    @property
    def localname(self):
        return self.target.localname + self.specifiers

    @property
    def is_const(self):
        return self.specifiers.endswith('const')

    @property
    def is_reference(self):
        if self.is_const:
            return self.specifiers.endswith('& const')
        else:
            return self.specifiers.endswith('&')

    @property
    def is_pointer(self):
        if self.is_const:
            return self.specifiers.endswith('* const')
        else:
            return self.specifiers.endswith('*')

    def __str__(self):
        return self.globalname

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

class DeclarationProxy(CodeNodeProxy):
    """
    """

    @property
    def globalname(self):
        return re.sub('::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', '', self.id)

    @property
    def localname(self):
        return split_scopes(self.globalname)[-1]

    @property
    def parent(self):
        return self._asg['::'+'::'.join(split_scopes(self.id)[:-1])]

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

    def __str__(self):
        return self.globalname

class EnumConstantProxy(DeclarationProxy):
    """
    """

class EnumProxy(DeclarationProxy):
    """
    """

    def _clean_default(self):
        if super(EnumProxy, self)._clean_default():
            return True
        elif not self.is_complete:
            return True
        else:
            return False

    @property
    def is_complete(self):
        return len(self._asg._syntax_edges[self._node]) > 0

    @property
    def constants(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

class TypedefProxy(DeclarationProxy):
    """
    """

    @property
    def type(self):
        return TypeSpecifiersProxy(self._asg, self._node)

class VariableProxy(DeclarationProxy):
    """
    """

    @property
    def type(self):
        return TypeSpecifiersProxy(self._asg, self._node)

class FieldProxy(VariableProxy):
    """
    """

class FunctionProxy(DeclarationProxy):
    """
    """

    @property
    def result_type(self):
        return TypeSpecifiersProxy(self._asg, self._node)

    @property
    def nb_parameters(self):
        return len(self._asg._syntax_edges[self._node])

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

    @property
    def parent(self):
        return self._asg['::'+'::'.join(split_scopes(self.globalname)[:-1])]

    @property
    def is_overloaded(self):
        if not hasattr(self, '_is_overloaded'):
            overloads = self._asg["^" + self.globalname + "::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"]
            if len(overloads) == 1:
                self._asg._nodes[self._node]["_is_overloaded"] = False
            else:
                for overload in overloads:
                    self._asg._nodes[overload._node]["_is_overloaded"] = True
        return self._is_overloaded

class MethodProxy(FunctionProxy):
    """
    """

class ConstructorProxy(DeclarationProxy):
    """
    """

    @property
    def nb_parameters(self):
        return len(self._asg._syntax_edges[self._node])

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

    @property
    def parent(self):
        return self._asg['::'+'::'.join(split_scopes(self.globalname)[:-1])]

class DestructorProxy(DeclarationProxy):
    """
    """

class ClassProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/class>_`
    """

    def _clean_default(self):
        if super(ClassProxy, self)._clean_default():
            return True
        elif not self.is_complete:
            return True
        else:
            return False

    @property
    def is_complete(self):
        return len(self.bases()) + len(self.declarations()) > 0

    @property
    def derived(self):
        return len(self._asg._base_edges[self._node]) > 0

    def bases(self, inherited=False):
        bases = []
        for base in self._asg._base_edges[self._node]:
            bases.append(self._asg[base['base']])
            bases[-1].access = base['access']
            bases[-1].virtual_base = base['virtual']
        if not inherited:
            return bases
        else:
            inheritedbases = []
            for base in bases:
                if isinstance(base, TypedefProxy):
                    basebases = base.type.target.bases(True)
                else:
                    basebases = base.bases(True)
                if base.access == 'protected':
                    for basebase in basebases:
                        if basebase.access == 'public':
                            basebase.access = 'protected'
                elif base.access == 'private':
                    for basebase in basebases:
                        basebase.access = 'private'
                inheritedbases += basebases
            return bases+inheritedbases

    @property
    def depth(self):
        if not self.derived:
            return 0
        else:
            if not hasattr(self, '_depth'):
                self._asg._nodes[self.id]['_depth'] = max([base.type.target.depth if isinstance(base, TypedefProxy) else base.depth for base in self.bases()])+1
            return self._depth

    def declarations(self, inherited=False):
        declarations = [self._asg[node] for node in self._asg._syntax_edges[self.id]]
        if not inherited:
            return declarations
        else:
            for base in self.bases(True):
                if isinstance(base, TypedefProxy):
                    basedeclarations = [basedeclaration for basedeclaration in base.type.target.declarations(False) if not basedeclaration.access == 'private']
                else:
                    basedeclarations = [basedeclaration for basedeclaration in base.declarations(False) if not basedeclaration.access == 'private']
                if base.access == 'protected':
                    for basedeclaration in basedeclarations:
                        if basedeclaration.access == 'public':
                            basedeclaration.access = 'protected'
                elif base.access == 'private':
                   for basedeclaration in basedeclarations:
                        basedeclaration.access = 'private'
                declarations += basedeclarations
            return declarations

    def enums(self, inherited=False):
        return [enum for enum in self.declarations(inherited) if isinstance(enum, EnumProxy)]

    def fields(self, inherited=False):
        return [field for field in self.declarations(inherited) if isinstance(field, FieldProxy)]

    def methods(self, inherited=False):
        return [method for method in self.declarations(inherited) if isinstance(method, MethodProxy)]

    def classes(self, inherited=False):
        return [klass for klass in self.declarations(inherited) if isinstance(klass, ClassProxy)]

    @property
    def constructors(self):
        return [constructor for constructor in self.declarations(False) if isinstance(constructor, ConstructorProxy)]

    @property
    def destructor(self):
        try:
            return [destructor for destructor in self.declarations(False) if isinstance(destructor, DestructorProxy)].pop()
        except:
            return None

class NamespaceProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/namespace>_`
    """

    @property
    def header(self):
        return None

    def __init__(self, asg, node):
        super(DeclarationProxy, self).__init__(asg, node)
        if node == '::':
            self._noname = '::'
        else:
            self._noname = 'namespace'

    @property
    def anonymous(self):
        return '-' in self._node

    @property
    def is_empty(self):
        return len(self.declarations(True)) == 0

    def declarations(self, nested=False):
        declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node]]
        if not nested:
            return declarations
        else:
            declarations = [declaration for declaration in declarations if not isinstance(declaration, NamespaceProxy)]
            for nestednamespace in self.namespaces(False):
                for nesteddeclaration in nestednamespace.declarations(True):
                    declarations.append(nesteddeclaration)
            return declarations

    def enums(self, nested=False):
        return [enum for enum in self.declarations(nested) if isinstance(enum, EnumProxy)]

    def enum_constants(self, nested=False):
        return [enum_constant for enum_constant in self.declarations(nested) if isinstance(enum_constant, EnumConstantProxy)]

    def variables(self, nested=False):
        return [variable for variable in self.declarations(nested) if isinstance(variable, VariableProxy)]

    def functions(self, nested=False):
        return [function for function in self.declarations(nested) if isinstance(function, FunctionProxy)]

    def classes(self, nested=False):
        return [klass for klass in self.declarations(nested) if isinstance(klass, ClassProxy)]

    def namespaces(self, nested=False):
        if not nested:
            return [namespace for namespace in self.declarations(nested) if isinstance(namespace, NamespacePRoxy)]
        else:
            nestednamespaces = []
            namespaces = self.namespaces(False)
            while len(namespaces):
                namespace = namespaces.pop()
                nestednamespaces.append(namespace)
                namespaces.extend(namespace.namespaces(False))
            return nestednamespaces

class AbstractSemanticGraph(object):

    def __init__(self, *args, **kwargs):
        self._nodes = dict()
        self._syntax_edges = dict()
        self._base_edges = dict()
        self._type_edges = dict()
        self._symbol_edges = dict()

    def __len__(self):
        return len(self._nodes)

    def add_directory(self, dirname):
        dirname = path(dirname).abspath()
        initname = str(dirname)
        if not initname.endswith(os.sep):
            initname += os.sep
        if not initname in self._nodes:
            idparent = initname
            if not idparent in self._syntax_edges:
                self._syntax_edges[idparent] = []
            while not dirname == os.sep:
                idnode = idparent
                if not idnode.endswith(os.sep):
                    idnode += os.sep
                if not idnode in self._nodes:
                    self._nodes[idnode] = dict(proxy=DirectoryProxy,
                            on_disk=dirname.exists())
                    dirname = dirname.parent
                    idparent = str(dirname)
                    if not idparent.endswith(os.sep):
                        idparent += os.sep
                    if not idparent in self._syntax_edges:
                        self._syntax_edges[idparent] = []
                    self._syntax_edges[idparent].append(idnode)
                else:
                    break
            if dirname == os.sep and not os.sep in self._nodes:
                self._nodes[os.sep] = dict(proxy=DirectoryProxy,
                            on_disk=dirname.exists())
        return self[initname]

    def add_file(self, filename, **kwargs):
        filename = path(filename).abspath()
        initname = str(filename)
        proxy = kwargs.pop('proxy', FileProxy)
        if not initname in self._nodes:
            idnode = str(filename)
            self._nodes[idnode] = dict(proxy=proxy,
                    on_disk=filename.exists(),
                    **kwargs)
            idparent = str(filename.parent)
            if not idparent.endswith(os.sep):
                idparent += os.sep
            if not idparent in self._syntax_edges:
                self._syntax_edges[idparent] = []
            self._syntax_edges[idparent].append(idnode)
            self.add_directory(idparent)
        else:
            self._nodes[initname].update(kwargs)
        return self[initname]

    def write(self, pattern=None, force=False):
        for node in self.files(pattern=pattern):
            try:
                node.write(force=force)
            except IOError as error:
                warnings.warn(str(error), Warning)

    def nodes(self, pattern=None):
        if pattern is None:
            return [self[node] for node in self._nodes.keys()]
        else:
            return [self[node] for node in self._nodes.keys() if re.match(pattern, node)]

    def directories(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, DirectoryProxy)]

    def files(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, FileProxy)]

    def fundamental_types(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, FundamentalTypeProxy)]

    def declarations(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, FundamentalTypeProxy)]

    def typedefs(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, TypedefProxy)]

    def enums(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, EnumProxy)]

    def functions(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, FunctionProxy)]

    def classes(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, ClassProxy)]

    def namespaces(self, pattern=None):
        return [node for node in self.nodes(pattern) if isinstance(node, NamespaceProxy)]

    def to_object(self, func2method=True):
        """
        """

        if func2method:
            for klass in [klass for klass in self['::'].classes() if hasattr(klass, '_header') and klass.header.language == 'c' and klass.traverse]:
                for function in [function for function in self['::'].functions() if function.traverse]:
                    mv = False
                    rtype = function.result_type
                    if rtype.target.id == klass.id:
                        self._nodes[function.id].update(proxy=MethodProxy,
                                is_static=True,
                                is_virtual=False,
                                is_pure_virtual=False,
                                is_const=ptype.is_const,
                                as_constructor=True,
                                access='public')
                        mv = True
                    elif function.nb_parameters > 0:
                        ptype = function.parameters[0].type
                        if ptype.target.id == klass.id and (ptype.is_reference or ptype.is_pointer):
                            self._nodes[function.id].update(proxy=MethodProxy,
                                    is_static=False,
                                    is_virtual=False,
                                    is_pure_virtual=False,
                                    is_const=ptype.is_const,
                                    access='public')
                            mv = True
                    if mv:
                        self._syntax_edges[function.parent.id].remove(function.id)
                        self._syntax_edges[klass.id].append(function.id)

    def compute_clean(self):
        temp = [node for node in self.nodes() if not node.clean]
        while len(temp) > 0:
            node = temp.pop()
            node.clean = False
            parent = node.parent
            if parent.clean:
                temp.append(parent)
            else:
                parent.clean = False
            if hasattr(node, 'header'):
                header = node.header
                if not header is None:
                    if header.clean:
                        temp.append(header)
                    else:
                        node.header.clean = False
            if isinstance(node, (TypedefProxy, VariableProxy)):
                underlying_type = node.type.target
                if underlying_type.clean:
                    temp.append(underlying_type)
                else:
                    underlying_type.clean = False
            elif isinstance(node, FunctionProxy):
                result_type = node.result_type.target
                result_type.clean = False
                for parameter in node.parameters:
                    if parameter.clean:
                        temp.append(parameter)
                    else:
                        parameter.clean = False
            elif isinstance(node, ConstructorProxy):
                for parameter in node.parameters:
                    if parameter.clean:
                        temp.append(parameter)
                    else:
                        parameter.clean = False
            elif isinstance(node, ClassProxy):
                for base in node.bases():
                    if base.clean:
                        temp.append(base)
                    else:
                        base.clean = False

    def clean(self):
        """
        """
        self.compute_clean()

        nodes = [node for node in self.nodes() if node.clean]
        for node in nodes:
            self._syntax_edges[node.parent.id].remove(node.id)

        for node in nodes:
            self._nodes.pop(node.id)
            self._syntax_edges.pop(node.id, None)
            self._base_edges.pop(node.id, None)
            self._type_edges.pop(node.id, None)

    def to_networkx(self, pattern='(.*)', specialization=True, type=True, base=True, directories=True, files=True, fundamentals=True, variables=True):
        graph = networkx.DiGraph()

        class Filter(object):

            __metaclass__ = ABCMeta

        if not directories:
            Filter.register(DirectoryProxy)
        if not files:
            Filter.register(FileProxy)
        if not fundamentals:
            Filter.register(FundamentalTypeProxy)
        if not variables:
            Filter.register(VariableProxy)
        for node in self.nodes():
            if not isinstance(node, Filter):
                graph.add_node(node.id)
        for source, targets in self._syntax_edges.iteritems():
            if not isinstance(self[source], Filter):
                for target in targets:
                    if not isinstance(self[target], Filter):
                        graph.add_edge(source, target, color='k', linestyle='solid')
        if type:
            for source, target in self._type_edges.iteritems():
                if not isinstance(self[source], Filter) and not isinstance(self[target['target']], Filter):
                    graph.add_edge(source, target['target'], color='r', linestyle='solid')
        if base:
            for source, targets in self._base_edges.iteritems():
                if not isinstance(self[source], Filter):
                    for target in targets:
                        if not isinstance(self[target], Filter):
                            graph.add_edge(source, target['base'], color='m', linestyle='solid')

        return graph.subgraph([node for node in graph.nodes() if re.match(pattern, node)])

    def _read_translation_unit(self, tu, libclang):
        """
        """
        if not '::' in self._nodes:
            self._nodes['::'] = dict(proxy = NamespaceProxy)
        if not '::' in self._syntax_edges:
            self._syntax_edges['::'] = []

        fundamentals = [FundamentalTypeProxy]
        while len(fundamentals) > 0:
            fundamental = fundamentals.pop()
            if hasattr(fundamental, '_node'):
                if not fundamental._node in self._nodes:
                    self._nodes[fundamental._node] = dict(proxy = fundamental)
                if not fundamental._node in self._syntax_edges['::']:
                    self._syntax_edges['::'].append(fundamental._node)
            fundamentals.extend(fundamental.__subclasses__())

        if libclang:
            for child in tu.cursor.get_children():
                self._read_decl(child, '::', libclang)
        else:
            for child in tu.get_children():
                self._read_decl(child, '::', libclang)

    def _read_qualified_type(self, qtype, libclang):
        if libclang:
            specifiers = ''
            while True:
                if qtype.kind is TypeKind.POINTER:
                    specifiers = ' *' + ' const'*qtype.is_const_qualified() + specifiers
                    qtype = qtype.get_pointee()
                elif qtype.kind is TypeKind.LVALUEREFERENCE:
                    specifiers = ' &' + specifiers
                    qtype = qtype.get_pointee()
                elif qtype.kind is TypeKind.RVALUEREFERENCE:
                    specifiers = ' &&' + specifiers
                    qtype = qtype.get_pointee()
                elif qtype.kind in [TypeKind.RECORD, TypeKind.TYPEDEF, TypeKind.ENUM, TypeKind.UNEXPOSED]:
                    spelling = '::' + qtype.get_declaration().type.spelling
                    if qtype.is_const_qualified():
                        specifiers = ' const' + specifiers
                    if qtype.is_volatile_qualified():
                        specifiers = ' volatile' + specifiers
                    return self[spelling].id, specifiers
                else:
                    target, _specifiers = self._read_builtin_type(qtype, libclang)
                    return target, _specifiers + specifiers
        else:
            specifiers = ' const' * qtype.is_const_qualified() + ' volatile' *  qtype.is_volatile_qualified()
            ttype = qtype.get_type_ptr_or_null()
            while True:
                if ttype is None:
                    raise NotImplementedError('No type accessible')
                elif ttype.is_builtin_type():
                    return self._read_builtin_type(ttype, clang), specifiers
                elif any([ttype.is_structure_or_class_type(), ttype.is_enumeral_type(), ttype.is_union_type()]):
                    return self._read_tag(ttype.get_as_tag_decl(),
                            '::'+'::'.join(split_scopes(ttype.get_as_tag_decl().spelling())[:-1]),
                            libclang)[0], specifiers
                elif ttype.is_pointer_type():
                    qtype = ttytpe.get_pointee_type()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' + qtype.is_volatile_qualified() + ' *' + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                elif ttype.is_rvalue_reference_type():
                    qtype = ttytpe.get_pointee_type()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' + qtype.is_volatile_qualified() + ' &&' + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                elif ttype.is_lvalue_reference_type():
                    qtype = ttytpe.get_pointee_type()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' + qtype.is_volatile_qualified() + ' &' + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                else:
                    raise NotImplementedError('Type: ' + str(ttype.get_type_class()))

    def _read_builtin_type(self, btype, libclang):
        if libclang:
            if btype.kind in [TypeKind.CHAR_U, TypeKind.CHAR_S]:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return CharTypeProxy._node, specifiers
            elif btype.kind is TypeKind.UCHAR:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return UnsignedCharTypeProxy._node, specifiers
            elif btype.kind is TypeKind.SCHAR:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedCharTypeProxy._node, specifiers
            elif btype.kind is TypeKind.CHAR16:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return Char16TypeProxy._node, specifiers
            elif btype.kind is TypeKind.CHAR32:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return Char32TypeProxy._node, specifiers
            elif btype.kind is TypeKind.WCHAR:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return WCharTypeProxy._node, specifiers
            elif btype.kind is TypeKind.SHORT:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedShortIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.INT:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.LONG:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedLongIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.LONGLONG:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedLongLongIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.USHORT:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return UnsignedShortIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.UINT:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return UnsignedIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.ULONG:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return UnsignedLongIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.ULONGLONG:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return UnsignedLongLongIntegerTypeProxy._node, specifiers
            elif btype.kind is TypeKind.FLOAT:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedFloatTypeProxy._node, specifiers
            elif btype.kind is TypeKind.DOUBLE:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedDoubleTypeProxy._node, specifiers
            elif btype.kind is TypeKind.LONGDOUBLE:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return SignedLongDoubleTypeProxy._node, specifiers
            elif btype.kind is TypeKind.BOOL:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return BoolTypeProxy._node, specifiers
            elif btype.kind is TypeKind.COMPLEX:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return ComplexTypeProxy._node, specifiers
            elif btype.kind is TypeKind.VOID:
                if btype.is_const_qualified():
                    specifiers = ' const'
                else:
                    specifiers = ''
                return VoidTypeProxy._node, specifiers
            else:
                raise NotImplementedError('Type: ' + str(btype.kind))
        else:
            kind = btype.get_kind()
            if btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Bool):
                return BoolTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Char_U):
                return UnsignedCharTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Char_S):
                return CharTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Char32):
                return Char32TypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Char16):
                return Char16TypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Double):
                return SignedDoubleTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Float):
                return SignedFloatTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Int):
                return SignedIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.LongLong):
                return SignedLongLongIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Long):
                return SignedLongIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.LongDouble):
                return SignedLongDoubleTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.NullPtr):
                return NullPtrTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Short):
                return SignedShortIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.SChar):
                return SignedCharTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.ULongLong):
                return UnsignedLongLongIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.UChar):
                return UnsignedCharTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.ULong):
                return nsignedLongIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.UInt):
                return UnsignedIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.UShort):
                return UnsignedShortIntegerTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.Void):
                return VoidTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.WChar_S):
                return WCharTypeProxy._node
            elif btype.is_specific_builtin_type(autowig.clang._builtin_type.Kind.WChar_U):
                return WCharTypeProxy._node
            else:
                raise NotImplementedError('Type: ' + str(btype.get_class_type()))

    def _read_enum(self, decl, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            if decl.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in decl.get_children():
                    children.extend(self._read_enum_constant(child, spelling, libclang))
                filename = str(path(str(decl.location.file)).abspath())
                self.add_file(filename, language=self._language)
                for childspelling in children:
                    self._nodes[childspelling]['_header'] = filename
                return children
            else:
                if not spelling in self._nodes :
                    self._syntax_edges[spelling] = []
                    self._nodes[spelling] = dict(proxy=EnumProxy)
                    self._syntax_edges[scope].append(spelling)
                elif not self[spelling].is_complete:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges[scope].append(spelling)
                if not self[spelling].is_complete:
                    for child in decl.get_children():
                        self._read_enum_constant(child, spelling, libclang)
                    filename = str(path(str(decl.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                return [spelling]
        else:
            spelling = decl.spelling()
            filename = str(path(str(decl.get_filename())).abspath())
            self.add_file(filename, language=self._language)
            if spelling == scope:
                children = []
                for child in decl.get_children():
                    children.extend(self._read_enum_constant(child, scope, libclang))
                for child in children:
                    self._nodes[child]['_header'] = filename
                return children
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(proxy=EnumProxy)
                    self._syntax_edges[spelling] = []
                    self._syntax_edges[scope].append(spelling)
                elif not self[spelling].is_complete:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges[scope].append(spelling)
                if not self[spelling].is_complete:
                    for child in decl.get_children():
                        self._read_enum_constant(child, spelling, libclang)
                    self._nodes[spelling]['_header'] = filename
                return [spelling]

    def _read_enum_constant(self, decl, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            self._nodes[spelling] = dict(proxy=EnumConstantProxy)
            self._syntax_edges[scope].append(spelling)
            return [spelling]
        else:
            spelling = decl.spelling()
            self._nodes[spelling] = dict(proxy=EnumConstantProxy)
            self._syntax_edges[scope].append(spelling)
            return [spelling]

    def _read_typedef(self, typedef, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + typedef.spelling
            else:
                spelling = scope + typedef.spelling
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=TypedefProxy)
                try:
                    target, specifiers = self._read_qualified_type(typedef.underlying_type, scope, libclang)
                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                except:
                    children = [child for child in typedef.get_children()]
                    if not len(children) == 1:
                        self._nodes.pop(spelling)
                        warnings.warn('Typedef interpretation failed for \'' + spelling + '\'')
                        return []
                    else:
                        try:
                            self._syntax_edges[scope].append(spelling)
                            child = children.pop()
                            if child.kind is CursorKind.TYPE_REF:
                                self._type_edges[spelling]['target'] = self[scope][child.type.spelling].id
                                filename = str(path(str(typedef.location.file)).abspath())
                                self.add_file(filename, language=self._language)
                                self._nodes[spelling]['_header'] = filename
                            elif child.kind in [CursorKind.UNION_DECL, CursorKind.STRUCT_DECL]:
                                if child.spelling == '':
                                    self._nodes[spelling] = dict(proxy=ClassProxy,
                                            default_access='public')
                                    self._syntax_edges[spelling] = []
                                    self._base_edges[spelling] = []
                                    for child in child.get_children():
                                        for childspelling in self._read_decl(child, spelling, libclang):
                                            self._nodes[childspelling]["access"] = 'public'
                                            dict.pop(self._nodes[childspelling], "header", None)
                                else:
                                    self._type_edges[spelling]['target'] = self[scope][child.type.spelling].id
                                filename = str(path(str(typedef.location.file)).abspath())
                                self.add_file(filename, language=self._language)
                                self._nodes[spelling]['_header'] = filename
                            elif child.kind is CursorKind.ENUM_DECL:
                                if child.spelling == '':
                                    filename = str(path(str(typedef.location.file)).abspath())
                                    self.add_file(filename, language=self._language)
                                    self._nodes[spelling] = dict(proxy=EnumProxy)
                                    self._syntax_edges[spelling] = []
                                    for child in child.get_children():
                                        self._read_enum_constant(child, spelling, libclang)
                                else:
                                    self._type_edges[spelling]['target'] = self[scope][child.type.spelling].id
                                filename = str(path(str(typedef.location.file)).abspath())
                                self.add_file(filename, language=self._language)
                                self._nodes[spelling]['_header'] = filename
                            else:
                                raise NotImplementedError()
                            return [spelling]
                        except:
                            self._nodes.pop(spelling)
                            self._syntax_edges[scope].remove(spelling)
                            warnings.warn('Typedef interpretation failed for \'' + spelling + '\'')
                            return []
                        else:
                            filename = str(path(str(typdef.location.file)).abspath())
                            self.add_file(filename, language=self._language)
                            self._nodes[spelling]['_header'] = filename
                            return [spelling]
                else:
                    self._syntax_edges[scope].append(spelling)
                    filename = str(path(str(typedef.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    return [spelling]
            else:
                return [spelling]
        else:
            spelling = typedef.spelling()
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=TypedefProxy)
                self._syntax_edges[scope].append(spelling)
                self._read_type(typedef.get_underlying_type(), spelling)
                return [spelling]
            else:
                return []

    def _read_variable(self, decl, scope, libclang):
        if libclang:
            if any(child.kind in [CursorKind.TEMPLATE_NON_TYPE_PARAMETER, CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_TEMPLATE_PARAMETER] for child in decl.get_children()):
                warnings.warn('Template variable not read')
                return []
            else:
                if not scope.endswith('::'):
                    spelling = scope + "::" + decl.spelling
                else:
                    spelling = scope + decl.spelling
                self._nodes[spelling] = dict(proxy=VariableProxy)
                filename = str(path(str(decl.location.file)).abspath())
                self.add_file(filename, language=self._language)
                self._nodes[spelling]['_header'] = filename
            self._syntax_edges[scope].append(spelling)
            try:
                target, specifiers = self._read_qualified_type(decl.type, libclang)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Exception as error:
                self._syntax_edges[scope].remove(spelling)
                self._nodes.pop(spelling)
                warnings.warn(str(error))
                return []
            else:
                return [spelling]
        else:
            if isinstance(decl, autowig.clang.VarTemplateSpecializationDecl):
                return []
            else:
                spelling = decl.spelling()
                if isinstance(decl, autowig.clang.ParmVarDecl):
                    if not scope.endswith('::'):
                        spelling = scope + '::' + spelling
                    else:
                        spelling = scope + spelling
                self._nodes[spelling] = dict(proxy=VariableProxy)
                self._syntax_edges[scope].append(spelling)
                try:
                    target, specifiers = self._read_qualified_type(decl.get_type(), scope, libclang)
                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                except Exception as error:
                    self._syntax_edges[scope].remove(spelling)
                    self._nodes.pop(spelling)
                    warnings.warn(str(error))
                    return []
                else:
                    if not isinstance(decl, autowig.ParmVarDecl):
                        filename = str(path(str(decl.get_filename())).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                    return [spelling]

    def _read_function(self, decl, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            if decl.kind in [CursorKind.DESTRUCTOR, CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR] and decl.lexical_parent.kind is CursorKind.NAMESPACE:
                return []
            else:
                if not decl.kind is CursorKind.DESTRUCTOR:
                    spelling = spelling + '::' + str(uuid.uuid4())
                if decl.kind is CursorKind.FUNCTION_DECL:
                    self._nodes[spelling] = dict(proxy=FunctionProxy)
                    if not decl.location is None:
                        filename = str(path(str(decl.location.file)).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                elif decl.kind is CursorKind.CXX_METHOD:
                    self._nodes[spelling] = dict(proxy=MethodProxy,
                            is_static=decl.is_static_method(),
                            is_virtual=True,
                            is_const=False,
                            is_pure_virtual=True)
                elif decl.kind is CursorKind.CONSTRUCTOR:
                    self._nodes[spelling] = dict(proxy=ConstructorProxy)
                else:
                    self._nodes[spelling] = dict(proxy=DestructorProxy, is_virtual=True)
                self._syntax_edges[spelling] = []
                self._syntax_edges[scope].append(spelling)
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter("error")
                        for child in decl.get_children():
                            if child.kind is CursorKind.PARM_DECL:
                                self._read_variable(child, spelling, libclang)
                        if not decl.kind in [CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:
                            target, specifiers = self._read_qualified_type(decl.result_type, libclang)
                            self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                except Exception as error:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges.pop(spelling)
                    self._nodes.pop(spelling)
                    if not spelling.endswith('::'):
                        spelling += '::'
                    for child in decl.get_children():
                        if child.kind is CursorKind.PARM_DECL:
                            self._nodes.pop(spelling + child.spelling, None)
                            self._syntax_edges.pop(spelling + child.spelling, None)
                            self._type_edges.pop(spelling, None)
                    warnings.warn(str(error))
                    return []
                else:
                    return [spelling]
        else:
            spelling = decl.spelling()
            if not isinstance(decl, autowig.clang.CXXDestructorDecl):
                spelling += '::' + str(uuid.uuid4())
            if isinstance(decl, autowig.clang.CXXMethodDecl):
                if isinstance(decl, autowig.clang.CXXConversionDecl):
                    warnings.warn('Conversion declaration not read')
                    return []
                else:
                    if not isinstance(decl, autowig.clang.CXXDestructorDecl):
                        self._syntax_edges[spelling] = []
                        self._syntax_edges[scope].append(spelling)
                        try:
                            with warnings.catch_warnings() as w:
                                warnings.simplefilter('error')
                                for child in decl.get_children():
                                    self._read_variable(child, spelling, libclang)
                            if not isinstance(decl, autowig.clang.CXXConstructorDecl):
                                target, specifiers = self._read_qualified_type(decl.get_return_type(), spelling, libclang)
                                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                                self._nodes[spelling] = dict(proxy=MethodProxy,
                                        is_static=decl.is_static(),
                                        is_const=decl.is_const(),
                                        is_volatile=decl.is_volatile(),
                                        is_virtual=decl.is_virtual())
                            else:
                                self._nodes[spelling] = dict(proxy=ConstructorProxy,
                                        virtual=decl.is_virtual())
                        except Exception as error:
                            self._syntax_edges[scope].remove(spelling)
                            self._syntax_edges.pop(spelling)
                            if not spelling.endswith('::'):
                                spelling += '::'
                            for child in decl.get_children():
                                self._nodes.pop(spelling + child.spelling(), None)
                                self._syntax_edges.pop(spelling + child.spelling(), None)
                            self._type_edges.pop(spelling, None)
                            warnings.warn(str(error))
                            return []
                        else:
                            return [spelling]
                    else:
                        if not spelling in self._nodes:
                            self._nodes[spelling] = dict(proxy=DestructorProxy,
                                    virtual=decl.is_virtual())
                            self._syntax_edges[scope].append(spelling)
                        else:
                            return [spelling]
            else:
                self._syntax_edges[spelling] = []
                self._syntax_edges[scope].append(spelling)
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter('error')
                        for child in decl.get_children():
                            self._read_variable(child, spelling, libclang)
                        target, specifiers = self._read_qualified_type(decl.get_return_type(), spelling, libclang)
                        self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                        self._nodes[spelling] = dict(proxy=FunctionProxy)
                except Exception as error:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges.pop(spelling)
                    if not spelling.endswith('::'):
                        spelling += '::'
                    for child in decl.get_children():
                        self._nodes.pop(spelling + child.spelling(), None)
                        self._syntax_edges.pop(spelling + child.spelling(), None)
                    self._type_edges.pop(spelling, None)
                    warnings.warn(str(error))
                    return []
                else:
                    filename = str(path(str(decl.get_filename())).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    return [spelling]

    def _read_field(self, decl, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            self._nodes[spelling] = dict(proxy=FieldProxy,
                    is_mutable=False,
                    is_static=False)
            self._syntax_edges[scope].append(spelling)
            try:
                target, specifiers = self._read_qualified_type(decl.type, libclang)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Exception as error:
                self._syntax_edges[scope].remove(spelling)
                self._nodes.pop(spelling)
                warnings.warn(str(error))
                return []
            else:
                return [spelling]
        else:
            spelling = decl.spelling()
            self._nodes[spelling] = dict(proxy=FieldProxy,
                    is_mutable=decl.is_mutable(),
                    is_static=False) # TODO
            self._syntax_edges[scope].append(spelling)
            try:
                target, specifiers = self._read_qualified_type(decl.get_type(), scope, libclang)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Exception as error:
                self._syntax_edges[scope].remove(spelling)
                self._nodes.pop(spelling)
                warnings.warn(str(error))
                return []
            else:
                return [spelling]

    def _read_tag(self, decl, scope, libclang):
        if libclang:
            if decl.spelling == '':
                warnings.warn('Anonymous struc/union/class not read')
                return []
            elif not decl.spelling == decl.displayname:
                warnings.warn('Class template specialization not read')
                return []
            else:
                if not scope.endswith('::'):
                    spelling = scope + "::" + decl.spelling
                else:
                    spelling = scope + decl.spelling
                if not spelling in self._nodes:
                    if decl.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
                        self._nodes[spelling] = dict(proxy=ClassProxy,
                                default_access='public',
                                is_abstract=True,
                                is_copyable=False)
                    elif decl.kind is CursorKind.CLASS_DECL:
                        self._nodes[spelling] = dict(proxy=ClassProxy,
                                    default_access='private',
                                    is_abstract=True,
                                    is_copyable=False)
                    self._syntax_edges[spelling] = []
                    self._base_edges[spelling] = []
                    self._syntax_edges[scope].append(spelling)
                elif not self[spelling].is_complete:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges[scope].append(spelling)
                if not self[spelling].is_complete:
                    for child in decl.get_children():
                        if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                            childspelling = '::' + child.type.spelling
                            if childspelling in self._nodes:
                                access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                                self._base_edges[spelling].append(dict(base=self[childspelling].id,
                                    access=access,
                                    virtual=False))
                            else:
                                warnings.warn('Base not found')
                        else:
                            for childspelling in self._read_decl(child, spelling, libclang):
                                self._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                                dict.pop(self._nodes[childspelling], "_header", None)
                    if self[spelling].is_complete:
                        filename = str(path(str(decl.location.file)).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                return [spelling]
        else:
            if isinstance(decl, autowig.clang.EnumDecl):
                return self._read_enum(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.ClassTemplatePartialSpecializationDecl):
                return []
            else:
                spelling = decl.spelling()
                if spelling == scope:
                    warnings.warn('Anonymous struct/union/class not read')
                    return []
                else:
                    if decl.is_class():
                        default_access = 'private'
                    else:
                        default_access = 'public'
                    if not spelling in self._nodes:
                        self._nodes[spelling] = dict(proxy=ClassProxy,
                                default_access=default_access)
                    if not self[spelling].is_complete:
                        if isinstance(decl, CXXRecordDecl):
                            self._nodes[spelling]['is_abstract'] = decl.is_abstract()
                            self._nodes[spelling]['is_copyable'] = decl.is_copyable()
                        else:
                            self._nodes[spelling]['is_abstract'] = False
                            self._nodes[spelling]['is_copyable'] = True
                    if not self[spelling].is_complete:
                        for base in decl.get_bases():
                            basespelling, specifiers = self._read_qualified_type(base.get_type(), libclang)
                            self._base_edges[spelling].append(dict(base=self[basespelling].id,
                                access=str(base.get_access_specifier()).strip('AS_'),
                                virtual=False))
                        for base in decl.get_virtual_bases():
                            basespelling, specifiers = self._read_qualified_type(base.get_type(), libclang)
                            self._base_edges[spelling].append(dict(base=self[basespelling].id,
                                access=str(base.get_access_specifier()).strip('AS_'),
                                virtual=True))
                        for child in decl.get_children():
                            access = str(child.get_access_specifier()).strip('AS_')
                            for childspelling in self._read_decl(child, spelling, libclang):
                                self._nodes[childspelling]["access"] = access
                                dict.pop(self._nodes[childspelling], "_header", None)
                        if self[spelling].is_complete:
                            filename = str(path(str(decl.get_filename())).abspath())
                            self.add_file(filename, language=self._language)
                            self._nodes[spelling]['_header'] = filename
                    return [spelling]

    def _read_namespace(self, decl, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            if decl.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in decl.get_children():
                    children.extend(self._read_decl(child, spelling, libclang))
                return children
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(proxy=NamespaceProxy)
                    self._syntax_edges[spelling] = []
                if not spelling in self._syntax_edges[scope]:
                    self._syntax_edges[scope].append(spelling)
                for child in decl.get_children():
                    self._read_decl(child, spelling, libclang)
                return [spelling]
        else:
            spelling = decl.spelling()
            if spelling == scope:
                children = []
                for child in decl.get_children():
                    children.extend(self._read_decl(child, spelling, libclang))
                return children
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(proxy=NamespaceProxy)
                    self._syntax_edges[spelling] = []
                if not spelling in self._syntax_edges[scope]:
                    self._syntax_edges[scope].append(spelling)
                for child in decl.get_children():
                    self._read_decl(child, spelling, libclang)
                return [spelling]

    def _read_decl(self, decl, scope, libclang):
        """
        """
        if libclang:
            if decl.kind is CursorKind.UNEXPOSED_DECL:
                if decl.spelling == '':
                    children = []
                    for child in decl.get_children():
                        children.extend(self._read_decl(child, scope, libclang))
                    return children
                else:
                    warnings.warn('Named unexposed declaration not read')
                    return []
            elif decl.kind is CursorKind.ENUM_DECL:
                return self._read_enum(decl, scope, libclang)
            elif decl.kind is CursorKind.ENUM_CONSTANT_DECL:
                return self._read_enum_constant(decl, scope, libclang)
            elif decl.kind is CursorKind.TYPEDEF_DECL:
                return self._read_typedef(decl, scope, libclang)
            elif decl.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL]:
                return self._read_variable(decl, scope, libclang)
            elif decl.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
                    CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
                return self._read_function(decl, scope, libclang)
            elif decl.kind is CursorKind.FIELD_DECL:
                return self._read_field(decl, scope, libclang)
            elif decl.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL, CursorKind.CLASS_DECL]:
                return self._read_tag(decl, scope, libclang)
            elif decl.kind is CursorKind.NAMESPACE:
                return self._read_namespace(decl, scope, libclang)
            elif decl.kind in [CursorKind.NAMESPACE_ALIAS, CursorKind.FUNCTION_TEMPLATE,
                    CursorKind.USING_DECLARATION, CursorKind.USING_DIRECTIVE,
                    CursorKind.UNEXPOSED_ATTR, CursorKind.CLASS_TEMPLATE,
                    CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
                    CursorKind.CXX_ACCESS_SPEC_DECL, CursorKind.CONVERSION_FUNCTION]:
                return []
            else:
                warnings.warn('Undefined behaviour for \'' + str(decl.kind) + '\' declaration')
                return []
        else:
            if isinstance(decl, autowig.clang.LinkageSpecDecl):
                language = self._language
                if decl.get_language() is autowig.clang._linkage_spec_decl.lang_c:
                    self._language = 'c'
                else:
                    self._language = 'c++'
                children = []
                for child in decl.get_children():
                    children = self._read_decl()
                self._language = language
                return children
            elif isinstance(decl, autowig.clang.EnumConstantDecl):
                return self._read_enum_constant(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.VarDecl):
                return self._read_variable(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.FunctionDecl):
                return self._read_function(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.FieldDecl):
                return self._read_field(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.TagDecl):
                return self._read_tag(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.NamespaceDecl):
                return self._read_namespace(decl, scope, libclang)
            elif isinstance(decl, (autowig.clang.AccessSpecDecl,
                autowig.clang.BlockDecl, autowig.clang.CapturedDecl,
                autowig.clang.ClassScopeFunctionSpecializationDecl,
                autowig.clang.EmptyDecl, autowig.clang.FileScopeAsmDecl,
                autowig.clang.FriendDecl, autowig.clang.FriendTemplateDecl,
                autowig.clang.StaticAssertDecl, autowig.clang.LabelDecl,
                autowig.clang.NamespaceAliasDecl, autowig.clang.TemplateDecl,
                autowig.clang.TemplateTypeParmDecl, autowig.clang.UsingDecl,
                autowig.clang.UsingDirectiveDecl, autowig.clang.UsingShadowDecl,
                autowig.clang.IndirectFieldDecl, autowig.clang.UnresolvedUsingValueDecl, autowig.clang.TypedefNameDecl)):
                return []
            else:
                warnings.warn('Undefinied behavious for \'' + decl.__class__.__name__ + '\' declaration')
                return []

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if not node in self._nodes:
            try:
                pattern = re.compile(node)
                return [self[_node] for _node in self._nodes if pattern.match(_node)]
            except:
                raise
                #ValueError('`node` parameter is not a valid regex pattern')
        else:
            return self._nodes[node]["proxy"](self, node)

    def _ipython_display_(self):
        global __asg__
        __asg__ = self
        interact(plot,
                layout=('graphviz', 'circular', 'random', 'spring', 'spectral'),
                size=(0., 60., .5),
                aspect=(0., 1., .01),
                specialization=True,
                type=False,
                base=True,
                fundamentals=False,
                variables=False,
                directories=True,
                files=True,
                pattern='(.*)')

def plot(layout='graphviz', size=16, aspect=.5, invert=False, pattern='(.*)', specialization=True, type=False, base=True, directories=True, files=True, fundamentals=False, variables=False, **kwargs):
    global __asg__
    graph = __asg__.to_networkx(pattern,
            specialization=specialization,
            type=type,
            base=base,
            directories=directories,
            files=files,
            fundamentals=fundamentals,
            variables=variables)
    mapping = {j : i for i, j in enumerate(graph.nodes())}
    graph = networkx.relabel_nodes(graph, mapping)
    layout = getattr(networkx, layout+'_layout')
    nodes = layout(graph)
    if invert:
        fig = pyplot.figure(figsize=(size*aspect, size))
    else:
        fig = pyplot.figure(figsize=(size, size*aspect))
    axes = fig.add_subplot(1,1,1)
    axes.set_axis_off()
    mapping = {j : i for i, j in mapping.iteritems()}
    xmin = float("Inf")
    xmax = -float("Inf")
    ymin = float("Inf")
    ymax = -float("Inf")
    for node in graph.nodes():
        xmin = min(xmin, nodes[node][0])
        xmax = max(xmax, nodes[node][0])
        ymin = min(ymin, nodes[node][1])
        ymax = max(ymax, nodes[node][1])
        asgnode = __asg__[mapping[node]]
        nodes[node] = axes.annotate(asgnode.localname, nodes[node],
                xycoords = "data",
                color = 'k',
                bbox = dict(
                    boxstyle = 'round',
                    fc = 'w',
                    lw = 2.,
                    alpha = 1.,
                    ec = 'k'))
        nodes[node].draggable()
    for source, target in graph.edges():
        axes.annotate(" ",
                xy=(.5, .5),
                xytext=(.5, .5),
                ha="center",
                va="center",
                xycoords=nodes[target],
                textcoords=nodes[source],
                color="k",
                arrowprops=dict(
                    patchA = nodes[source].get_bbox_patch(),
                    patchB = nodes[target].get_bbox_patch(),
                    arrowstyle = '->',
                    linestyle = graph.edge[source][target]['linestyle'],
                    connectionstyle = 'arc3,rad=0.',
                    lw=2.,
                    fc=graph.edge[source][target]['color'],
                    ec=graph.edge[source][target]['color'],
                    alpha=1.))
    axes.set_xlim(xmin, xmax)
    axes.set_ylim(ymin, ymax)
    return axes
