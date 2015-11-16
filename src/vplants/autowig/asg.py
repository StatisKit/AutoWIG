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

from .sloc_count import sloc_count
sloc_count.plugin = 'basic'
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
        if isinstance(other, NodeProxy):
            return self.asg == other.asg and self.node == other.node
        elif isinstance(other, basestring):
            return self.node == other
        else:
            return False

    @property
    def asg(self):
        return self._asg

    @property
    def node(self):
        return self._node

    @property
    def hash(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self.node)).replace('-', '')

    def __repr__(self):
        return self.node

    def __dir__(self):
        return sorted([key for key in self.asg._nodes[self.node].keys() if not key.startswith('_')])

    def __getattr__(self, attr):
        try:
            return self.asg._nodes[self.node][attr]
        except KeyError:
            raise #AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')
        except:
            raise

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

    def relativename(self, directory):
        relativename = './'
        dirancestors = [ancestor.globalname for ancestor in self.asg[directory].ancestors] + [self.asg[directory].globalname]
        selfancestors = [ancestor.globalname for ancestor in self.ancestors] + [self.globalname]
        if len(dirancestors) > len(selfancestors):
            relativename = '../'*(len(dirancestors)-len(selfancestors))
            dirancestors = dirancestors[:-(len(dirancestors)-len(selfancestors))]
        index = -1
        while len(dirancestors)+index > 0:
            if dirancestors[index] == selfancestors[index]:
                break
            else:
                relativename += '../'
                index -= 1
        return relativename + selfancestors[-1][len(selfancestors[index]):]

    @property
    def ancestors(self):
        ancestors = [self.parent]
        while not ancestors[-1].globalname == '/':
            ancestors.append(ancestors[-1].parent)
        return list(reversed(ancestors))

    @property
    def parent(self):
        parent = os.sep.join(self.globalname.split(os.sep)[:-2]) + os.sep
        if parent == '':
            parent = os.sep
        return self.asg[parent]

    #@property
    #def depth(self):
    #    if self.globalname == os.sep:
    #        return 0
    #    else:
    #        return self.parent.depth+1

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

    @property
    def directories(self):
        return [d for d in [self.asg[d] for d in self.asg._syntax_edges[self.node]] if isinstance(d, DirectoryProxy)]

    @property
    def files(self):
        return [f for f in [self.asg[f] for f in self.asg._syntax_edges[self.node]] if isinstance(f, FileProxy)]

    def walkdirs(self, pattern=None):
        if pattern is None:
            directories = self.directories
        else:
            directories = [d for d in self.directories if fnmatch(d.globalname, pattern)]
        return directories + list(itertools.chain(*[d.walkdirs(pattern=pattern) for d in self.directories]))

    def walkfiles(self, pattern=None):
        if pattern is None:
            files = self.files
        else:
            files =  [f for f in self.files if fnmatch(f.globalname, pattern)]
        return files + list(itertools.chain(*[d.walkfiles(pattern=pattern) for d in self.directories]))

def get_as_include(self):
    if hasattr(self, '_as_include'):
        return self._as_include
    else:
        return False

def set_as_include(self, as_include):
    self.asg._nodes[self.node]['_as_include'] = as_include

def del_as_include(self):
    self.asg._nodes[self.node].pop('_as_include', False)

DirectoryProxy.as_include = property(get_as_include, set_as_include, del_as_include, doc = """
        """)
del get_as_include, set_as_include, del_as_include

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
    def prefix(self):
        return self.localname[:self.localname.rfind('.')]

    @property
    def suffix(self):
        index = self.localname.rfind('.')
        if index > 0:
            return self.localname[index:]
        else:
            return ''

    @property
    def sloc(self):
        return sloc_count(self.content, language=self.language)

    def touch(self):
        parent = self.parent
        if not parent.on_disk:
            parent.makedirs()
        filehandler = open(self.globalname, 'w')
        filehandler.close()
        self.asg._nodes[self.node]['on_disk'] = True

    def write(self, database=None, force=False):
        parent = self.parent
        if not parent.on_disk:
            parent.makedirs()
        content = self.content
        self.content = content
        with open(self.globalname, 'w') as filehandler:
            filehandler.write(content)
            filehandler.close()
            self.asg._nodes[self.node]['on_disk'] = True

    def remove(self, force=False):
        os.remove(self.globalname)
        self.asg._nodes[self.node]['on_disk'] = False

    @property
    def is_empty(self):
        return self.content == ""

    def __repr__(self):
        return self.node

    def md5(self):
        return hashlib.md5(str(self)).hexdigest()

    @property
    def ancestors(self):
        ancestors = [self.parent]
        while not ancestors[-1].globalname == '/':
            ancestors.append(ancestors[-1].parent)
        return list(reversed(ancestors))

    @property
    def parent(self):
        return self.asg[os.sep.join(self.globalname.split(os.sep)[:-1]) + os.sep]

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
    self.asg._nodes[self.node].pop('_content', False)

FileProxy.content = property(get_content, set_content, del_content)
del get_content, set_content, del_content

class HeaderProxy(FileProxy):

    @property
    def include(self):
        if self.node in self.asg._include_edges:
            return self.asg[self.asg._include_edges[self.node]]

    @property
    def depth(self):
        if not hasattr(self, '_depth'):
            include = self.include
            if include is None:
                self.asg._nodes[self.node]['_depth'] = 0
            else:
                self.asg._nodes[self.node]['_depth'] = include.depth+1
        return self._depth

    @property
    def path(self):
        if not self.is_independent:
            raise ValueError
        incpath = self.localname
        parent = self.parent
        while not parent.localname == '/' and not parent.as_include:
            incpath = parent.localname + incpath
            parent = parent.parent
        if parent.localname == '/':
            return '/' + incpath
        else:
            return incpath

def get_is_primary(self):
    if hasattr(self, '_is_primary'):
        return self._is_primary
    else:
        return False

def set_is_primary(self, is_primary):
    self.asg._nodes[self.node]['_is_primary'] = is_primary

def del_is_primary(self):
    self.asg._nodes[self.node].pop('_is_primary', None)

HeaderProxy.is_primary = property(get_is_primary, set_is_primary, del_is_primary)
del get_is_primary, set_is_primary, del_is_primary

def get_is_independent(self):
    if hasattr(self, '_is_independent'):
        return self._is_independent
    else:
        return self.is_primary

def set_is_independent(self, is_independent):
    self.asg._nodes[self.node]['_is_independent'] = is_independent

def del_is_independent(self):
    self.asg._nodes[self.node].pop('_is_independent', None)

HeaderProxy.is_independent = property(get_is_independent, set_is_independent, del_is_independent)
del get_is_independent, set_is_independent, del_is_independent

class CodeNodeProxy(NodeProxy):

    @property
    def header(self):
        if not hasattr(self, '_header'):
            return self.parent.header
        else:
            return self.asg[self._header]

    @property
    def ancestors(self):
        ancestors = [self.parent]
        while not ancestors[-1].globalname == '::':
            ancestors.append(ancestors[-1].parent)
        return list(reversed(ancestors))

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

    def __init__(self, asg, target, specifiers):
        self._asg = asg
        self._target = target
        self._specifiers = specifiers

    @property
    def asg(self):
        return self._asg

    @property
    def target(self):
        return self.asg[self._target]

    @property
    def specifiers(self):
        return self._specifiers

    @property
    def globalname(self):
        return self.target.globalname + self.specifiers

    @property
    def localname(self):
        return self.target.localname + self.specifiers

    @property
    def is_const(self):
        if self.specifiers.endswith('&&'):
            return self.specifiers.endswith('const &&')
        elif self.specifiers.endswith('&'):
            return self.specifiers.endswith('const &')
        else:
            return self.specifiers.endswith('const')

    @property
    def is_reference(self):
        return self.specifiers.endswith('&') or self.specifiers.endswith('& const')

    @property
    def is_rvalue_reference(self):
        return self.specifiers.endswith('&&') or self.specifiers.endswith('&& const')


    @property
    def is_lvalue_reference(self):
        return self.is_reference and not self.is_rvalue_reference

    @property
    def is_pointer(self):
        if self.is_const:
            return self.specifiers.endswith('* const')
        else:
            return self.specifiers.endswith('*')

    @property
    def nested(self):
        specifiers = str(self.specifiers)
        if self.is_const:
            specifiers = specifiers[:-6]
        if self.is_pointer or self.is_reference:
            specifiers = specifiers[:-2]
        return TypeSpecifiersProxy(self.asg, self.target, specifiers)

    def __str__(self):
        return self.globalname

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

class TypedefProxy(DeclarationProxy):
    """
    """

    @property
    def type(self):
        return TypeSpecifiersProxy(self.asg, **self.asg._type_edges[self.node])

class VariableProxy(DeclarationProxy):
    """
    """

    @property
    def type(self):
        return TypeSpecifiersProxy(self.asg, **self.asg._type_edges[self.node])

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

class ParameterProxy(EdgeProxy):
    """
    """

    def __init__(self, asg, source, index):
        self._asg = asg
        self._source = source
        self._index = index

    @property
    def asg(self):
        return self._asg

    @property
    def source(self):
        return self[self._source]

    @property
    def index(self):
        return self._index

    @property
    def localname(self):
        return self.asg._parameter_edges[self._source][self.index]['name']

    @property
    def globalname(self):
        return self.source.globalname + '::' + self.localname

    @property
    def hash(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self.globalname + '::' + str(self.index))).replace('-', '')

    @property
    def type(self):
        kwargs = self.asg._parameter_edges[self._source][self.index]
        return TypeSpecifiersProxy(self.asg, kwargs['target'], kwargs['specifiers'])

    def rename(self, name=None):
        if name is None:
            self.asg._parameter_edges[self._source][self._index]['name'] = 'parm_' + str(self.index)
        else:
            self.asg._parameter_edges[self._source][self._index]['name'] = name

class FunctionProxy(DeclarationProxy):
    """
    """

    @property
    def result_type(self):
        return TypeSpecifiersProxy(self.asg, **self.asg._type_edges[self.node])

    @property
    def nb_parameters(self):
        return len(self.asg._parameter_edges[self.node])

    @property
    def parameters(self):
        return [ParameterProxy(self.asg, self.node, index) for index in range(self.nb_parameters)]

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

def get_call_policy(self):
    if hasattr(self, '_call_policy'):
        return self._call_policy
    else:
        result_type = self.result_type
        if result_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif result_type.is_reference:
            if result_type.is_const or isinstance(result_type.target, (FundamentalTypeProxy, EnumProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'

def set_call_policy(self, call_policy):
    self.asg._nodes[self.node].pop('_call_policy', call_policy)

def del_call_policy(self):
    self.asg._nodes[self.node].pop('_call_policy', None)

FunctionProxy.call_policy = property(get_call_policy, set_call_policy, del_call_policy)
del get_call_policy, set_call_policy, del_call_policy

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

def get_call_policy(self):
    if hasattr(self, '_call_policy'):
        return self._call_policy
    else:
        result_type = self.result_type
        if result_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif result_type.is_reference:
            if result_type.is_const or isinstance(result_type.target, (FundamentalTypeProxy, EnumProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_internal_reference<>()'

def set_call_policy(self, call_policy):
    self.asg._nodes[self.node].pop('_call_policy', call_policy)

def del_call_policy(self):
    self.asg._nodes[self.node].pop('_call_policy', None)

MethodProxy.call_policy = property(get_call_policy, set_call_policy, del_call_policy)
del get_call_policy, set_call_policy, del_call_policy

#class ConversionProxy(DeclarationProxy):
#    """
#    """
#
#    @property
#    def parent(self):
#        parent = remove_templates(self.globalname)
#        parent = parent[:parent.rindex(':')-1]
#        if parent == '':
#            return self.asg['::']
#        else:
#            for decorator in ['class', 'struct', 'union']:
#                decorator += ' ' + parent
#                if decorator in self.asg._nodes:
#                    parent = self.asg[decorator]
#                    break
#            if not isinstance(parent, NodeProxy):
#                if not parent in self.asg._nodes:
#                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
#                parent = self.asg[parent]
#            return parent
#
#    @property
#    def type(self):
#        return TypeSpecifiersProxy(self.asg, **self.asg._type_edges[self.node])

class ConstructorProxy(DeclarationProxy):
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

    @property
    def nb_parameters(self):
        return len(self.asg._parameter_edges[self.node])

    @property
    def parameters(self):
        return [ParameterProxy(self.asg, self.node, index) for index in range(self.nb_parameters)]

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
        already = set()
        for base in self.asg._base_edges[self.node]:
            if not base['base'] in already:
                already.add(base['base'])
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

    def declarations(self, pattern=None, metaclass=None, inherited=False):
        if metaclass is None:
            if pattern is None:
                declarations = [self.asg[node] for node in self.asg._syntax_edges[self.node]]
            else:
                declarations = [self.asg[node] for node in self.asg._syntax_edges[self.node] if re.match(pattern, node)]
        else:
            declarations = [declaration for declaration in self.declarations(pattern=pattern, metaclass=None, inherited=False) if isinstance(declaration, metaclass)]
        if not inherited:
            return declarations
        else:
            for base in self.bases(True):
                if isinstance(base, TypedefProxy):
                    basedeclarations = [basedeclaration for basedeclaration in base.type.target.declarations(pattern=pattern, metaclass=metaclass, inherited=False) if not basedeclaration.access == 'private']
                else:
                    basedeclarations = [basedeclaration for basedeclaration in base.declarations(pattern=pattern, metaclass=metaclass, inherited=False) if not basedeclaration.access == 'private']
                if base.access == 'protected':
                    for basedeclaration in basedeclarations:
                        if basedeclaration.access == 'public':
                            basedeclaration.access = 'protected'
                elif base.access == 'private':
                   for basedeclaration in basedeclarations:
                        basedeclaration.access = 'private'
                declarations += basedeclarations
            return declarations

    def enums(self, pattern=None, inherited=False):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(EnumProxy)
        metaclass = _MetaClass
        return self.declarations(pattern=pattern, metaclass=metaclass, inherited=inherited)

    def enum_constants(self, pattern=None, inherited=False):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(EnumConstantProxy)
        metaclass = _MetaClass
        return self.declarations(pattern=pattern, metaclass=metaclass, inherited=inherited)

    def typedefs(self, pattern=None, inherited=False):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(TypedefProxy)
        metaclass = _MetaClass
        return self.declarations(pattern=pattern, metaclass=metaclass, inherited=inherited)

    def fields(self, pattern=None, inherited=False):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(FieldProxy)
        metaclass = _MetaClass
        return self.declarations(pattern=pattern, metaclass=metaclass, inherited=inherited)

    def methods(self, pattern=None, inherited=False):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(MethodProxy)
        metaclass = _MetaClass
        return self.declarations(pattern=pattern, metaclass=metaclass, inherited=inherited)

    def classes(self, pattern=None, inherited=False, recursive=False, templated=None, specialized=None):
        if recursive:
            classes = self.classes(inherited=inherited, recursive=False, templated=templated, specialized=specialized)
            for cls in classes:
                if isinstance(cls, ClassProxy):
                    classes += cls.classes(inherited=inherited, recursive=True, templated=templated, specialized=specialized)
            return classes
        else:
            if templated is None:
                if specialized is None:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, (ClassProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy))]
                elif specialized:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy))]
                else:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, (ClassProxy, ClassTemplateProxy)) and not isinstance(cls, ClassTemplateSpecializationProxy)]
            elif templated:
                if specialized is None:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, (ClassTemplateProxy, ClassTemplatePartialSpecializationProxy))]
                elif specialized:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, ClassTemplatePartialSpecializationProxy)]
                else:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, ClassTemplateProxy)]
            else:
                if specialized is None:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, ClassProxy)]
                elif specialized:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, ClassTemplateSpecializationProxy)]
                else:
                    return [cls for cls in self.declarations(inherited=inherited) if isinstance(cls, ClassProxy) and not isinstance(cls, ClassTemplateSpecializationProxy)]


    @property
    def constructors(self):
        return [constructor for constructor in self.declarations(inherited=False) if isinstance(constructor, ConstructorProxy)]

    @property
    def destructor(self):
        try:
            return [destructor for destructor in self.declarations(inherited=False) if isinstance(destructor, DestructorProxy)].pop()
        except:
            return None

def get_is_copyable(self):
    return self._is_copyable

def set_is_copyable(self, copyable):
    self.asg._nodes[self.node]['_is_copyable'] = copyable

ClassProxy.is_copyable = property(get_is_copyable, set_is_copyable)
del get_is_copyable, set_is_copyable

#class TemplateTypeSpecifiersProxy(TypeSpecifiersProxy):
#
#    def __init__(self, asg, source, target):
#        super(TemplateTypeSpecifiersProxy, self).__init__(asg, source)
#        self._target = target
#
#    @property
#    def target(self):
#        return self.asg[self._target['target']]
#
#    @property
#    def specifiers(self):
#        return self._target["specifiers"]


class ClassTemplateSpecializationProxy(ClassProxy):
    """
    """

    @property
    def header(self):
        if not hasattr(self, '_header'):
            return self.specialize.header
        else:
            return self.asg[self._header]

    @property
    def specialize(self):
        specialize = remove_templates(self.node)
        if specialize.startswith('class '):
            pass
        elif specialize.startswith('struct '):
            specialize = 'class ' + specialize[7:]
        elif specialize.startswith('union '):
            specialize = 'class ' + specialize[6:]
        else:
            specialize = 'class ' + specialize
        return self.asg[specialize]

    @property
    def templates(self):
        return [TypeSpecifiersProxy(self.asg, **template) for template in self.asg._template_edges[self.node]] #TODO

class ClassTemplatePartialSpecializationProxy(DeclarationProxy):
    """
    """


    @property
    def header(self):
        if not hasattr(self, '_header'):
            return self.specialize.header
        else:
            return self.asg[self._header]

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
    def specialize(self):
        specialize = remove_templates(self.node)
        if specialize.startswith('class '):
            pass
        elif specialize.startswith('struct '):
            specialize = 'class ' + specialize[7:]
        elif specialize.startswith('union '):
            specialize = 'class ' + specialize[6:]
        else:
            specialize = 'class ' + specialize
        return self.asg[specialize]

class ClassTemplateProxy(DeclarationProxy):
    """
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

    def specializations(self, partial=None):
        if partial is None:
            return [self.asg[spc] for spc in self.asg._specialization_edges[self.node]]
        elif partial:
            return [spec for spec in self.specializations(None) if isinstance(spec, ClassTemplatePartialSpecializationProxy)]
        else:
            return [spec for spec in self.specializations(None) if isinstance(spec, ClassTemplateSpecializationProxy)]

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

class AbstractSemanticGraph(object):

    def __init__(self, *args, **kwargs):
        self._nodes = dict()
        self._syntax_edges = dict()
        self._base_edges = dict()
        self._type_edges = dict()
        self._parameter_edges = dict()
        self._template_edges = dict()
        self._specialization_edges = dict()
        self._include_edges = dict()

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

    def files(self, pattern=None, header=None):
        if header is None:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(FileProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)
        elif header:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(HeaderProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)
        else:
            return [f for f in self.files(pattern=pattern, header=None) if not isinstance(f, HeaderProxy)]

    def declarations(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(CodeNodeProxy)
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

    def classes(self, pattern=None, specialized=None, templated=False, free=None):
        if free is None:
            if templated is None:
                if specialized is None:
                    class _MetaClass(object):
                        __metaclass__ = ABCMeta
                    _MetaClass.register(ClassProxy)
                    _MetaClass.register(ClassTemplatePartialSpecializationProxy)
                    _MetaClass.register(ClassTemplateProxy)
                    metaclass = _MetaClass
                    return self.nodes(pattern, metaclass=metaclass)
                elif specialized:
                    class _MetaClass(object):
                        __metaclass__ = ABCMeta
                    _MetaClass.register(ClassTemplateSpecializationProxy)
                    _MetaClass.register(ClassTemplatePartialSpecializationProxy)
                    metaclass = _MetaClass
                    return self.nodes(pattern, metaclass=metaclass)
                else:
                    class _MetaClass(object):
                        __metaclass__ = ABCMeta
                    _MetaClass.register(ClassProxy)
                    _MetaClass.register(ClassTemplateProxy)
                    return [node for node in self.classes(specialized=None) if not isinstance(node, ClassTemplateSpecializationProxy)]
            elif templated:
                if specialized is None:
                    class _MetaClass(object):
                        __metaclass__ = ABCMeta
                    _MetaClass.register(ClassTemplateProxy)
                    _MetaClass.register(ClassTemplatePartialSpecializationProxy)
                    metaclass = _MetaClass
                    return self.nodes(pattern, metaclass=metaclass)
                elif specialized:
                    class _MetaClass(object):
                        __metaclass__ = ABCMeta
                    _MetaClass.register(ClassTemplateSpecializationProxy)
                    metaclass = _MetaClass
                    return self.nodes(pattern, metaclass=metaclass)
                else:
                    class _MetaClass(object):
                        __metaclass__ = ABCMeta
                    _MetaClass.register(ClassTemplateProxy)
                    metaclass = _MetaClass
                    return self.nodes(pattern, metaclass=metaclass)
            else:
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
        elif free:
            return [cls for cls in self.classes(specialized=specialized, templated=templated, free=None) if isinstance(cls.parent, NamespaceProxy)]
        else:
            return [cls for cls in self.classes(specialized=specialized, templated=templated, free=None) if isinstance(cls.parent, ClassProxy)]

    def template_classes(self, pattern=None, specialized=None):
        if specialized is None:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(ClassTemplatePartialSpecializationProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)
        elif specialized:
            return [node for node in self.classes(specialized=None) if not isinstance(node, ClassTemplateProxy)]
        else:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(ClassTemplateProxy)
            metaclass = _MetaClass
            return self.nodes(pattern, metaclass=metaclass)

    def namespaces(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(NamespaceProxy)
        metaclass = _MetaClass
        return self.nodes(pattern, metaclass=metaclass)

    def include_path(self, header, absolute=False):
        if not header.is_independent:
            include = header.include
            while include is not None and not include.is_indepentent:
                include = include.include
            if include is None:
                raise ValueError('\'header\' parameter is not independent and has no include parent file independent')
            header = include
        if absolute:
            return header.globalname
        else:
            include = header.localname
            parent = header.parent
            while not parent.localname == '/' and not parent.as_include:
                include = parent.localname + include
                parent = parent.parent
            if parent.localname == '/':
                return '/' + include
            else:
                return include

    def headers(self, *nodes):
        white = []
        for node in nodes:
            if isinstance(node, basestring):
                white.extend(self.nodes(node))
            else:
                white.append(node)
        headers = []
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
                elif isinstance(node, ClassTemplatePartialSpecializationProxy):
                    # TODO templates !
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
                elif isinstance(node, ClassTemplateProxy):
                    pass
                elif isinstance(node, NamespaceProxy):
                    white.extend(node.declarations())
                elif isinstance(node, TypedefProxy):
                    white.append(node.type.target)
                else:
                    raise NotImplementedError(node.__class__.__name__)
                header = node.header
                while not header is None and not header.is_independent:
                    header = header.include
                if not header is None:
                    headers.append(header)
        headers = sorted(headers, key = lambda header: header.depth)
        _headers = set()
        for header in headers:
            include = header.include
            while not include is None and not include.globalname in _headers:
                include = include.include
            if include is None:
                _headers.add(header.globalname)
        headers = [self[header] for header in _headers]
        return sorted(headers, key = lambda header: header.depth)

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if isinstance(node, NodeProxy):
            node = node.globalname
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if node in self._nodes:
            return self._nodes[node]["proxy"](self, node)
        else:
            if node == '.':
                return self.add_directory('.')
            elif node.startswith('.'):
                parent = self.add_directory('.')
                for node in node.split('../'):
                    directory = self[parent.globalname + node.replace('./', '')]
                    parent = directory.parent
                return directory
            else:
                node = path(node)
                if node.exists():
                    if node.isfile():
                        return self.add_file(str(node))
                    elif node.isdir():
                        return self.add_directory(str(node))
                    else:
                        raise KeyError('\'' + node + '\' parameter')
                else:
                    raise KeyError('\'' + node + '\' parameter')

__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(NodeProxy)]
__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(EdgeProxy)]
