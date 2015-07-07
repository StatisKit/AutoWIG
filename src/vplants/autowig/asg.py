from clang.cindex import Index, TranslationUnit, CursorKind, Type, TypeKind
import uuid
from mako.template import Template
from path import path
import itertools
import os
from tempfile import NamedTemporaryFile
from abc import ABCMeta
from fnmatch import fnmatch
import re
import warnings
import hashlib
import pdb

from .tools import subclasses, remove_regex, split_scopes, remove_templates
from .custom_warnings import NotWrittenFileWarning, ErrorWarning, NoneTypeWarning,  UndeclaredParentWarning, MultipleDeclaredParentWarning, MultipleDefinitionWarning, NoDefinitionWarning, SideEffectWarning, ProtectedFileWarning, InfoWarning, TemplateParentWarning, TemplateParentWarning, AnonymousWarning, AnonymousFunctionWarning, AnonymousFieldWarning, AnonymousClassWarning, NotImplementedWarning, NotImplementedTypeWarning, NotImplementedDeclWarning, NotImplementedParentWarning, NotImplementedOperatorWarning, NotImplementedTemplateWarning

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
    self._asg._cleaned = False
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

    def glob(self, pattern='*', on_disk=False):
        if on_disk:
            dirname = path(self.globalname)
            for name in dirname.glob(pattern=pattern):
                if name.isdir():
                    self._asg.add_directory(str(name.abspath()))
                if name.isfile():
                    self._asg.add_file(str(name.abspath()))
        nodes = [self._asg[node] for node in self._asg._syntax_edges[self.id]]
        return [node for node in nodes if fnmatch(node.localname, pattern) and node.traverse]

    def walkdirs(self, pattern='*', on_disk=False):
        if on_disk:
            dirname = path(self.globalname)
            for name in dirname.glob(pattern=pattern):
                if name.isdir():
                    self._asg.add_directory(str(name.abspath()))
        nodes = [node for node in self.glob(pattern=pattern) if isinstance(node, DirectoryProxy)]
        return nodes+list(itertools.chain(*[node.walkdirs(pattern, on_disk=on_disk) for node in nodes]))

    def walkfiles(self, pattern='*', on_disk=False):
        nodes = itertools.chain(*[node.glob(on_disk=on_disk) for node in self.walkdirs(on_disk=on_disk)])
        return [node for node in self.glob(pattern=pattern, on_disk=on_disk) if isinstance(node, FileProxy)]+[node for node in nodes if isinstance(node, FileProxy) and fnmatch(node.globalname, pattern)]

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
        self._asg._parse(*includes, flags=flags, **kwargs)
        #if libclang:
        #    index = Index.create()
        #    tempfilehandler = NamedTemporaryFile(delete=False)
        #    for include in includes:
        #        if include.on_disk:
        #            tempfilehandler.write('#include \"' + include.globalname + '\"\n')
        #        else:
        #            tempfilehandler.write('\n' + str(include) + '\n')
        #    tempfilehandler.close()
        #    tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        #    os.unlink(tempfilehandler.name)
        #else:
        #    content = ""
        #    for include in includes:
        #        if include.on_disk:
        #            content += '#include \"' + include.globalname + '\"\n'
        #        else:
        #            content += '\n' + str(include) + '\n'
        #    tu = autowig.clang.tooling.build_ast_from_code_with_args(content, flags)
        #self._asg._read_translation_unit(tu, libclang)
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

    def touch(self):
        if not self.is_protected or force:
            parent = self.parent
            if not parent.on_disk:
                parent.makedirs()
            filehandler = open(self.globalname, 'w')
            filehandler.close()
        else:
            warnings.warn('Cannot create file \'' + self.globalname + '\'', ProtectedFileWarning)

    def write(self, force=False):
        if not self.is_protected or force:
            if self.is_empty:
                warnings.warn()
            else:
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
            warnings.warn('Cannot write file \'' + self.globalname + '\'', ProtectedFileWarning)

    def remove(self, force=False):
        if not self.is_protected or force:
            os.remove(self.globalname)
            self._asg._nodes[self.id]['on_disk'] = False

    @property
    def is_empty(self):
        return str(self) == ""

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.content

    def _repr_html_(self):
        from pygments import highlight
        from pygments.lexers import CLexer, CppLexer, PythonLexer
        from pygments.formatters import HtmlFormatter
        if not self.language is None:
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
            return str(self)

    def md5(self):
        return hashlib.md5(str(self)).hexdigest()

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

def get_language(self):
    if hasattr(self, '_language'):
        return self._language
    else:
        return None

def set_language(self, language):
    self._asg._nodes[self.id]['_language'] = language

def del_language(self):
    self._asg._nodes[self.id].pop('_language', None)

FileProxy.language = property(get_language, set_language, del_language)
del get_language, set_language, del_language

def get_content(self):
    if not hasattr(self, '_content') or self._content == "":
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

    def _headers(self):
        if self.header is None:
            return set()
        else:
            return set([self.header.globalname])

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

    @property
    def nested(self):
        nested = TypeSpecifiersProxy(self._asg, self._source)
        nested.specifiers = str(self.specifiers)
        if self.is_const:
            nested.specifiers = nested.specifiers[:-6]
        if self.is_pointer or self.is_reference:
            nested.specifiers = nested.specifiers[:-2]
        return nested

    def __str__(self):
        return self.globalname


def get_specifiers(self):
    if not hasattr(self, '_specifiers'):
        return self._asg._type_edges[self._source]["specifiers"]
    else:
        return self._specifiers

def set_specifiers(self, specifiers):
    self._specifiers = specifiers

def del_specifiers(self):
    del self._specifiers

TypeSpecifiersProxy.specifiers = property(get_specifiers, set_specifiers, del_specifiers)
del get_specifiers, set_specifiers, del_specifiers

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
        parent = self.id[:self.id.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            return self._asg[parent]

    def __str__(self):
        return self.globalname

class EnumConstantProxy(DeclarationProxy):
    """
    """

    @property
    def parent(self):
        parent = self.globalname
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['enum', 'class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

class EnumProxy(DeclarationProxy):
    """
    """

    @property
    def parent(self):
        parent = self.globalname
        if parent.startswith('enum '):
            parent = parent[5:]
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

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

class ParameterProxy(VariableProxy):
    """
    """

    @property
    def is_anonymous(self):
        return re.match('(.*)parm_[0-9]*$', self.id)

    def rename(self, localname):
        pass

class FieldProxy(VariableProxy):
    """
    """

    @property
    def parent(self):
        parent = self.globalname
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

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
    def overloads(self):
        parent = self.parent
        if isinstance(parent, NamespaceProxy):
            return [overload for overload in self.parent.functions() if overload.localname == self.localname]
        elif isinstance(parent, ClassProxy):
            return [overload for overload in self.parent.methods() if overload.localname == self.localname]
        else:
            raise NotImplementedError('For parent class \'' + parent.__class__.__name__ + '\'')

    @property
    def parent(self):
        parent = remove_templates(self.globalname)
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            return self._asg[parent]

def get_clean(self):
    if not hasattr(self, '_clean'):
        return self._clean_default()
    else:
        return self._clean

def set_clean(self, clean):
    self._asg._cleaned = False
    self._asg._nodes[self._node]['_clean'] = clean
    for parameter in self.parameters:
        parameter.clean = clean

def del_clean(self):
    self._asg._nodes[self._node].pop('_clean', False)
    for parameter in self.parameters:
        del parameter.clean

FunctionProxy.clean = property(get_clean, set_clean, del_clean)

del get_clean, set_clean, del_clean

def get_is_overloaded(self):
    if not hasattr(self, '_is_overloaded'):
        if len(self.overloads) == 1:
            return False
        else:
            return True
    else:
        return self._is_overloaded

def set_is_overloaded(self, is_overloaded):
    self._asg._nodes[self._node]["_is_overloaded"] = is_overloaded

def del_is_overloaded(self):
    self._asg._nodes[self._node].pop("_is_overloaded", False)

FunctionProxy.is_overloaded = property(get_is_overloaded, set_is_overloaded, del_is_overloaded)
del get_is_overloaded, set_is_overloaded

class MethodProxy(FunctionProxy):
    """
    """

    @property
    def parent(self):
        parent = remove_templates(self.globalname)
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

class ConstructorProxy(DeclarationProxy):
    """
    """

    def _headers(self):
        headers = set()
        for prm in self.parameters:
            headers.update(prm._headers())
        if not self.header is None:
            headers.add(self.header.globalname)
        return headers

    @property
    def parent(self):
        parent = remove_templates(self.globalname)
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

    @property
    def nb_parameters(self):
        return len(self._asg._syntax_edges[self._node])

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

def get_clean(self):
    if not hasattr(self, '_clean'):
        return self._clean_default()
    else:
        return self._clean

def set_clean(self, clean):
    self._asg._cleaned = False
    self._asg._nodes[self._node]['_clean'] = clean
    for parameter in self.parameters:
        parameter.clean = clean

def del_clean(self):
    self._asg._nodes[self._node].pop('_clean', False)
    for parameter in self.parameters:
        del parameter.clean

ConstructorProxy.clean = property(get_clean, set_clean, del_clean)

class DestructorProxy(DeclarationProxy):
    """
    """

    @property
    def parent(self):
        parent = remove_templates(self.globalname)
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

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
        parent = remove_templates(self.globalname)
        if parent.startswith('class '):
            parent = parent[6:]
        elif parent.startswith('union '):
            parent = parent[6:]
        elif parent.startswith('struct '):
            parent = parent[7:]
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self._asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self._asg._nodes:
                    parent = self._asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self._asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self._asg[parent]
            return parent

    @property
    def is_derived(self):
        return len(self._asg._base_edges[self._node]) > 0

    def bases(self, inherited=False):
        bases = []
        for base in self._asg._base_edges[self._node]:
            bases.append(self._asg[base['base']])
            bases[-1].access = base['access']
            bases[-1].is_virtual_base = base['is_virtual']
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

    def inheritors(self, recursive=False):
        return [cls for cls in self._asg.classes() if any(base.id == self.id for base in cls.bases(inherited=recursive))]

    @property
    def depth(self):
        if not self.is_derived:
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
        return [enm for enm in self.declarations(inherited) if isinstance(enm, EnumProxy)]

    def fields(self, inherited=False):
        return [field for field in self.declarations(inherited) if isinstance(field, FieldProxy)]

    def methods(self, inherited=False):
        return [method for method in self.declarations(inherited) if isinstance(method, MethodProxy)]

    def classes(self, inherited=False):
        return [cls for cls in self.declarations(inherited) if isinstance(cls, ClassProxy)]

    @property
    def constructors(self):
        return [constructor for constructor in self.declarations(False) if isinstance(constructor, ConstructorProxy)]

    @property
    def destructor(self):
        try:
            return [destructor for destructor in self.declarations(False) if isinstance(destructor, DestructorProxy)].pop()
        except:
            return None

def get_is_copyable(self):
    return self._is_copyable

def set_is_copyable(self, copyable):
    self._asg._nodes[self.id]['_is_copyable'] = copyable

ClassProxy.is_copyable = property(get_is_copyable, set_is_copyable)
del get_is_copyable, set_is_copyable

class TemplateTypeSpecifiersProxy(TypeSpecifiersProxy):

    def __init__(self, asg, source, target):
        super(TemplateTypeSpecifiersProxy, self).__init__(asg, source)
        self._target = target

    @property
    def target(self):
        return self._asg[self._target['target']]

    @property
    def specifiers(self):
        return self._target["specifiers"]


class ClassTemplateSpecializationProxy(ClassProxy):
    """
    """

    def _headers(self):
        headers = super(ClassTemplateSpecializationProxy, self)._headers()
        for template in self.templates:
            headers.update(template.target._headers())
        return headers

    @property
    def templates(self):
        return [TemplateTypeSpecifiersProxy(self._asg, self.id, template) for template in self._asg._template_edges[self.id]] #TODO

def get_as_held_type(self):
    if hasattr(self, '_as_held_type'):
        return self._as_held_type
    else:
        return False

def set_as_held_type(self, as_held_type):
    self._asg._nodes[self.id]['_as_held_type'] = as_held_type

def del_as_held_type(self):
    self._asg._nodes[self.id].pop('_as_held_type', False)

ClassTemplateSpecializationProxy.as_held_type = property(get_as_held_type, set_as_held_type, del_as_held_type)
del get_as_held_type, set_as_held_type, del_as_held_type

class NamespaceProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/namespace>_`
    """

    @property
    def header(self):
        return None

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
        return [enm for enm in self.declarations(nested) if isinstance(enm, EnumProxy)]

    def enum_constants(self, nested=False):
        return [cst for cst in self.declarations(nested) if isinstance(cst, EnumConstantProxy)]

    def variables(self, nested=False):
        return [variable for variable in self.declarations(nested) if isinstance(variable, VariableProxy)]

    def functions(self, nested=False):
        return [fct for fct in self.declarations(nested) if isinstance(fct, FunctionProxy)]

    def classes(self, nested=False):
        return [cls for cls in self.declarations(nested) if isinstance(cls, ClassProxy)]

    def namespaces(self, nested=False):
        if not nested:
            return [namespace for namespace in self.declarations(nested) if isinstance(namespace, NamespaceProxy)]
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
        self._template_edges = dict()
        self._held_types = set()
        self._boost_python_export_edges = dict()
        self._boost_python_module_edges = dict()
        self._cleaned = True

    def __len__(self):
        return len(self._nodes)

    def register_held_type(self, held_type):
        if not isinstance(held_type, basestring):
            raise TypeError('\'held_type\' parameter')
        self._held_types.add(held_type)

    def _compute_held_types(self):
        for cls in self.classes(specialized=True):
            if any(re.match('^(class |struct |union |)' + held_type + '<(.*)>$', cls.globalname) for held_type in self._held_types):
                cls.as_held_type = True

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

    @property
    def directory(self):
        files = self.files()
        directories = set([node.parent.id for node in files])
        while not len(directories) == 1:
            parents = set()
            for directory in directories:
                parent = self[directory].parent.id
                if not parent in directories:
                    if not parent in parents:
                        parents.add(parent)
            directories = parents

    def nodes(self, pattern=None, metaclass=None):
        if metaclass is None:
            if pattern is None:
                return [self[node] for node in self._nodes.keys()]
            else:
                return [self[node] for node in self._nodes.keys() if re.match(pattern, node)]
        else:
            if pattern is None:
                return [node for node in [self[node] for node in self._nodes.keys()] if isinstance(node, metaclass)]
            else:
                return [node for node in [self[node] for node in self._nodes.keys()] if isinstance(node, metaclass) and re.match(pattern, node.id)]

    def directories(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(DirectoryProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def files(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(FileProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def fundamental_types(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(FundamentalTypeProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def typedefs(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(TypedefProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def enums(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(EnumProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def functions(self, pattern=None, free=None):
        if free is None:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(FunctionProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)
        elif free:
            return [node for node in self.functions(free=None) if not isinstance(node, MethodProxy)]
        else:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(MethodProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)

    def classes(self, pattern=None, specialized=None):
        if specialized is None:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(ClassProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)
        elif specialized:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(ClassTemplateSpecializationProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)
        else:
            return [node for node in self.classes(specialized=None) if not isinstance(node, ClassTemplateSpecializationProxy)]

    def namespaces(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(NamespaceProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def headers(self, *nodes):
        white = []
        for node in nodes:
            if isinstance(node, basestring):
                white.extend(self.nodes(node))
            else:
                white.append(node)
        headers = dict()
        black = set()
        while len(white) > 0:
            node = white.pop()
            if not node.id in black:
                black.add(node.id)
                if isinstance(node, FundamentalTypeProxy):
                    continue
                elif isinstance(node, EnumConstantProxy):
                    pass
                elif isinstance(node, EnumProxy):
                    pass
                elif isinstance(node, VariableProxy):
                    white.append(node.type.target)
                elif isinstance(node, FunctionProxy):
                    white.append(node.result_type.target)
                    white.extend([prm.type.target for prm in node.parameters])
                elif isinstance(node, ConstructorProxy):
                    white.extend([prm.type.target for prm in node.parameters])
                elif isinstance(node, DestructorProxy):
                    pass
                elif isinstance(node, ClassProxy):
                    white.extend(node.bases())
                    white.extend(node.declarations())
                    if isinstance(node, ClassTemplateSpecializationProxy):
                        white.extend([tpl.target for tpl in node.templates])
                elif isinstance(node, NamespaceProxy):
                    white.extend(node.declarations())
                elif isinstance(node, TypedefProxy):
                    white.append(node.type.target)
                else:
                    raise NotImplementedError(node.__class__.__name__)
                header = node.header
                if not header is None:
                    headers[header.globalname] = header
        return headers.values()

    def check_syntax(self):
        for node in self.nodes():
            if not node.id in ['/', '::'] and not node.id in self._syntax_edges[node.parent.id]:
                yield node

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if not node in self._nodes:
            raise KeyError('\'' + node + '\' parameter')
        else:
            return self._nodes[node]["proxy"](self, node)

    #def _ipython_display_(self):
    #    global __asg__
    #    __asg__ = self
    #    interact(plot,
    #            layout=('graphviz', 'circular', 'random', 'spring', 'spectral'),
    #            size=(0., 60., .5),
    #            aspect=(0., 1., .01),
    #            specialization=False,
    #            type=False,
    #            base=False,
    #            fundamentals=False,
    #            variables=False,
    #            directories=True,
    #            files=True,
    #            pattern='/(.*)')

__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(NodeProxy)]
__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(EdgeProxy)]
