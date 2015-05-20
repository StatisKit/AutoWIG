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

from .scope import Scope
from .config import Cursor

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

    def parse(self,  pattern='*.h', side_effect=True, **kwargs):
        includes = self.walkfiles(pattern=pattern)
        for include in includes:
            include.clean = False
        if not side_effect:
            if kwargs.pop('libclang', True):
                index = Index.create()
                tempfilehandler = NamedTemporaryFile(delete=False)
                for include in includes:
                    if include.on_disk:
                        tempfilehandler.write('#include \"' + include.globalname + '\"\n')
                    else:
                        tempfilehandler.write('\n' + str(include) + '\n')
                tempfilehandler.close()
                flags = kwargs.pop('flags', None)
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
                tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
                os.unlink(tempfilehandler.name)
                self._asg._read_translation_unit(tu)
                del self._asg._language
            else:
                raise NotImplementedError('')
        else:
            for include in includes:
                include.parse(**kwargs)

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
        if not self.on_disk or not self.is_protected or force:
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
        parent = os.sep.join(self.globalname.split(os.sep)[:-1]) + os.sep
        return self._asg[parent]

    def parse(self, **kwargs):
        self.clean = False
        if kwargs.pop('libclang', True):
            index = Index.create()
            flags = kwargs.pop('flags', None)
            if flags is None:
                language = kwargs.pop('language', self.language)
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
            if self.on_disk:
                tu = index.parse(self.globalname, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
            else:
                tempfilehandler = NamedTemporaryFile(delete=False)
                tempfilehandler.write(str(self))
                tempfilehandler.close()
                tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
                os.unlink(tempfilehandler.name)
            self._asg._read_translation_unit(tu)
            del self._asg._language
        else:
            raise NotImplementedError('')

def get_is_protected(self):
    if hasattr(self, '_is_protected'):
        return self._is_protected
    else:
        return True

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
                return self.scope.header
            except:
                return None

    def _clean_default(self):
        header = self.header
        return header is None or header.clean

    def __contains__(self, scope):
        if scope.has_scopes:
            raise ValueError('\'scope\' parameter')
        node = self.id
        if not node.endswith('::'):
            node += '::'
        #if scope.has_templates:
        #    #if not node + scope.name in self._asg._syntax_edges[self._node]:
        #    #    #templates = scope.templates
        #    #    #nb_templates = len(templates)
        #    #    #candidate = [candidate for candidate in self.classes() if isinstance(candidate, (ClassTemplateProxy, ClassDefaultTemplateProxy)) and candidate.nb_templates == nb_templates]
        #    #    #if len(candidate) == 0:
        #    #    #    return False
        #    #    #elif len(candidate) == 1:
        #    #    #    candidate = candidate.pop()
        #    #    #    #if candidate.is_specialized:
        #    #    #    #    maxmatch = 0
        #    #    #    #    candidates = []
        #    #    #    #    for specialization in candidate.specializations:
        #    #    #    #        match = specialization.match(scope)
        #    #    #    #        if match >= maxmatch:
        #    #    #    #            maxmatch = match
        #    #    #    #            candidates.append(specialization)
        #    #    #    #    if len(candidates) > 1:
        #    #    #    #        raise ValueError()
        #    #    #    #    elif len(candidates) == 1:
        #    #    #    #        candidate = candidates.pop()
        #    #    #    candidate.instantiate(*templates)
        #    #    #    return True
        #    #    #else:
        #    #    #    raise ValueError()
        #    #raise NotImplementedError()
        #    #else:
        #    #    return True
        #    node = node + scope.remove_templates().name
        #else:
        node = node + scope.name
        return node in self._asg._syntax_edges[self._node]
        #if not contains and hasattr(self, 'usings'):
        #    for using in self.usings:
        #        if scope in self._asg[using]:
        #            contains = True
        #            break
        #return contains

    def __getitem__(self, scope):
        if isinstance(scope, basestring):
            scope = Scope(scope)
        if scope.is_global:
            item = self._asg._nodes['::']['proxy'](self._asg, '::')
            for scope in scope.split():
                item = item[scope]
            return item
        elif scope.has_scopes:
            item = self
            scopes = list(scope.split())
            while not scopes[0] in item and not item.globalname == '::':
                item = item.scope
            item = self.__getproxy__(item, scopes[0])
            for scope in scopes[1:]:
                item = item[scope]
            return item
        else:
            item = self
            while not scope in item and not item.globalname == '::':
                item = item.scope
            return self.__getproxy__(item, scope)

    def __getproxy__(self, item, scope):
        if isinstance(item, AliasProxy):
            item = item.alias
        node = item._node
        if not node.endswith('::'):
            node += '::'
        if scope.has_templates:
            node += scope.remove_templates().name
        else:
            node += scope.name
        #if node in self._asg._syntax_edges[item.id]:
        return self._asg._nodes[node]['proxy'](self._asg, node)
        #elif hasattr(item, 'usings'):
        #     for using in item.usings:
        #         self._asg._syntax_edges[self._node]
        #         if scope in self._asg[using]:
        #            contains = True
        #            break

    @property
    def scopes(self):
        scopes = []
        scope = self.parent
        while not scope.globalname == '::':
            scopes.append(scope)
            scope = scope.parent
        return reversed(scopes)

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
    def scope(self):
        return self.parent

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

    def __call__(self, localname):
        return str(localname)

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

    def __call__(self, localname):
        return str(int(localname))

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

    def __call__(self, localname):
        return str(int(localname))

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

    def __call__(self, localname):
        return str(float(localname))

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

    def __call__(self, localname):
        return str(bool(localname))

class ComplexTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = "::_Complex float"

    def __call__(self, localname):
        return str(bool(localname))

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
        if self.is_reference:
            return self.specifiers.endswith('const &')
        else:
            return self.specifiers.endswith('const')

    @property
    def is_reference(self):
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
        return re.sub('(.*)::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}(.*)', r'\1\2', self.id)

    @property
    def localname(self):
        return Scope(self.globalname, False).split()[-1].name

    @property
    def scope(self):
        return self.parent

    @property
    def parent(self):
        parent = self.globalname
        parent = parent[:parent.rfind(':')-1]
        if parent == '':
            parent = '::'
        return self._asg[parent]

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

    def __str__(self):
        if hasattr(self, '_template'):
            return self._template.render(obj=self)
        else:
            return self.globalname

class AliasProxy(DeclarationProxy):

    def __dir__(self):
        return sorted(['alias'] + self.alias.__dir__())

    def __getattr__(self, attr):
        if attr == 'alias':
            return self._asg[self._asg._nodes[self.id]['alias']]
        else:
            return getattr(self.alias, attr)

    def __contains__(self, scope):
        if scope.has_scopes:
            raise ValueError('\'scope\' parameter')
        node = self.alias.id
        if not node.endswith('::'):
            node += '::'
        if scope.has_templates:
            #if not node + scope.name in self._asg._syntax_edges[self._node]:
            #    #templates = scope.templates
            #    #nb_templates = len(templates)
            #    #candidate = [candidate for candidate in self.classes() if isinstance(candidate, (ClassTemplateProxy, ClassDefaultTemplateProxy)) and candidate.nb_templates == nb_templates]
            #    #if len(candidate) == 0:
            #    #    return False
            #    #elif len(candidate) == 1:
            #    #    candidate = candidate.pop()
            #    #    #if candidate.is_specialized:
            #    #    #    maxmatch = 0
            #    #    #    candidates = []
            #    #    #    for specialization in candidate.specializations:
            #    #    #        match = specialization.match(scope)
            #    #    #        if match >= maxmatch:
            #    #    #            maxmatch = match
            #    #    #            candidates.append(specialization)
            #    #    #    if len(candidates) > 1:
            #    #    #        raise ValueError()
            #    #    #    elif len(candidates) == 1:
            #    #    #        candidate = candidates.pop()
            #    #    candidate.instantiate(*templates)
            #    #    return True
            #    #else:
            #    #    raise ValueError()
            #raise NotImplementedError()
            #else:
            #    return True
            node = node + scope.remove_templates().name
        else:
            node = node + scope.name
        return node in self._asg._syntax_edges[self.alias.id]

class EnumConstantProxy(DeclarationProxy):
    """
    """

class ParameterProxy(DeclarationProxy):
    """
    """

    @property
    def parent(self):
        parent = self.id
        parent = parent[:parent.rfind(':')-1]
        if parent == '':
            parent = '::'
        return self._asg[parent]

    @property
    def type(self):
        return TypeSpecifiersProxy(self._asg, self._node)

    def __str__(self):
        return self.type.globalname + " " + self.localname

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
    def scope(self):
        return self.parent

    @property
    def is_overloaded(self):
        if not hasattr(self, '_is_overloaded'):
            overloads = self._asg["^" + self.globalname + "::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"]
            if len(overloads) == 1:
                self._asg._nodes[self._node]["_is_overloaded"] = False
            else:
                for overload in overloads:
                    self._asg._nodes[overload._node]["_is_overloaded"] = True
        overloaded = self._is_overloaded
        if not overloaded:
            self._asg._nodes[self._node].pop("_is_overloaded")
        return overloaded

    @property
    def signature(self):
        return str(self.result_type) + " " + self.localname + "(" + ", ".join(str(parameter.type) for parameter in self.parameters)+ ")"

class MethodProxy(FunctionProxy):
    """
    """

class ConstructorProxy(DeclarationProxy):
    """
    """

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

    @property
    def scope(self):
        return self.parent

    #@property
    #def overloaded(self):
    #    if not self._asg._frozen:
    #        raise ValueError('')
    #    if not overloaded in self._asg[node]:
    #        overloads = self._asg[self.scope._node + "(.*)-(.*)-(.*)-(.*)-(.*)" + self.localname + "$"]
    #        if len(overloads) == 1:
    #            self._asg[node]["overloaded"] = False
    #        else:
    #            for overload in overloads:
    #                self._nodes[overload._node]["overloaded"] = True
    #    return self._asg[self._node]["overloaded"]

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
    def parent(self):
        parent = self.globalname
        if parent[-1] == '>':
            index = -2
            delimiter = 1
            while not delimiter == 0:
                if parent[index] == '<':
                    delimiter -= 1
                elif parent[index] == '>':
                    delimiter += 1
                index -= 1
            parent = parent[:index+1]
        parent = parent[:parent.rfind(':')-1]
        if parent == '':
            parent = '::'
        return self._asg[parent]

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
            #if isinstance(bases[-1], TypedefProxy):
            #    bases[-1] = bases[-1].type.target
            bases[-1].access = base['access']
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
                        self._syntax_edges[function.scope.id].remove(function.id)
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
            if isinstance(node, (TypedefProxy, VariableProxy, ParameterProxy)):
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

    def to_networkx(self, pattern='(.*)', specialization=True, type=True, base=True, directories=True, files=True, fundamentals=True, parameters=True):
        graph = networkx.DiGraph()

        class Filter(object):

            __metaclass__ = ABCMeta

        if not directories:
            Filter.register(DirectoryProxy)
        if not files:
            Filter.register(FileProxy)
        if not fundamentals:
            Filter.register(FundamentalTypeProxy)
        if not parameters:
            Filter.register(ParameterProxy)
        for node in self.nodes():
            if not isinstance(node, Filter):
                graph.add_node(node.id)
        for source, targets in self._syntax_edges.iteritems():
            if not isinstance(self[source], Filter):
                for target in targets:
                    if not isinstance(self[target], Filter):
                        graph.add_edge(source, target, color='k', linestyle='solid')
        #if specialization:
        #    for target, sources in self._specializationedges.iteritems():
        #        if not isinstance(self[target], Filter):
        #            for source in sources:
        #                if not isinstance(self[source], Filter):
        #                    graph.add_edge(source, target, color='y', linestyle='dashed')
        if type:
            for source, target in self._type_edges.iteritems():
                if not isinstance(self[source], Filter) and not isinstance(self[target['target']], Filter):
                    graph.add_edge(source, target['target'], color='r', linestyle='solid')
        #for source, properties in self._nodes.iteritems():
        #    if 'instantiation' in properties:
        #        graph.add_edge(source, properties['instantiation'], color='y', linestyle='solid')
        #for source, targets in self._syntax_edges.iteritems():
        #    for target in targets: graph.add_edge(source, target, color='k', linestyle='solid')
        if base:
            for source, targets in self._base_edges.iteritems():
                if not isinstance(self[source], Filter):
                    for target in targets:
                        if not isinstance(self[target], Filter):
                            graph.add_edge(source, target['base'], color='m', linestyle='solid')

        return graph.subgraph([node for node in graph.nodes() if re.match(pattern, node)])

    def _read_type(self, cursortype, scope, **kwargs):
        specifiers = ''
        while True:
            if cursortype.kind is TypeKind.LVALUEREFERENCE:
                specifiers = ' &' + specifiers
                cursortype = cursortype.get_pointee()
            if cursortype.kind is TypeKind.RVALUEREFERENCE:
                specifiers = ' &&' + specifiers
                cursortype = cursortype.get_pointee()
            elif cursortype.kind is TypeKind.POINTER:
                specifiers = ' *' + ' const'*cursortype.is_const_qualified() + specifiers
                cursortype = cursortype.get_pointee()
            elif cursortype.kind is TypeKind.INCOMPLETEARRAY:
                specifiers = ' []' + ' const'*cursortype.is_const_qualified() + specifiers
                cursortype = cursortype.get_array_element_type()
            elif cursortype.kind is TypeKind.CONSTANTARRAY:
                specifiers = ' [' + str(cursortype.get_array_size()) +']' + ' const'*cursortype.is_const_qualified() + specifiers
                cursortype = cursortype.get_array_element_type()
            elif cursortype.kind in [TypeKind.RECORD, TypeKind.TYPEDEF, TypeKind.ENUM, TypeKind.UNEXPOSED]:
                spelling = cursortype.get_declaration().type.spelling
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                if cursortype.is_volatile_qualified():
                    specifiers = ' volatile' + specifiers
                return self[scope][Scope(spelling)].id, specifiers
            elif cursortype.kind is TypeKind.MEMBERPOINTER:
                    return UnexposedTypeProxy._node, specifiers
            elif cursortype.kind in [TypeKind.CHAR_U, TypeKind.CHAR_S]:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return CharTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.UCHAR:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return UnsignedCharTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.SCHAR:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedCharTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.CHAR16:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return Char16TypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.CHAR32:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return Char32TypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.WCHAR:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return WCharTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.SHORT:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedShortIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.INT:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.LONG:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedLongIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.LONGLONG:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedLongLongIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.USHORT:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return UnsignedShortIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.UINT:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return UnsignedIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.ULONG:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return UnsignedLongIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.ULONGLONG:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return UnsignedLongLongIntegerTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.FLOAT:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedFloatTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.DOUBLE:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedDoubleTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.LONGDOUBLE:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return SignedLongDoubleTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.BOOL:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return BoolTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.COMPLEX:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return ComplexTypeProxy._node, specifiers
            elif cursortype.kind is TypeKind.VOID:
                if cursortype.is_const_qualified():
                    specifiers = ' const' + specifiers
                return VoidTypeProxy._node, specifiers
            else:
                raise NotImplementedError(str(cursortype.kind) + ': ' + cursortype.spelling)

    def _read_translation_unit(self, tu):
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

        for child in tu.cursor.get_children():
            self._read_cursor(child, scope='::')

    def _read_decl(self, decl, scope='::', **kwargs):
        """
        """
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        if isinstance(decl, _autowig.clang.EnumDecl):
            if spelling.endswith('::'):
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in decl.get_children():
                    children.extend(self._read_decl(child, spelling))
                #filename = str(path(str(cursor.location.file)).abspath()) TODO
                #self.add_file(filename, language=self._language)
                #for childspelling in children:
                #    self._nodes[childspelling]['_header'] = filename
                return children
            else:
                if not spelling in self._nodes:
                    self._syntax_edges[spelling] = []
                    self._nodes[spelling] = dict(proxy=EnumProxy)
                    self._syntax_edges[scope].append(spelling)
                elif not self[spelling].is_complete:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges[scope].append(spelling)
                if not self[spelling].is_complete:
                    for child in decl.get_children():
                        self._read_decl(child, spelling)
                    #filename = str(path(str(cursor.location.file)).abspath()) TODO
                    #self.add_file(filename, language=self._language)
                    #self._nodes[spelling]['_header'] = filename
                    return [spelling]
                else:
                    return []
        elif isinstance(decl, _autowig.clang.EnumConstantDecl):
            self._nodes[spelling] = dict(proxy=EnumConstantProxy)
            self._syntax_edges[scope].append(spelling)
            return [spelling]
        elif isinstance(decl, _autowig.clang.TypedefDecl):
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=TypedefProxy)
                self._syntax_edges[scope].append(spelling)
                pass # TODO type
            else:
                return []
        elif isinstance(decl, _autowig.clang.VarDecl) and not isinstance(decl, _autowig.clang.VarTemplateSpecializationDecl):
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=VariableProxy)
                self._syntax_edges[scope].append(spelling)
                if not isinstance(decl, _autowig.clang.ParmDecl):
                    #filename = str(path(str(cursor.location.file)).abspath()) TODO
                    #self.add_file(filename, language=self._language)
                    #self._nodes[spelling]['_header'] = filename
                    pass
                pass # TODO tyoe
            else:
                return []
        elif isinstance(decl, _autowig.clang.FieldDecl):
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=FieldProxy,
                        is_mutable=decl.is_mutable())
                self._syntax_edges[scope].append(spelling)
                pass # TODO type + anonymous
            else:
                return []
        elif isinstance(decl, _autowig.clang.FunctionDecl):
            if not isinstance(decl, _autowig.clang.CXXMethodDecl):
                if not self.language == 'c' and not decl.is_extern_c_context():
                    spelling += '::' + str(uuid.uuid4())
                self._nodes[spelling] = dict(proxy=FunctionProxy)
                self._syntax_edges[scope].append(spelling)
                for child in decl.get_children():
                    self._read_decl(child, spelling)
                #filename = str(path(str(cursor.location.file)).abspath()) TODO
                #self.add_file(filename, language=self._language)
                #self._nodes[spelling]['_header'] = filename
                # TODO type
                # TODO Problem when parsing 2 or more times the same file
                return [spelling]
            else:
                if not isinstance(decl.get_lexical_parent(), _autowig.NamespaceDecl):
                    if isinstance(decl, _autowig.clang.CXXDestructorDecl):
                        self._nodes[spelling] = dict(proxy=DestructorProxy,
                                is_static=decl.is_static(),
                                is_const=decl.is_const(),
                                is_volatile=decl.is_volatile(),
                                is_virtual=decl.is_virtual())
                        return [spelling]
                    else:
                        spelling += '::' + str(uuid.uuid4())
                        if isinstance(decl, _autowig.clang.CXXConstructorDecl):
                            self._nodes[spelling] = dict(proxy=ConstructorProxy,
                                    is_static=decl.is_static(),
                                    is_const=decl.is_const(),
                                    is_volatile=decl.is_volatile(),
                                    is_virtual=decl.is_virtual())
                            for child in decl.get_children():
                                self._read_decl(child, spelling)
                            return [spelling]
                        elif isinstance(decl, _autowig.clang.CXXConversionDecl):
                            # TODO
                            pass
                        else:
                            self._nodes[spelling] = dict(proxy=MethodProxy,
                                is_static=decl.is_static(),
                                is_const=decl.is_const(),
                                is_volatile=decl.is_volatile(),
                                is_virtual=decl.is_virtual())
                            for child in decl.get_children():
                                self._read_decl(child, spelling)
                                # TODO type
                            return [spelling]
                else:
                    return []
        elif isinstance(decl, _autowig.RecordDecl):
            if not isinstance(decl, _autowig.CXXRecordDecl): # C STRUCT UNION
                pass
            elif not isinstance(decl, _autowig.ClassTemplateSpecializationDecl): # C++ CLASS
                pass
            elif not isinstance(decl, _autowig.ClassTemplatePartialSpecializationDecl): # C++ SPECIALIZED CLASS
                pass
            else:
                return []
        elif isinstance(decl, _autowig.NamespaceDecl):
            pass

    def _read_cursor(self, cursor, scope='::', **kwargs):
        """
        """
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        #spelling = Scope(spelling).name
        if cursor.kind is CursorKind.UNEXPOSED_DECL:
            if cursor.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in cursor.get_children():
                    children.extend(self._read_cursor(child, spelling))
                return children
            else:
                warnings.warn(str(cursor.kind) + ': ' + cursor.spelling, SyntaxWarning)
                return []
        elif cursor.kind is CursorKind.ENUM_DECL:
            if cursor.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in cursor.get_children():
                    children.extend(self._read_cursor(child, spelling))
                filename = str(path(str(cursor.location.file)).abspath())
                self.add_file(filename, language=self._language)
                for childspelling in children:
                    self._nodes[childspelling]['_header'] = filename
                return children
            else:
                if not spelling in self._nodes :
                    self._syntax_edges[spelling] = []
                    self._nodes[spelling] = dict(cursor=cursor,proxy=EnumProxy)
                    self._syntax_edges[scope].append(spelling)
                elif not self[spelling].is_complete:
                    self._syntax_edges[scope].remove(spelling)
                    self._syntax_edges[scope].append(spelling)
                if not self[spelling].is_complete:
                    for child in cursor.get_children():
                        self._read_cursor(child, spelling)
                    filename = str(path(str(cursor.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    return [spelling]
                else:
                    return []
        elif cursor.kind is CursorKind.ENUM_CONSTANT_DECL:
            self._nodes[spelling] = dict(cursor=cursor,proxy=EnumConstantProxy)
            self._syntax_edges[scope].append(spelling)
            return [spelling]
        elif cursor.kind is CursorKind.TYPEDEF_DECL:
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(cursor=cursor,
                        proxy=TypedefProxy)
                try:
                    target, specifiers = self._read_type(cursor.underlying_typedef_type, scope)
                    self._type_edges[spelling] = dict(target=target, specifiers='')
                except:
                    children = [child for child in cursor.get_children()]
                    if not len(children) == 1:
                        self._nodes.pop(spelling)
                        warnings.warn(str(cursor.kind) + ': ' + cursor.spelling, SyntaxWarning)
                        return []
                    else:
                        try:
                            self._syntax_edges[scope].append(spelling)
                            child = children.pop()
                            if child.kind is CursorKind.TYPE_REF:
                                self._type_edges[spelling]['target'] = self[scope][child.type.spelling].id
                                filename = str(path(str(cursor.location.file)).abspath())
                                self.add_file(filename, language=self._language)
                                self._nodes[spelling]['_header'] = filename
                            elif child.kind in [CursorKind.UNION_DECL, CursorKind.STRUCT_DECL]:
                                if child.spelling == '':
                                    self._nodes[spelling] = dict(cursor=cursor,
                                            proxy=ClassProxy,
                                            default_access='public')
                                    self._syntax_edges[spelling] = []
                                    self._base_edges[spelling] = []
                                    for child in child.get_children():
                                        for childspelling in self._read_cursor(child, spelling):
                                            self._nodes[childspelling]["access"] = 'public'
                                            dict.pop(self._nodes[childspelling], "header", None)
                                else:
                                    self._type_edges[spelling]['target'] = self[scope][child.type.spelling].id
                                filename = str(path(str(cursor.location.file)).abspath())
                                self.add_file(filename, language=self._language)
                                self._nodes[spelling]['_header'] = filename
                            elif child.kind is CursorKind.ENUM_DECL:
                                if child.spelling == '':
                                    filename = str(path(str(cursor.location.file)).abspath())
                                    self.add_file(filename, language=self._language)
                                    self._nodes[spelling] = dict(cursor=cursor,
                                            proxy=EnumProxy)
                                    self._syntax_edges[spelling] = []
                                    for child in child.get_children():
                                        self._read_cursor(child, spelling)
                                else:
                                    self._type_edges[spelling]['target'] = self[scope][child.type.spelling].id
                                filename = str(path(str(cursor.location.file)).abspath())
                                self.add_file(filename, language=self._language)
                                self._nodes[spelling]['_header'] = filename
                            else:
                                raise NotImplementedError(str(cursor.kind) + ': ' + cursor.spelling)
                            return [spelling]
                        except:
                            self._nodes.pop(spelling)
                            self._syntax_edges[scope].remove(spelling)
                            warnings.warn(str(cursor.kind) + ': ' + cursor.spelling, SyntaxWarning)
                            return []
                        else:
                            filename = str(path(str(cursor.location.file)).abspath())
                            self.add_file(filename, language=self._language)
                            self._nodes[spelling]['_header'] = filename
                            return [spelling]
                else:
                    self._syntax_edges[scope].append(spelling)
                    filename = str(path(str(cursor.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    return [spelling]
                # TODO
            else:
                return []
        elif cursor.kind in [CursorKind.VAR_DECL, CursorKind.FIELD_DECL]:
            if any(child.kind in [CursorKind.TEMPLATE_NON_TYPE_PARAMETER, CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_TEMPLATE_PARAMETER] for child in cursor.get_children()):
                return []
            if cursor.kind is CursorKind.VAR_DECL:
                self._nodes[spelling] = dict(cursor=cursor,
                        proxy=VariableProxy,
                        is_static=False) # TODO
                filename = str(path(str(cursor.location.file)).abspath())
                self.add_file(filename, language=self._language)
                self._nodes[spelling]['_header'] = filename
            else:
                self._nodes[spelling] = dict(cursor=cursor,
                        proxy=FieldProxy,
                        is_mutable=False, # TODO
                        is_static=False) # TODO
            self._syntax_edges[scope].append(spelling)
            try:
                target, specifiers = self._read_type(cursor.type, scope)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Exception as error:
                self._syntax_edges[scope].remove(spelling)
                self._nodes.pop(spelling)
                warnings.warn(str(error), SyntaxWarning)
                return []
            else:
                return [spelling]
        elif cursor.kind is CursorKind.PARM_DECL:
            self._nodes[spelling] = dict(proxy = ParameterProxy)
            self._syntax_edges[scope].append(spelling)
            try:
                target, specifiers = self._read_type(cursor.type, scope)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Exception as error:
                self._syntax_edges[scope].remove(spelling)
                self._nodes.pop(spelling)
                warnings.warn(str(error), SyntaxWarning)
                return []
            else:
                return [spelling]
        elif cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD, CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
            if cursor.kind in [CursorKind.DESTRUCTOR, CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR] and cursor.lexical_parent.kind is CursorKind.NAMESPACE:
                return []
            if not cursor.kind is CursorKind.DESTRUCTOR:
                spelling = spelling + '::' + str(uuid.uuid4())
            if cursor.kind is CursorKind.FUNCTION_DECL:
                self._nodes[spelling] = dict(cursor=cursor,proxy=FunctionProxy)
                if not cursor.location is None:
                    filename = str(path(str(cursor.location.file)).abspath())
                self.add_file(filename, language=self._language)
                self._nodes[spelling]['_header'] = filename
            elif cursor.kind is CursorKind.CXX_METHOD:
                self._nodes[spelling] = dict(cursor=cursor,proxy=MethodProxy,
                        is_static=cursor.is_static_method(),
                        is_virtual=cursor.is_virtual_method(),
                        is_const=cursor.type.is_const_qualified(),
                        is_pure_virtual=cursor.is_pure_virtual_method())
            elif cursor.kind is CursorKind.CONSTRUCTOR:
                self._nodes[spelling] = dict(cursor=cursor,proxy=ConstructorProxy)
            else:
                self._nodes[spelling] = dict(cursor=cursor,proxy=DestructorProxy,
                        virtual=cursor.is_virtual_method())
            self._syntax_edges[spelling] = []
            self._syntax_edges[scope].append(spelling)
            try:
                with warnings.catch_warnings() as w:
                    warnings.simplefilter("error")
                    for child in cursor.get_children():
                        if child.kind is CursorKind.PARM_DECL:
                            self._read_cursor(child, spelling)
                    if not cursor.kind in [CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:
                        target, specifiers = self._read_type(cursor.result_type, spelling)
                        self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Exception as error:
                self._syntax_edges[scope].remove(spelling)
                self._syntax_edges.pop(spelling)
                self._nodes.pop(spelling)
                if not spelling.endswith('::'):
                    spelling += '::'
                for child in cursor.get_children():
                    if child.kind is CursorKind.PARM_DECL:
                        self._nodes.pop(spelling + child.spelling, None)
                        self._syntax_edges.pop(spelling + child.spelling, None)
                warnings.warn(str(error), SyntaxWarning)
                return []
            else:
                return [spelling]
        elif cursor.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL, CursorKind.CLASS_DECL]:
            if cursor.spelling == '':
                return []
            else:
                spelling = Scope(cursor.type.spelling)
                scope = '::' + '::'.join(scope.name for scope in spelling.split()[:-1])
                if not scope in self:
                    return []
                spelling = spelling.name
                if not spelling.startswith('::'):
                    spelling = '::' + spelling
                if not spelling in self._nodes:
                    if cursor.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
                        self._nodes[spelling] = dict(cursor=cursor,proxy=ClassProxy,
                                default_access='public',
                                is_abstract=True,
                                is_copyable=False)
                    elif cursor.kind is CursorKind.CLASS_DECL:
                        self._nodes[spelling] = dict(cursor=cursor,proxy=ClassProxy,
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
                    forward_declaration = True
                    for child in cursor.get_children():
                        if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                            try:
                                childspelling = Scope(child.type.spelling)
                                base = self[scope][childspelling]
                            except:
                                warnings.warn(str(child.kind) + ": " + childspelling.name, SyntaxWarning)
                            else:
                                access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                                self._base_edges[spelling].append(dict(base=base.id,
                                    access=access))
                            finally:
                              forward_declaration = False
                        elif child.kind in [CursorKind.ENUM_DECL, CursorKind.TYPEDEF_DECL, CursorKind.CXX_METHOD, CursorKind.FIELD_DECL, CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR, CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL]:
                                forward_declaration = False
                                for childspelling in self._read_cursor(child, spelling):
                                    self._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                                    dict.pop(self._nodes[childspelling], "_header", None)
                        elif child.kind in [CursorKind.FUNCTION_TEMPLATE, CursorKind.CLASS_TEMPLATE, CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION]:
                            forward_declaration = False
                    if not forward_declaration and not '_header' in self._nodes[spelling]:
                        self._nodes[spelling]['is_abstract'] = cursor.is_abstract_record()
                        self._nodes[spelling]['is_copyable'] = cursor.is_copyable_record()
                        filename = str(path(str(cursor.location.file)).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                return [spelling]
        elif cursor.kind is CursorKind.NAMESPACE:
            if cursor.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in cursor.get_children():
                    children.extend(self._read_cursor(child, spelling))
                return children
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(cursor=cursor,proxy=NamespaceProxy)
                    self._syntax_edges[spelling] = []
                if not spelling in self._syntax_edges[scope]:
                    self._syntax_edges[scope].append(spelling)
                for child in cursor.get_children():
                    self._read_cursor(child, spelling)
                return [spelling]
        elif cursor.kind is CursorKind.NAMESPACE_ALIAS:
            try:
                newscope = ""
                for child in cursor.get_children():
                    if child.kind is CursorKind.NAMESPACE_REF:
                        newscope += child.spelling + '::'
                    else:
                        raise NotImplementedError(str(cursor.kind) + ': '+ cursor.spelling)
                newscope = newscope[:-2]
            except NotImplementedError as error:
                warnings.warn(str(error), SyntaxWarning)
                return []
            except:
                raise
            else:
                self._nodes[spelling] = dict(cursor=cursor,proxy=AliasProxy,alias=newscope)
                return [spelling]
        elif cursor.kind in [CursorKind.FUNCTION_TEMPLATE, CursorKind.USING_DECLARATION, CursorKind.USING_DIRECTIVE, CursorKind.UNEXPOSED_ATTR]:
            return []
        else:
            warnings.warn(str(cursor.kind) + ': ' + cursor.spelling, SyntaxWarning)
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
                parameters=False,
                directories=True,
                files=True,
                pattern='(.*)')

def plot(layout='graphviz', size=16, aspect=.5, invert=False, pattern='(.*)', specialization=True, type=False, base=True, directories=True, files=True, fundamentals=False, parameters=False, **kwargs):
    global __asg__
    graph = __asg__.to_networkx(pattern,
            specialization=specialization,
            type=type,
            base=base,
            directories=directories,
            files=files,
            fundamentals=fundamentals,
            parameters=parameters)
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
