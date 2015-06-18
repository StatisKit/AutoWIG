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

from vplants.autowig import autowig

from .config import Cursor
from .tools import remove_regex, split_scopes, remove_templates
from .custom_warnings import NotWrittenFileWarning, NoneTypeWarning, NotImplementedTypeWarning, UndeclaredParentWarning, NotImplementedDeclWarning, TemplateParentWarning, NotImplementedDeclWarning, NotImplementedParentWarning, AnonymousFunctionWarning, AnonymousFieldWarning, AnonymousClassWarning, NoDefinitionWarning, MultipleDefinitionWarning, SideEffectWarning

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
            raise AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')

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
            raise IOError('Cannot write file \'' + self.globalname + '\' since it is a protected file')

    def remove(self, force=False):
        if not self.is_protected or force:
            os.remove(self.globalname)
            self._asg._nodes[self.id]['on_disk'] = False

    def __str__(self):
        return self.content

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
        return re.match('(.*)_parm_[0-9]*$', self.id)

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

    @property
    def headers(self):
        return [self.header] + [template.header for template in self.templates]

    @property
    def templates(self):
        return [TemplateTypeSpecifiersProxy(self._asg, self.id, template) for template in self._asg._template_edges[self.id]] #TODO

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
        self._cleaned = True

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
                warnings.warn(error.message, NotWrittenFileWarning)

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

    def to_object(self, func2method=True):
        """
        """

        if func2method:
            for cls in [cls for cls in self['::'].classes() if hasattr(cls, '_header') and cls.header.language == 'c' and cls.traverse]:
                for fct in [fct for fct in self['::'].functions() if fct.traverse]:
                    mv = False
                    rtype = fct.result_type
                    if rtype.target.id == cls.id:
                        self._nodes[fct.id].update(proxy=MethodProxy,
                                is_static=True,
                                is_virtual=False,
                                is_pure_virtual=False,
                                is_const=ptype.is_const,
                                as_constructor=True,
                                access='public')
                        mv = True
                    elif fct.nb_parameters > 0:
                        ptype = fct.parameters[0].type
                        if ptype.target.id == cls.id and (ptype.is_reference or ptype.is_pointer):
                            self._nodes[fct.id].update(proxy=MethodProxy,
                                    is_static=False,
                                    is_virtual=False,
                                    is_pure_virtual=False,
                                    is_const=ptype.is_const,
                                    access='public')
                            mv = True
                    if mv:
                        self._syntax_edges[fct.parent.id].remove(fct.id)
                        self._syntax_edges[cls.id].append(fct.id)

    def resolve_overloads(self):
        if not self._cleaned:
            for fct in self.functions(free=None):
                if hasattr(fct, '_is_overloaded') and not fct._is_overloaded:
                    del fct.is_overloaded
            for fct in self.functions(free=None):
                overloads = fct.overloads
                if len(overloads) == 1:
                    fct.is_overloaded = False
                else:
                    for overload in overloads:
                        overload.is_overloaded = True

    def remove_invalid_pointers(self):
        cleanbuffer =  []
        for node in self.nodes():
            if hasattr(node, '_clean'):
                cleanbuffer.append((node, node._clean))
            node.clean = False
        for fct in self.functions(free=False):
            if fct.result_type.is_pointer and isinstance(fct.result_type.target, FundamentalTypeProxy):
                fct.clean = True
            elif any(parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in fct.parameters):
                fct.clean = True
        for cls in self.classes():
            for ctr in cls.constructors:
                if any(parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in ctr.parameters):
                    ctr.clean = True
        self._clean(cleanbuffer)

    def _remove_duplicates(self):
        cleanbuffer =  []
        for node in self.nodes():
            if hasattr(node, '_clean'):
                cleanbuffer.append((node, node._clean))
            node.clean = False
        scopes = [self['::']]
        while len(scopes) > 0:
            scope = scopes.pop()
            if isinstance(scope, NamespaceProxy):
                scopes.extend(scope.namespaces())
            for cls in scope.classes():
                classes = cls.id
                if classes.startswith('class '):
                    classes = classes[6:]
                elif classes.startswith('union '):
                    classes = classes[6:]
                elif classes.startswith('struct '):
                    classes = classes[7:]
                classes = remove_regex(classes)
                classes = '^(class |struct |union |)' + classes + '$'
                classes = [cls for cls in scope.classes() if re.match(classes, cls.id)]
                if len(classes) > 1:
                    complete = [cls for cls in classes if cls.is_complete]
                    if len(complete) == 0:
                        warnings.warn('\'' + '\', \''.join(cls.id for cls in classes) + '\'', NoDefinitionWarning)
                        ids = [cls.id for cls in classes]
                        for fct in self.functions(free=False):
                            if fct.result_type.target.id in ids or any([parameter.type.target.id in ids for parameter in fct.parameters]):
                                fct.clean = True
                                warnings.warn('\'' + fct.globalname + '\'', SideEffectWarning)
                    elif len(complete) == 1:
                        complete = complete.pop()
                        classes = [cls for cls in classes if not cls.is_complete]
                        ids = [cls.id for cls in classes]
                        for node, edge in self._type_edges.iteritems():
                            if edge['target'] in ids:
                                edge['target'] = complete.id
                        for node, edges in self._base_edges.iteritems():
                            for index, edge in enumerate(edges):
                                if edge['base'] in ids:
                                    edges[index]['base'] = complete.id
                        scopes.append(complete)
                    else:
                        warnings.warn('\'' + '\', \''.join(cls.id for cls in classes) + '\'', MultipleDefinitionWarning)
                        ids = [cls.id for cls in classes]
                        for fct in self.functions(free=False):
                            if fct.result_type.target.id in ids or any([parameter.type.target.id in ids for parameter in fct.parameters]):
                                fct.clean = True
                                warnings.warn('\'' + fct.globalname + '\'', SideEffectWarning)
                    for cls in classes:
                        cls.clean = True
                elif len(classes) == 1:
                    scopes.append(classes.pop())
        temp = [node for node in self.nodes() if node.clean]
        colored = set()
        while len(temp) > 0:
            node = temp.pop()
            node.clean = True
            if not node.id in colored:
                if isinstance(node, DirectoryProxy):
                    temp.extend(node.glob())
                elif isinstance(node, FunctionProxy):
                    temp.extend(node.parameters)
                elif isinstance(node, ConstructorProxy):
                    temp.extend(node.parameters)
                elif isinstance(node, ClassProxy):
                    temp.extend(node.declarations())
                elif isinstance(node, NamespaceProxy):
                    temp.extend(node.declarations())
                colored.add(node.id)
        self._clean(cleanbuffer)

    def _compute_clean(self):
        if not self._cleaned:
            cleanbuffer = [(node, node._clean) for node in self.nodes() if hasattr(node, '_clean')]
            temp = []
            for node in self.nodes():
                if node.clean:
                    node.clean = True
                else:
                    temp.append(node)
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
                            header.clean = False
                if isinstance(node, (TypedefProxy, VariableProxy)):
                    underlying_type = node.type.target
                    if underlying_type.clean:
                        temp.append(underlying_type)
                    else:
                        underlying_type.clean = False
                elif isinstance(node, FunctionProxy):
                    result_type = node.result_type.target
                    if result_type.clean:
                        temp.append(result_type)
                    else:
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
            return cleanbuffer
        else:
            return []

    def clean(self):
        """
        """
        if not self._cleaned:
            previous = len(self)
            cleanbuffer = self._compute_clean()
            self.resolve_overloads()
            self._clean(cleanbuffer)
            self._cleaned = True
            return CleanedDiagnostic(previous, len(self))
        else:
            return AlreadyCleanedDiagnostic(len(self))

    def _clean(self, cleanbuffer):
        nodes = [node for node in self.nodes() if node.clean]
        for node in nodes:
            if not node.id in ['::', '/']:
                self._syntax_edges[node.parent.id].remove(node.id)
        for node in nodes:
            self._nodes.pop(node.id)
            self._syntax_edges.pop(node.id, None)
            self._base_edges.pop(node.id, None)
            self._type_edges.pop(node.id, None)
        self._reset_clean(cleanbuffer)

    def _reset_clean(self, cleanbuffer):
        for node in self.nodes():
            del node.clean
        for node, clean in cleanbuffer:
            if node.id in self:
                node.clean = clean

    def check_syntax(self):
        for node in self.nodes():
            if not node.id in ['/', '::'] and not node.id in self._syntax_edges[node.parent.id]:
                yield node

    def _read_translation_unit(self, tu, libclang):
        """
        """
        self._cleaned = False

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
                self._read_decl(child, '::', libclang, True)
        else:
            with warnings.catch_warnings() as w:
                warnings.simplefilter('always')
                for child in tu.get_children():
                    self._read_decl(child, '::', libclang, True)
                self._remove_duplicates()

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
                    try:
                        return self[spelling].id, specifiers
                    except:
                        warnings.warn('record not found')
                        break
                else:
                    target, _specifiers = self._read_builtin_type(qtype, libclang)
                    return target, _specifiers + specifiers
        else:
            specifiers = ' const' * qtype.is_const_qualified() + ' volatile' *  qtype.is_volatile_qualified()
            ttype = qtype.get_type_ptr_or_null()
            while True:
                if ttype is None:
                    raise warnings.warn(qtype.get_as_string(), NoneTypeWarning)
                elif ttype.get_type_class() is autowig.clang._type.TypeClass.Typedef:
                    qtype = ttype.get_canonical_type_internal()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                elif any([ttype.is_structure_or_class_type(), ttype.is_enumeral_type(), ttype.is_union_type()]):
                    with warnings.catch_warnings() as w:
                        tag = ttype.get_as_tag_decl()
                        tag = self._read_tag(tag, '', libclang, read=True)
                        return tag[0], specifiers
                elif ttype.is_pointer_type():
                    qtype = ttype.get_pointee_type()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + ' *' + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                elif ttype.is_rvalue_reference_type():
                    qtype = ttype.get_pointee_type()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + ' &&' + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                elif ttype.is_lvalue_reference_type():
                    qtype = ttype.get_pointee_type()
                    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + ' &' + specifiers
                    ttype = qtype.get_type_ptr_or_null()
                elif ttype.is_builtin_type():
                    return self._read_builtin_type(ttype, libclang), specifiers
                else:
                    warnings.warn('\'' + str(ttype.get_type_class()) + '\'', NotImplementedTypeWarning)
                    break

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
                warnings.warn('\'' + str(btype.kind) + '\'', NotImplementedTypeWarning)
        else:
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
                return UnsignedLongIntegerTypeProxy._node
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
                warnings.warn('\'' + str(btype.get_class_type()) + '\'', NotImplementedTypeWarning)

    def _read_enum(self, decl, scope, libclang, read):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            if decl.spelling == '':
                children = []
                decls = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                for child in decl.get_children():
                    if child.kind is CursorKind.ENUM_CONSTANT_DECL:
                        children.extend(self._read_enum_constant(child, spelling, libclang))
                        decls.append(child)
                filename = str(path(str(decl.location.file)).abspath())
                self.add_file(filename, language=self._language)
                for childspelling, child in zip(children, decls):
                    self._nodes[childspelling]['_header'] = filename
                    self._nodes[spelling]['decl'] = child
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
                if self[spelling].is_complete:
                    filename = str(path(str(decl.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    self._nodes[spelling]['decl'] = decl
                return [spelling]
        else:
            filename = str(path(str(decl.get_filename())).abspath())
            self.add_file(filename, language=self._language)
            if decl.get_name() == '':
                children = []
                decls = []
                for child in decl.get_children():
                    children.extend(self._read_enum_constant(child, '', libclang))
                    decls.append(child)
                for childspelling, child in zip(children, decls):
                    self._nodes[childspelling]['_header'] = filename
                    self._nodes[childspelling]['decl'] = child
                return children
            else:
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter("error")
                        parent = self._read_syntaxic_parent(decl, libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for enum \'' + decl.get_name() + '\'', warning.__class__)
                    return []
                else:
                    if isinstance(parent, autowig.clang.TranslationUnitDecl):
                        scope = '::'
                        spelling = scope + decl.get_name()
                    else:
                        scope = self._read_decl(parent, '', libclang, read=False)
                        if len(scope) == 0:
                            warnings.warn(spelling, UndeclaredParentWarning)
                            return []
                        elif len(scope) == 1:
                            scope = scope[0]
                        else:
                            warnings.warn(spelling, MultipleDeclaredParentWarning)
                            return []
                        spelling = scope + '::' + decl.get_name()
                        if spelling.startswith('class '):
                            spelling = spelling[6:]
                        elif spelling.startswith('union '):
                            spelling = spelling[6:]
                        elif spelling.startswith('struct '):
                            spelling = spelling[7:]
                    if not spelling.startswith('enum '):
                        spelling = 'enum ' + spelling
                    if not spelling in self._nodes:
                        self._nodes[spelling] = dict(proxy=EnumProxy)
                        self._syntax_edges[spelling] = []
                        self._syntax_edges[scope].append(spelling)
                    elif not self[spelling].is_complete:
                        self._syntax_edges[scope].remove(spelling)
                        self._syntax_edges[scope].append(spelling)
                    if read and not self[spelling].is_complete:
                        for child in decl.get_children():
                            self._read_enum_constant(child, spelling, libclang)
                    if read and self[spelling].is_complete:
                        self._nodes[spelling]['_header'] = filename
                        self._nodes[spelling]['decl'] = decl
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
            try:
                with warnings.catch_warnings() as w:
                    warnings.simplefilter("error")
                    parent = self._read_context_parent(decl, libclang)
            except Warning as warning:
                warnings.warn(warning.message + ' for enum constant \'' + decl.get_name() + '\'', warning.__class__)
                return []
            else:
                if isinstance(parent, autowig.clang.TranslationUnitDecl):
                    scope = '::'
                    spelling = scope + decl.get_name()
                else:
                    scope = self._read_decl(parent, '', libclang, read=False)
                    if len(scope) == 0:
                        warnings.warn(spelling, UndeclaredParentWarning)
                        return []
                    elif len(scope) == 1:
                        scope = scope[0]
                    else:
                        warnings.warn(spelling, MultipleDeclaredParentWarning)
                        return []
                    spelling = scope + '::' + decl.get_name()
                    if spelling.startswith('enum '):
                        spelling = spelling[5:]
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
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter("error")
                        target, specifiers = self._read_qualified_type(typedef.underlying_typedef_type, libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for typedef \'' + spelling + '\'', warning.__class__)
                    return []
                else:
                    self._nodes[spelling] = dict(proxy=TypedefProxy)
                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                    self._syntax_edges[scope].append(spelling)
                    filename = str(path(str(typedef.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    return [spelling]
            else:
                return [spelling]
        else:
            warnings.warn(typedef.get_name(), NotImplementedDeclWarning)
            return []

    def _read_variable(self, decl, scope, libclang):
        if libclang:
            if any(child.kind in [CursorKind.TEMPLATE_NON_TYPE_PARAMETER, CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_TEMPLATE_PARAMETER] for child in decl.get_children()):
                return []
            else:
                if not scope.endswith('::'):
                    spelling = scope + "::" + decl.spelling
                else:
                    spelling = scope + decl.spelling
                try:
                    with warnings.catch_warnings() as warning:
                        warnings.simplefilter("error")
                        target, specifiers = self._read_qualified_type(decl.type, libclang)
                        self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                except Warning as warning:
                    warnings.warn(warning.message + ' for variable \'' + spelling + '\'', warning.__class__)
                    return []
                else:
                    self._nodes[spelling] = dict(proxy=VariableProxy)
                    filename = str(path(str(decl.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    self._nodes[spelling]['decl'] = decl
                    self._syntax_edges[scope].append(spelling)
                    return [spelling]
        else:
            if isinstance(decl, (autowig.clang.VarTemplateDecl, autowig.clang.VarTemplateSpecializationDecl)):
                return []
            else:
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter("error")
                        parent = self._read_context_parent(decl, libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for variable \'' + decl.get_name() + '\'', warning.__class__)
                    return []
                else:
                    if isinstance(parent, autowig.clang.TranslationUnitDecl):
                        scope = '::'
                        spelling = scope + decl.get_name()
                    else:
                        scope = self._read_decl(parent, '', libclang, read=False)
                        if len(scope) == 0:
                            warnings.warn(spelling, UndeclaredParentWarning)
                            return []
                        elif len(scope) == 1:
                            scope = scope[0]
                        else:
                            warnings.warn(spelling, MultipleDeclaredParentWarning)
                            return []
                        spelling = scope + '::' + decl.get_name()
                    try:
                        with warnings.catch_warnings() as warning:
                            warnings.simplefilter("error")
                            target, specifiers = self._read_qualified_type(decl.get_type(), libclang)
                            self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                    except Warning as warning:
                        warnings.warn(warning.message + ' for variable \'' + spelling + '\'', warning.__class__)
                        return []
                    else:
                        self._nodes[spelling] = dict(proxy=VariableProxy)
                        self._syntax_edges[scope].append(spelling)
                        filename = str(path(str(decl.get_filename())).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                        self._nodes[spelling]['decl'] = decl
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
                    self._nodes[spelling] = dict(proxy=FunctionProxy, decl=decl)
                    if not decl.location is None:
                        filename = str(path(str(decl.location.file)).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                elif decl.kind is CursorKind.CXX_METHOD:
                    self._nodes[spelling] = dict(proxy=MethodProxy,
                            is_static=decl.is_static_method(),
                            is_virtual=True,
                            is_const=False,
                            is_pure_virtual=True,
                            decl=decl)
                elif decl.kind is CursorKind.CONSTRUCTOR:
                    self._nodes[spelling] = dict(proxy=ConstructorProxy,
                            decl=decl)
                else:
                    self._nodes[spelling] = dict(proxy=DestructorProxy,
                            is_virtual=True,
                            decl=decl)
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
                except Warning as warning:
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
                    warnings.warn(warning.message, warning.__class__)
                    return []
                else:
                    return [spelling]
        else:
            if isinstance(decl, autowig.clang.FunctionTemplateDecl) or decl.is_implicit() or decl.is_deleted():
                return []
            if decl.get_name() == '':
                warnings.warn('', AnonymousFunctionWarning)
                return []
            try:
                with warnings.catch_warnings() as w:
                    warnings.simplefilter('error')
                    if isinstance(decl, autowig.clang.CXXMethodDecl):
                        parent = self._read_lexical_parent(decl, libclang)
                        if isinstance(parent, autowig.clang.NamespaceDecl):
                            return []
                    parent = self._read_syntaxic_parent(decl, libclang)
            except Warning as warning:
                warnings.warn(warning.message + ' for function \'' + decl.get_name() + '\'', warning.__class__)
                return []
            else:
                if isinstance(parent, autowig.clang.TranslationUnitDecl):
                    scope = '::'
                    spelling = scope + decl.get_name()
                else:
                    scope = self._read_decl(parent, '', libclang, read=False)
                    if len(scope) == 0:
                        warnings.warn(spelling, UndeclaredParentWarning)
                        return []
                    elif len(scope) == 1:
                        scope = scope[0]
                    else:
                        warnings.warn(spelling, MultipleDeclaredParentWarning)
                        return []
                    spelling =  scope + '::' + decl.get_name()
                if not isinstance(decl, autowig.clang.CXXDestructorDecl):
                    spelling += '::' + str(uuid.uuid5(uuid.NAMESPACE_X500, decl.get_mangling()))
                    #spelling =  spelling + '::' + str(uuid.uuid4())
                if not spelling in self._nodes:
                    if isinstance(decl, autowig.clang.CXXMethodDecl):
                        if spelling.startswith('class '):
                            spelling = spelling[6:]
                        elif spelling.startswith('union '):
                            spelling = spelling[6:]
                        elif spelling.startswith('struct '):
                            spelling = spelling[7:]
                        if isinstance(decl, autowig.clang.CXXConversionDecl):
                            warnings.warn(autowig.clang.CXXConversionDecl.__class__.__name__.split('.')[-1] + ' for function \'' + spelling + '\'',
                                    NotImplementedDeclWarning)
                            return []
                        elif isinstance(self[scope], NamespaceProxy):
                            return []
                        else:
                            if not isinstance(decl, autowig.clang.CXXDestructorDecl):
                                self._syntax_edges[spelling] = []
                                try:
                                    with warnings.catch_warnings() as warning:
                                        warnings.simplefilter("error")
                                        for index, child in enumerate(decl.get_children()):
                                            childspelling = spelling + child.spelling()
                                            if childspelling.endswith('::'):
                                                childspelling += 'parm_' + str(index)
                                            target, specifiers = self._read_qualified_type(child.get_type(),
                                                    libclang)
                                            self._type_edges[childspelling] = dict(target=target,
                                                    specifiers=specifiers)
                                            self._nodes[childspelling] = dict(proxy=VariableProxy)
                                            self._syntax_edges[spelling].append(childspelling)
                                except Warning as warning:
                                    message = warning.message + ' for parameter \'' + childspelling + '\''
                                    self._syntax_edges.pop(spelling)
                                    for index, child in enumerate(decl.get_children()):
                                        childspelling = spelling + child.spelling()
                                        if childspelling.endswith('::'):
                                            childspelling += 'parm_' + str(index)
                                        self._nodes.pop(childspelling, None)
                                        self._type_edges.pop(childspelling, None)
                                    warnings.warn(message,
                                            warning.__class__)
                                    return []
                                else:
                                    if not isinstance(decl, autowig.clang.CXXConstructorDecl):
                                        try:
                                            with warnings.catch_warnings() as warning:
                                                warnings.simplefilter("error")
                                                target, specifiers = self._read_qualified_type(decl.get_return_type(),
                                                        libclang)
                                        except Warning as warning:
                                            self._syntax_edges.pop(spelling)
                                            for index, child in enumerate(decl.get_children()):
                                                childspelling = spelling + child.spelling()
                                                if childspelling.endswith('::'):
                                                    childspelling += 'parm_' + str(index)
                                                self._nodes.pop(childspelling, None)
                                                self._type_edges.pop(childspelling, None)
                                            warnings.warn(warning.message + ' for function \'' + spelling + '\' return type',
                                                    warning.__class__)
                                            return []
                                        else:
                                            self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                                            self._nodes[spelling] = dict(proxy=MethodProxy,
                                                    is_static=decl.is_static(),
                                                    is_const=decl.is_const(),
                                                    is_volatile=decl.is_volatile(),
                                                    is_virtual=decl.is_virtual(),
                                                    decl=decl)
                                    else:
                                        self._nodes[spelling] = dict(proxy=ConstructorProxy,
                                                is_virtual=decl.is_virtual(),
                                                decl=decl)
                                    self._syntax_edges[scope].append(spelling)
                                    return [spelling]
                            else:
                                if not spelling in self._nodes:
                                    self._nodes[spelling] = dict(proxy=DestructorProxy,
                                            virtual=decl.is_virtual(),
                                            decl=decl)
                                    self._syntax_edges[scope].append(spelling)
                                return [spelling]
                    else:
                        self._syntax_edges[spelling] = []
                        try:
                            with warnings.catch_warnings() as warning:
                                warnings.simplefilter("error")
                                for index, child in enumerate(decl.get_children()):
                                    childspelling = spelling + child.spelling()
                                    if childspelling.endswith('::'):
                                        childspelling += 'parm_' + str(index)
                                    target, specifiers = self._read_qualified_type(child.get_type(),
                                            libclang)
                                    self._type_edges[childspelling] = dict(target=target,
                                            specifiers=specifiers)
                                    self._nodes[childspelling] = dict(proxy=VariableProxy)
                                    self._syntax_edges[spelling].append(childspelling)
                        except Warning as warning:
                            message = warning.message + ' for parameter \'' + childspelling + '\''
                            self._syntax_edges.pop(spelling)
                            for index, child in enumerate(decl.get_children()):
                                childspelling = spelling + child.spelling()
                                if childspelling.endswith('::'):
                                    childspelling += 'parm_' + str(index)
                                self._nodes.pop(childspelling, None)
                                self._type_edges.pop(childspelling, None)
                            warnings.warn(message,
                                    warning.__class__)
                            return []
                        else:
                            try:
                                with warnings.catch_warnings() as warning:
                                    warnings.simplefilter("error")
                                    target, specifiers = self._read_qualified_type(decl.get_return_type(),
                                            libclang)
                            except Warning as warning:
                                message = warning.message + ' for function \'' + spelling + '\''
                                self._syntax_edges.pop(spelling)
                                for index, child in enumerate(decl.get_children()):
                                    childspelling = spelling + child.spelling()
                                    if childspelling.endswith('::'):
                                        childspelling += 'parm_' + str(index)
                                    self._nodes.pop(childspelling, None)
                                    self._type_edges.pop(childspelling, None)
                                self._type_edges.pop(spelling, None)
                                warnings.warn(message,
                                        warning.__class__)
                                return []
                            else:
                                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                                self._nodes[spelling] = dict(proxy=FunctionProxy,
                                        decl=decl)
                                self._syntax_edges[scope].append(spelling)
                                return [spelling]

    def _read_field(self, decl, scope, libclang):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            self._nodes[spelling] = dict(proxy=FieldProxy,
                    is_mutable=False,
                    is_static=False,
                    decl=decl)
            self._syntax_edges[scope].append(spelling)
            try:
                with warnings.catch_warnings() as warning:
                    warnings.simplefilter("error")
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
            if decl.get_name() == '':
                warnings.warn('', AnonymousFieldWarning)
                return []
            try:
                with warnings.catch_warnings() as w:
                    warnings.simplefilter('error')
                    parent = self._read_context_parent(decl, libclang)
            except Warning as warning:
                warnings.warn(warning.message + ' for field \'' + decl.get_name() + '\'', warning.__class__)
                return []
            else:
                if isinstance(parent, autowig.clang.TranslationUnitDecl):
                    scope = '::'
                    spelling = scope + decl.get_name()
                else:
                    scope = self._read_decl(parent, '', libclang, read=False)
                    if len(scope) == 0:
                        warnings.warn(spelling, UndeclaredParentWarning)
                        return []
                    elif len(scope) == 1:
                        scope = scope[0]
                    else:
                        warnings.warn(spelling, MultipleDeclaredParentWarning)
                        return []
                    spelling = scope + '::' + decl.get_name()
                    if spelling.startswith('class '):
                        spelling = spelling[6:]
                    elif spelling.startswith('union '):
                        spelling = spelling[6:]
                    elif spelling.startswith('struct '):
                        spelling = spelling[7:]
                try:
                    with warnings.catch_warnings() as warning:
                        warnings.simplefilter("error")
                        target, specifiers = self._read_qualified_type(decl.get_type(), libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for field \'' + spelling + '\'', warning.__class__)
                    return []
                else:
                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                    self._nodes[spelling] = dict(proxy=FieldProxy,
                            is_mutable=decl.is_mutable(),
                            is_static=False, # TODO
                            decl=decl)
                    self._syntax_edges[scope].append(spelling)
                    return [spelling]

    def _read_tag(self, decl, scope, libclang, read):
        if libclang:
            if decl.kind is CursorKind.ENUM_DECL:
                return self._read_enum(decl, scope, libclang, read)
            else:
                if decl.spelling == '':
                    warnings.warn('Anonymous struc/union/class in scope \'' + scope + '\' not read')
                    return []
                elif not decl.spelling == decl.displayname:
                    warnings.warn('Class template specialization \'' + scope + '::' + decl.displayname + '\' not read')
                    return []
                if not scope.endswith('::'):
                    spelling = scope + "::" + decl.spelling
                else:
                    spelling = scope + decl.spelling
                if not spelling in self._nodes:
                    if decl.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
                        self._nodes[spelling] = dict(proxy=ClassProxy,
                                default_access='public',
                                is_abstract=True,
                                is_copyable=False,
                                is_complete=False)
                    elif decl.kind is CursorKind.CLASS_DECL:
                        self._nodes[spelling] = dict(proxy=ClassProxy,
                                    default_access='private',
                                    is_abstract=True,
                                    is_copyable=False,
                                    is_complete=False)
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
                                    is_virtual=False))
                            else:
                                warnings.warn('Base not found')
                        else:
                            for childspelling in self._read_decl(child, spelling, libclang, read):
                                self._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                                dict.pop(self._nodes[childspelling], "_header", None)
                    self._nodes[spelling]['is_complete'] = len(self._base_edges[spelling]) + len(self._syntax_edges[spelling]) > 0
                    if self[spelling].is_complete:
                        filename = str(path(str(decl.location.file)).abspath())
                        self.add_file(filename, language=self._language)
                        self._nodes[spelling]['_header'] = filename
                        self._nodes[spelling]['decl'] = decl
                return [spelling]
        else:
            if isinstance(decl, autowig.clang.EnumDecl):
                return self._read_enum(decl, scope, libclang, read)
            elif isinstance(decl, (autowig.clang.ClassTemplateDecl, autowig.clang.ClassTemplatePartialSpecializationDecl)):
                return []
            if not decl.has_name_for_linkage():
                warnings.warn('in scope \'' + scope + '\'', AnonymousClassWarning)
                return []
            if not decl.get_typedef_name_for_anon_decl() is None:
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter('error')
                        parent = self._read_syntaxic_parent(decl, libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for class \'' + decl.get_typedef_name_for_anon_decl().get_name() + '\'', warning.__class__)
                    return []
                else:
                    if isinstance(parent, autowig.clang.TranslationUnitDecl):
                        scope = '::'
                        spelling = scope + decl.get_typedef_name_for_anon_decl().get_name()
                    else:
                        scope = self._read_decl(parent, '', libclang, read=False)
                        if len(scope) == 0:
                            warnings.warn(spelling, UndeclaredParentWarning)
                            return []
                        elif len(scope) == 1:
                            scope = scope[0]
                        else:
                            warnings.warn(spelling, MultipleDeclaredParentWarning)
                            return []
                        spelling = scope + '::' + decl.get_typedef_name_for_anon_decl().get_name()
                        if spelling.startswith('class '):
                            spelling = spelling[6:]
                        elif spelling.startswith('union '):
                            spelling = spelling[6:]
                        elif spelling.startswith('struct '):
                            spelling = spelling[7:]
            elif decl.get_name() == '':
                warnings.warn('in scope \'' + scope + '\'', AnonymousClassWarning)
                return []
            else:
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter('error')
                        parent = self._read_syntaxic_parent(decl, libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for class \'' + decl.get_typedef_name_for_anon_decl().get_name() + '\'', warning.__class__)
                    return []
                else:
                    if isinstance(parent, autowig.clang.TranslationUnitDecl):
                        scope = '::'
                        spelling = scope + decl.get_name()
                    else:
                        scope = self._read_decl(parent, '', libclang, read=False)
                        if len(scope) == 0:
                            warnings.warn(spelling, UndeclaredParentWarning)
                            return []
                        elif len(scope) == 1:
                            scope = scope[0]
                        else:
                            warnings.warn(spelling, MultipleDeclaredParentWarning)
                            return []
                        spelling = scope + '::' + decl.get_name()
                        if spelling.startswith('class '):
                            spelling = spelling[6:]
                        elif spelling.startswith('union '):
                            spelling = spelling[6:]
                        elif spelling.startswith('struct '):
                            spelling = spelling[7:]
                    if decl.is_class():
                        spelling = 'class ' + spelling
                    elif decl.is_struct():
                        spelling = 'struct ' + spelling
                    elif decl.is_union():
                        spelling = 'union ' + spelling
                    else:
                        warnings.warn(spelling, NotImplementedDeclWarning)
                        return []
            if not spelling in self._nodes:
                if decl.is_class():
                    default_access = 'private'
                else:
                    default_access = 'public'
                if isinstance(decl, autowig.clang.ClassTemplateSpecializationDecl):
                    self._nodes[spelling] = dict(proxy=ClassTemplateSpecializationProxy,
                        _scope = scope,
                        default_access=default_access,
                        is_abstract=False,
                        is_copyable=True,
                        is_complete=False)
                    self._template_edges[spelling] = []
                    templates = decl.get_template_args()
                    for template in [templates.get(index) for index in range(templates.size())]:
                        if template.get_kind() is autowig.clang._template_argument.ArgKind.Type:
                            target, specifiers = self._read_qualified_type(template.get_as_type(), libclang)
                            self._template_edges[spelling].append(dict(target = target, specifiers = specifiers))
                        elif template.get_kind() is autowig.clang._template_argument.ArgKind.Declaration:
                            target, specifiers = self._read_qualifier_type(template.get_as_decl().get_type(), libclang)
                            self._template_edges[spelling].append(dict(target = target, specifiers = specifiers))
                        else:
                            print spelling
                            print template.get_kind()
                else:
                    self._nodes[spelling] = dict(proxy=ClassProxy,
                        _scope = scope,
                        default_access=default_access,
                        is_abstract=False,
                        is_copyable=True,
                        is_complete=False)
                self._syntax_edges[spelling] = []
                self._base_edges[spelling] = []
                self._syntax_edges[scope].append(spelling)
            if read and not self[spelling].is_complete and decl.is_complete_definition():
                self._syntax_edges[scope].remove(spelling)
                self._syntax_edges[scope].append(spelling)
                if isinstance(decl, autowig.clang.CXXRecordDecl):
                    self._nodes[spelling]['is_abstract'] = decl.is_abstract()
                    self._nodes[spelling]['is_copyable'] = decl.is_copyable()
                else:
                    self._nodes[spelling]['is_abstract'] = False
                    self._nodes[spelling]['is_copyable'] = True
            if read and not self[spelling].is_complete and decl.is_complete_definition():
                self._nodes[spelling]['is_complete'] = True
                with warnings.catch_warnings() as w:
                    warnings.simplefilter('always')
                    self._base_edges[spelling] = []
                    for base in decl.get_bases():
                        basespelling, specifiers = self._read_qualified_type(base.get_type(), libclang)
                        self._base_edges[spelling].append(dict(base=self[basespelling].id,
                            access=str(base.get_access_specifier()).strip('AS_'),
                            is_virtual=False))
                    for base in decl.get_virtual_bases():
                        basespelling, specifiers = self._read_qualified_type(base.get_type(), libclang)
                        self._base_edges[spelling].append(dict(base=self[basespelling].id,
                            access=str(base.get_access_specifier()).strip('AS_'),
                            is_virtual=True))
                    for child in decl.get_children():
                        access = str(child.get_access_unsafe()).strip('AS_')
                        for childspelling in self._read_decl(child, spelling, libclang, read):
                            self._nodes[childspelling]["access"] = access
                            dict.pop(self._nodes[childspelling], "_header", None)
                self._nodes[spelling]['is_complete'] = len(self._syntax_edges[spelling])+len(self._base_edges[spelling]) > 0
                if self[spelling].is_complete:
                    filename = str(path(str(decl.get_filename())).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    self._nodes[spelling]['decl'] = decl
            return [spelling]

    def _read_namespace(self, decl, scope, libclang, read):
        if libclang:
            if not scope.endswith('::'):
                spelling = scope + "::" + decl.spelling
            else:
                spelling = scope + decl.spelling
            if decl.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                with warnings.catch_warnings() as w:
                    warnings.simplefilter('always')
                    for child in decl.get_children():
                        children.extend(self._read_decl(child, spelling, libclang, read))
                return children
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(proxy=NamespaceProxy)
                    self._syntax_edges[spelling] = []
                if not spelling in self._syntax_edges[scope]:
                    self._syntax_edges[scope].append(spelling)
                with warnings.catch_warnings() as w:
                    warnings.simplefilter('always')
                    for child in decl.get_children():
                        self._read_decl(child, spelling, libclang, read)
                return [spelling]
        else:
            if decl.get_name() == '':
                with warnings.catch_warnings() as w:
                    warnings.simplefilter('always')
                    children = []
                    for child in decl.get_children():
                        children.extend(self._read_decl(child, '', libclang, read))
                    return children
            else:
                try:
                    with warnings.catch_warnings() as w:
                        warnings.simplefilter('error')
                        parent = self._read_syntaxic_parent(decl, libclang)
                except Warning as warning:
                    warnings.warn(warning.message + ' for namespace \'' + decl.get_name() + '\'', warning.__class__)
                    return []
                else:
                    if isinstance(parent, autowig.clang.TranslationUnitDecl):
                        scope = '::'
                        spelling = scope + decl.get_name()
                    else:
                        scope = self._read_decl(parent, '', libclang, read=False)
                        if len(scope) == 0:
                            warnings.warn(spelling, UndeclaredParentWarning)
                            return []
                        elif len(scope) == 1:
                            scope = scope[0]
                        else:
                            warnings.warn(spelling, MultipleDeclaredParentWarning)
                            return []
                        spelling = scope + '::' + decl.get_name()
                    if not spelling in self._nodes:
                        self._nodes[spelling] = dict(proxy=NamespaceProxy)
                        self._syntax_edges[spelling] = []
                    if not spelling in self._syntax_edges[scope]:
                        self._syntax_edges[scope].append(spelling)
                    if read:
                        with warnings.catch_warnings() as w:
                            warnings.simplefilter('always')
                            for child in decl.get_children():
                                self._read_decl(child, spelling, libclang, read)
                    return [spelling]

    def _read_decl(self, decl, scope, libclang, read):
        """
        """
        if libclang:
            if decl.kind is CursorKind.UNEXPOSED_DECL:
                if decl.spelling == '':
                    children = []
                    for child in decl.get_children():
                        children.extend(self._read_decl(child, scope, libclang, read))
                    return children
                else:
                    warnings.warn('Named unexposed declaration not read')
                    return []
            elif decl.kind is CursorKind.TYPEDEF_DECL:
                return self._read_typedef(decl, scope, libclang)
            elif decl.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL]:
                return self._read_variable(decl, scope, libclang)
            elif decl.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
                    CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
                return self._read_function(decl, scope, libclang)
            elif decl.kind is CursorKind.FIELD_DECL:
                return self._read_field(decl, scope, libclang)
            elif decl.kind in [CursorKind.ENUM_DECL, CursorKind.STRUCT_DECL,
                    CursorKind.UNION_DECL, CursorKind.CLASS_DECL]:
                return self._read_tag(decl, scope, libclang, read)
            elif decl.kind is CursorKind.NAMESPACE:
                return self._read_namespace(decl, scope, libclang, read)
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
                if decl.get_language() is autowig.clang._linkage_spec_decl.LanguageIDs.lang_c:
                    self._language = 'c'
                else:
                    self._language = 'c++'
                children = []
                for child in decl.get_children():
                    children = self._read_decl(child, scope, libclang, read)
                self._language = language
                return children
            elif isinstance(decl, autowig.clang.VarDecl):
                return self._read_variable(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.FunctionDecl):
                return self._read_function(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.FieldDecl):
                return self._read_field(decl, scope, libclang)
            elif isinstance(decl, autowig.clang.TagDecl):
                return self._read_tag(decl, scope, libclang, read)
            elif isinstance(decl, autowig.clang.NamespaceDecl):
                return self._read_namespace(decl, scope, libclang, read)
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
                warnings.warn(decl.__class__.__name__, NotImplementedDeclWarning) #.split('.')[-1]
                return []

    def _read_lexical_parent(self, decl, libclang):
        if libclang:
            raise NotImplementedError()
        else:
            return self._read_parent(decl.get_lexical_parent(), libclang)

    def _read_syntaxic_parent(self, decl, libclang):
        if libclang:
            raise NotImplementedError()
        else:
            return self._read_parent(decl.get_parent(), libclang)

    def _read_context_parent(self, decl, libclang):
        if libclang:
            raise NotImplementedError()
        else:
            return self._read_parent(decl.get_decl_context(), libclang)

    def _read_parent(self, parent, libclang):
        if libclang:
            raise NotImplementedError()
        else:
            kind = parent.get_decl_kind()
            if kind is autowig.clang._decl.Kind.Namespace:
                parent = autowig.clang.cast.cast_as_namespace_decl(parent)
                if parent.get_name() == '':
                    parent = self._read_parent(parent.get_parent(), libclang)
                return parent
            elif kind in [autowig.clang._decl.Kind.CXXRecord, autowig.clang._decl.Kind.Record, autowig.clang._decl.Kind.firstCXXRecord, autowig.clang._decl.Kind.firstClassTemplateSpecialization, autowig.clang._decl.Kind.firstRecord]:
                parent = autowig.clang.cast.cast_as_record_decl(parent)
                if parent.get_name() == '':
                    parent = self._read_parent(parent.get_parent(), libclang)
                return parent
            elif kind in [autowig.clang._decl.Kind.Enum]:
                parent = autowig.clang.cast.cast_as_enum_decl(parent)
                if parent.get_name() == '':
                    parent = self._read_parent(parent.get_parent(), libclang)
                return parent
            elif kind is autowig.clang._decl.Kind.LinkageSpec:
                return self._read_parent(self._read_parent(parent.get_parent(), libclang), libclang)
            elif kind in [autowig.clang._decl.Kind.TranslationUnit, autowig.clang._decl.Kind.lastDecl]:
                return autowig.clang.cast.cast_as_translation_unit_decl(parent)
            elif kind in [autowig.clang._decl.Kind.ClassTemplatePartialSpecialization, autowig.clang._decl.Kind.firstTemplate, autowig.clang._decl.Kind.firstVarTemplateSpecialization, autowig.clang._decl.Kind.lastTag, autowig.clang._decl.Kind.lastRedeclarableTemplate, autowig.clang._decl.Kind.lastTemplate]:
                warnings.warn('', TemplateParentWarning)
            else:
                warnings.warn(kind, NotImplementedParentWarning)

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if not node in self._nodes:
            try:
                pattern = re.compile(node)
                return [self[_node] for _node in sorted(self._nodes) if pattern.match(_node)]
            except:
                raise
                #ValueError('`node` parameter is not a valid regex pattern')
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

class CleanedDiagnostic(object):

    def __init__(self, previous, current):
        self.previous = previous
        self.current = current

    def __repr__(self):
        return 'Previous number of nodes: ' + str(self.previous) + '\nCurrent number of nodes: ' + str(self.current) + '\nPercentage of nodes cleaned: ' + str(round((self.previous-self.current)/float(self.previous)*100, 2)) + '%'

class AlreadyCleanedDiagnostic(object):

    def __init__(self, current):
        self.current = current

    def __repr__(self):
        return 'Number of nodes: ' + self.current
