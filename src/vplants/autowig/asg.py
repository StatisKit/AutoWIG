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

from .tools import subclasses, split_scopes, remove_templates
from .custom_warnings import NotWrittenFileWarning, ErrorWarning, NoneTypeWarning,  UndeclaredParentWarning, MultipleDeclaredParentWarning, MultipleDefinitionWarning, NoDefinitionWarning, SideEffectWarning, ProtectedFileWarning, InfoWarning, TemplateParentWarning, TemplateParentWarning, AnonymousWarning, AnonymousFunctionWarning, AnonymousFieldWarning, AnonymousClassWarning, NotImplementedWarning, NotImplementedTypeWarning, NotImplementedDeclWarning, NotImplementedParentWarning, NotImplementedOperatorWarning, NotImplementedTemplateWarning

__all__ = ['AbstractSemanticGraph']

class NodeProxy(object):
    """
    """

    def __init__(self, asg, node):
        self._asg = asg
        self._node = node

    def __eq__(self, other):
        return self.asg == other.asg and self.node == other.node

    @property
    def asg(self):
        return self._asg

    @property
    def node(self):
        return self._node

    @property
    def hash(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self.node)).replace('-', '_')

    def __repr__(self):
        return self.node

    def __dir__(self):
        return sorted([key for key in self.asg._nodes[self.node].keys() if not key.startswith('_')])

    def __getattr__(self, attr):
        try:
            return self.asg._nodes[self.node][attr]
        except:
            raise #AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')

    def _remove(self):
        self.asg._nodes.pop(self.node)

class EdgeProxy(object):
    """
    """


class DirectoryProxy(NodeProxy):
    """
    """

    @property
    def globalname(self):
        return self.node

    @property
    def localname(self):
        return self.globalname[self.globalname.rfind(os.sep, 0, -1)+1:]

    @property
    def parent(self):
        parent = os.sep.join(self.globalname.split(os.sep)[:-2]) + os.sep
        if parent == '':
            parent = os.sep
        return self.asg[parent]

    @property
    def depth(self):
        if self.globalname == os.sep:
            return 0
        else:
            return self.parent.depth+1

    def makedirs(self):
        if not self.on_disk:
            os.makedirs(self.globalname)
            self.asg._nodes[self.node]['on_disk'] = True

    def remove(self, recursive=False, force=False):
        if self.on_disk:
            if recursive:
                for dirnode in reversed(sorted(self.walkdirs(), key=lambda node: node.depth)):
                    dirnode.remove(False, force=force)
            for filenode in self.glob():
                filenode.remove(force=force)
            os.rmdir(self.globalname)
            self.asg._nodes[self.node]['on_disk'] = False

    def _remove(self):
        super(DirectoryProxy, self)._remove()
        if not self.node == '/':
            self.asg._syntax_edges[self.parent.node].remove(self.node)
        self.asg._syntax_edges.pop(self.node)

class FileProxy(NodeProxy):
    """
    """

    @property
    def globalname(self):
        return self.node

    @property
    def localname(self):
        return self.globalname[self.globalname.rfind(os.sep)+1:]

    @property
    def suffix(self):
        return self.localname[self.localname.rfind('.'):]

    def touch(self):
        parent = self.parent
        if not parent.on_disk:
            parent.makedirs()
        filehandler = open(self.globalname, 'w')
        filehandler.close()
        self.asg._nodes[self.node]['on_disk'] = True

    def write(self, force=False):
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
            self.asg._nodes[self.node]['on_disk'] = True

    def remove(self, force=False):
        os.remove(self.globalname)
        self.asg._nodes[self.node]['on_disk'] = False

    @property
    def is_empty(self):
        return str(self) == ""

    def __repr__(self):
        return self.node

    def __str__(self):
        return self.content

    def md5(self):
        return hashlib.md5(str(self)).hexdigest()

    @property
    def parent(self):
        return self.asg[os.sep.join(self.globalname.split(os.sep)[:-1]) + os.sep]


    def _remove(self):
        super(FileProxy, self)._remove()
        self.asg._syntax_edges[self.parent.node].remove(self.node)

def get_language(self):
    if hasattr(self, '_language'):
        return self._language
    else:
        return None

def set_language(self, language):
    self.asg._nodes[self.node]['_language'] = language

def del_language(self):
    self.asg._nodes[self.node].pop('_language', None)

FileProxy.language = property(get_language, set_language, del_language)
del get_language, set_language, del_language

def get_parsed(self):
    if hasattr(self, '_parsed'):
        return self._parsed
    else:
        return False

def set_parsed(self, parsed):
    self.asg._nodes[self.node]['_parsed'] = parsed

def del_parsed(self):
    self.asg._nodes[self.node].pop('_parsed', None)

FileProxy.parsed = property(get_parsed, set_parsed, del_parsed)
del get_parsed, set_parsed, del_parsed

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
    self.asg._nodes[self.node]['_content'] = content

def del_content(self):
    self.asg._nodes[self._id].pop('_content', False)

FileProxy.content = property(get_content, set_content, del_content)
del get_content, set_content, del_content

class CodeNodeProxy(NodeProxy):

    @property
    def header(self):
        try:
            return self.asg[self._header]
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

    @property
    def ancestors(self):
        ancestors = [self.parent]
        while not ancestors[-1].globalname == '::':
            ancestors.append(ancestors[-1].parent)
        return reversed(ancestors)

    def _remove(self):
        super(CodeNodeProxy, self)._remove()
        if not self.node == '::':
            self.asg._syntax_edges[self.parent.node].remove(self.node)

class FundamentalTypeProxy(CodeNodeProxy):
    """
    http://www.cplusplus.com/doc/tutorial/variables/
    """

    @property
    def globalname(self):
        return self.node.lstrip('::')

    @property
    def localname(self):
        return self.globalname

    def __str__(self):
        return self.node

    @property
    def parent(self):
        return self.asg['::']

    def _remove(self):
        pdb.set_trace()

class UnexposedTypeProxy(FundamentalTypeProxy):
    """
    """

    node = '::unexposed'

class CharacterFundamentalTypeProxy(FundamentalTypeProxy):
    """
    """

class CharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    node = '::char'

class UnsignedCharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    node = '::unsigned char'

class SignedCharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    node = '::signed char'

class Char16TypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    node = "::char16_t"

class Char32TypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    node = "::char32_t"

class WCharTypeProxy(CharacterFundamentalTypeProxy):
    """
    """

    node = "::wchar_t"

class SignedIntegerTypeProxy(FundamentalTypeProxy):
    """
    """

class SignedShortIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::short"

class SignedIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::int"

class SignedLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::long"

class SignedLongLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::long long"

class UnsignedIntegerTypeProxy(FundamentalTypeProxy):
    """
    """

class UnsignedShortIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned short"

class UnsignedIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned int"

class UnsignedLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned long"

class UnsignedLongLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned long long"

class SignedFloatingPointTypeProxy(FundamentalTypeProxy):
    """
    """

class SignedFloatTypeProxy(SignedFloatingPointTypeProxy):
    """
    """

    node = "::float"

class SignedDoubleTypeProxy(SignedFloatingPointTypeProxy):
    """
    """

    node = "::double"

class SignedLongDoubleTypeProxy(SignedFloatingPointTypeProxy):
    """
    """

    node = "::long double"

class BoolTypeProxy(FundamentalTypeProxy):
    """
    """

    node = "::bool"

class ComplexTypeProxy(FundamentalTypeProxy):
    """
    """

    node = "::_Complex float"

class NullPtrTypeProxy(FundamentalTypeProxy):
    """
    """

    node = "::null_ptr"

class VoidTypeProxy(FundamentalTypeProxy):
    """
    """

    node = "::void"

class TypeSpecifiersProxy(EdgeProxy):
    """
    http://en.cppreference.com/w/cpp/language/declarations
    """

    def __init__(self, asg, source):
        self._asg = asg
        self._source = source

    @property
    def asg(self):
        return self._asg

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self.asg[self.asg._type_edges[self._source]["target"]]

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
        nested = TypeSpecifiersProxy(self.asg, self._source)
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
        return self.asg._type_edges[self._source]["specifiers"]
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
        return re.sub('::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', '', self.node)

    @property
    def localname(self):
        return split_scopes(self.globalname)[-1]

    @property
    def parent(self):
        parent = self.node[:self.node.rindex(':')-1]
        if parent == '':
            return self.asg['::']
        else:
            return self.asg[parent]

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
            return self.asg['::']
        else:
            for decorator in ['enum', 'class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
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
            return self.asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
            return parent

    @property
    def is_complete(self):
        return len(self.asg._syntax_edges[self.node]) > 0

    @property
    def constants(self):
        return [self.asg[node] for node in self.asg._syntax_edges[self.node]]

    def _remove(self):
        for cst in self.constants:
            cst._remove()
        for tdf in self.asg.typedefs():
            if tdf.node in self.asg:
                if tdf.type.target == self:
                    tdf._remove()
        for fct in self.asg.functions():
            if fct.result_type.target == self or any(prm.type.target == self for prm in fct.parameters):
                fct._remove()
        for var in self.asg.variables():
            if var.type.target == self:
                var._remove()
        for cls in self.asg.classes():
            for ctr in cls.constructors:
                if any(prm.type.target == self for prm in ctr.parameters):
                    ctr._remove()
        super(DeclarationProxy, self)._remove()

class TypedefProxy(DeclarationProxy):
    """
    """

    @property
    def type(self):
        return TypeSpecifiersProxy(self.asg, self.node)

    def _remove(self):
        for tdf in self.asg.typedefs():
            if tdf.node in self.asg:
                if tdf.type.target == self:
                    tdf._remove()
        for fct in self.asg.functions():
            if fct.result_type.target == self or any(prm.type.target == self for prm in fct.parameters):
                fct._remove()
        for var in self.asg.variables():
            if var.type.target == self:
                var._remove()
        for cls in self.asg.classes():
            for ctr in cls.constructors:
                if any(prm.type.target == self for prm in ctr.parameters):
                    ctr._remove()
        super(TypedefProxy, self)._remove()
        self.asg._type_edges.pop(self.node)

class VariableProxy(DeclarationProxy):
    """
    """

    @property
    def type(self):
        return TypeSpecifiersProxy(self.asg, self.node)

    def _remove(self):
        super(VariableProxy, self)._remove()
        self.asg._type_edges.pop(self.node)

class ParameterProxy(VariableProxy):
    """
    """

    @property
    def is_anonymous(self):
        return re.match('(.*)parm_[0-9]*$', self.node)

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
            return self.asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
            return parent

class FunctionProxy(DeclarationProxy):
    """
    """

    @property
    def result_type(self):
        return TypeSpecifiersProxy(self.asg, self.node)

    @property
    def nb_parameters(self):
        return len(self.asg._syntax_edges[self.node])

    @property
    def parameters(self):
        return [self.asg[node] for node in self.asg._syntax_edges[self.node]]

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
            return self.asg['::']
        else:
            return self.asg[parent]

    def _remove(self):
        for prm in self.parameters:
            prm._remove()
        super(FunctionProxy, self)._remove()
        self.asg._syntax_edges.pop(self.node)
        self.asg._type_edges.pop(self.node)

def get_is_overloaded(self):
    if not hasattr(self, '_is_overloaded'):
        if len(self.overloads) == 1:
            return False
        else:
            return True
    else:
        return self._is_overloaded

def set_is_overloaded(self, is_overloaded):
    self.asg._nodes[self.node]["_is_overloaded"] = is_overloaded

def del_is_overloaded(self):
    self.asg._nodes[self.node].pop("_is_overloaded", False)

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
            return self.asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
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
            return self.asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
            return parent

    @property
    def nb_parameters(self):
        return len(self.asg._syntax_edges[self.node])

    @property
    def parameters(self):
        return [self.asg[node] for node in self.asg._syntax_edges[self.node]]

    def _remove(self):
        for prm in self.parameters:
            prm._remove()
        super(ConstructorProxy, self)._remove()
        self.asg._syntax_edges.pop(self.node)

class DestructorProxy(DeclarationProxy):
    """
    """

    @property
    def parent(self):
        parent = remove_templates(self.globalname)
        parent = parent[:parent.rindex(':')-1]
        if parent == '':
            return self.asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
            return parent

class ClassProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/class>_`
    """

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
            return self.asg['::']
        else:
            for decorator in ['class', 'struct', 'union']:
                decorator += ' ' + parent
                if decorator in self.asg._nodes:
                    parent = self.asg[decorator]
                    break
            if not isinstance(parent, NodeProxy):
                if not parent in self.asg._nodes:
                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
                parent = self.asg[parent]
            return parent

    @property
    def is_derived(self):
        return len(self.asg._base_edges[self.node]) > 0

    def bases(self, inherited=False):
        bases = []
        for base in self.asg._base_edges[self.node]:
            bases.append(self.asg[base['base']])
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
        return [cls for cls in self.asg.classes() if any(base.node == self.node for base in cls.bases(inherited=recursive))]

    @property
    def depth(self):
        if not self.is_derived:
            return 0
        else:
            if not hasattr(self, '_depth'):
                self.asg._nodes[self.node]['_depth'] = max([base.type.target.depth if isinstance(base, TypedefProxy) else base.depth for base in self.bases()])+1
            return self._depth

    def declarations(self, inherited=False):
        declarations = [self.asg[node] for node in self.asg._syntax_edges[self.node]]
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

    def classes(self, inherited=False, recursive=False):
        if recursive:
            classes = self.classes(inherited=inherited, recursive=False)
            for cls in classes:
                classes += cls.classes(inherited=inherited, recursive=True)
            return classes
        else:
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

    def _remove(self):
        for dcl in self.declarations():
            if dcl.node in self.asg:
                dcl._remove()
        for inh in self.inheritors():
            self.asg._base_edges[inh.node] = [base for base in self.asg._base_edges[inh.node] if not base['base'] == self.node]
        for tdf in self.asg.typedefs():
            if tdf.node in self.asg:
                if tdf.type.target == self:
                    tdf._remove()
        for fct in self.asg.functions():
            if fct.result_type.target == self or any(prm.type.target == self for prm in fct.parameters):
                fct._remove()
        for var in self.asg.variables():
            if var.type.target == self:
                var._remove()
        for cls in self.asg.classes():
            for ctr in cls.constructors:
                if any(prm.type.target == self for prm in ctr.parameters):
                    ctr._remove()
        super(ClassProxy, self)._remove()
        self.asg._base_edges.pop(self.node)
        self.asg._syntax_edges.pop(self.node)

def get_is_copyable(self):
    return self._is_copyable

def set_is_copyable(self, copyable):
    self.asg._nodes[self.node]['_is_copyable'] = copyable

ClassProxy.is_copyable = property(get_is_copyable, set_is_copyable)
del get_is_copyable, set_is_copyable

class TemplateTypeSpecifiersProxy(TypeSpecifiersProxy):

    def __init__(self, asg, source, target):
        super(TemplateTypeSpecifiersProxy, self).__init__(asg, source)
        self._target = target

    @property
    def target(self):
        return self.asg[self._target['target']]

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
        return [TemplateTypeSpecifiersProxy(self.asg, self.node, template) for template in self.asg._template_edges[self.node]] #TODO

    def _remove(self):
        super(ClassTemplateSpecialization, self)._remove()
        self._templates_edges.pop(self.node)

def get_as_held_type(self):
    if hasattr(self, '_as_held_type'):
        return self._as_held_type
    else:
        return False

def set_as_held_type(self, as_held_type):
    self.asg._nodes[self.node]['_as_held_type'] = as_held_type

def del_as_held_type(self):
    self.asg._nodes[self.node].pop('_as_held_type', False)

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
        return '-' in self.node

    @property
    def is_empty(self):
        return len(self.declarations(True)) == 0

    def declarations(self, nested=False):
        declarations = [self.asg[node] for node in self.asg._syntax_edges[self.node]]
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

    def _remove(self):
        for dcl in self.declarations():
            if dcl.node in self.asg:
                dcl._remove()
        super(NamespaceProxy, self)._remove()
        self.asg._syntax_edges.pop(self.node)

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
        directories = set([node.parent.node for node in files])
        while not len(directories) == 1:
            parents = set()
            for directory in directories:
                parent = self[directory].parent.node
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
                return [node for node in [self[node] for node in self._nodes.keys()] if isinstance(node, metaclass) and re.match(pattern, node.node)]

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

    def variables(self, pattern=None, free=None):
        if free is None:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(VariableProxy)
            metaclass = _MetaClass
            return [node for node in self.nodes(pattern, metaclass=metaclass) if not isinstance(node.parent, FunctionProxy)]
        elif free:
            return [node for node in self.variables(free=None) if not isinstance(node, FieldProxy)]
        else:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(FieldProxy)
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
            if not node.node in black:
                black.add(node.node)
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

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if not node in self._nodes:
            raise KeyError('\'' + node + '\' parameter')
        else:
            return self._nodes[node]["proxy"](self, node)

    def __delitem__(self, node):
        self[node]._remove()

__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(NodeProxy)]
__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(EdgeProxy)]
