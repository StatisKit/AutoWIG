"""
"""

import uuid
import itertools
import os
import re
from path import Path
from .plugin import PluginManager

from .tools import subclasses

__all__ = ['AbstractSemanticGraph']


visitor = PluginManager('autowig.visitor', brief="",
        details="""""")

def all_visitor(node):
    return True

class NodeProxy(object):
    """Abstract semantic graph node proxy

    .. seealso:: :class:`AbstractSemanticGraph`
    """

    _clean_default = True

    def __init__(self, asg, node):
        self._asg = asg
        self._node = node

    def __eq__(self, other):
        if isinstance(other, NodeProxy):
            return self._asg == other._asg and self._node == other._node
        elif isinstance(other, basestring):
            return self._node == other
        else:
            return False

    def __repr__(self):
        return self.globalname

    @property
    def globalname(self):
        """Node global name

        The node name is not neccessarily unique in the abstract semantic graph (e.g. overload functions)

        .. seealso:: :attr:`node`
        """
        return self._node

    @property
    def ancestors(self):
        """Node ancestors
        """
        parent = self.parent
        if parent is None:
            return []
        else:
            return parent.ancestors + [parent]

    @property
    def hash(self):
        """Node hash

        The node hash is usefull for having a valid an unique Python or C/C++ identifiers

        .. seealso:: :attr:`node`
        """
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self._node)).replace('-', '')

    def __hash__(self):
        return int(uuid.uuid5(uuid.NAMESPACE_X500, self._node).hex, 16)

    def __dir__(self):
        return sorted([key for key in self._asg._nodes[self._node].keys()] + [key for key in dir(self.__class__)])

    def __getattr__(self, attr):
        if attr not in dir(self):
            raise AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')
        else:
            return self._asg._nodes[self._node][attr]

    @property
    def clean(self):
        """Is this node clean"""
        if not hasattr(self, '_clean'):
            return self._clean_default
        else:
            return self._clean

    @clean.setter
    def clean(self, clean):
        if not isinstance(clean, bool):
            raise TypeError('\'clean\' parameter')
        self._asg._nodes[self._node]['_clean'] = clean

    @clean.deleter
    def clean(self):
        self._asg._nodes[self._node].pop('_clean', self._clean_default)

class EdgeProxy(object):
    """Abstract semantic graph node proxy

    .. seealso:: :class:`AbstractSemanticGraph`
    """

    def __init__(self, asg, source, target):
        self._asg = asg
        self._source = source
        self._target = target

class FilesystemProxy(NodeProxy):
    """Abstract semantic graph node proxy for a filesystem component
    """

    @property
    def on_disk(self):
        """Is the filesystem component on disk"""
        return os.path.exists(self.globalname)

class DirectoryProxy(FilesystemProxy):
    """Abstract semantic graph node proxy for a directory

    .. seealso:: :class:`FileProxy`
    """

    @property
    def localname(self):
        """Directory local name

        The directory local name is computed by removing the parent directory global name in the directory globalname

        .. seealso:: :attr:`globalname`
        """
        return self.globalname[self.globalname.rfind(os.sep, 0, -2)+1:]

    @property
    def parent(self):
        """Parent directory

        .. warning:: The parent directory is `None` only for the system root directory
        """
        if self._node == os.path.abspath(os.sep):
            return None
        elif self._node in ["/", "\"]:
            return None 
        else:
            return self._asg[self.globalname[:len(self.globalname)-len(self.localname)]]

    def relpath(self, location):
        """Compute the relative path from the directory to the given location

        :Parameter:
          `location` (:class:`FilesystemProxy`) - The given location.

        :Returns Type:
          str
        """
        if isinstance(location, basestring):
            try:
                location = self._asg[location]
            except:
                raise ValueError('\'location\' parameter')
        elif not isinstance(location, FilesystemProxy):
            raise TypeError('\'location\' parameter')
        ancestors = self.ancestors, location.ancestors
        i = 0
        while i < min(len(ancestors[0]), len(ancestors[1])) and ancestors[0][i] == ancestors[1][i]:
            i += 1
        return './' + ('..' + os.sep) * (len(ancestors[0]) - i - 1) + os.sep.join(ancestors[1][i+1:])

    def makedirs(self):
        """Write the directory and its ancestral directories into the filesystem"""
        if not self.on_disk:
            os.makedirs(self.globalname)

    @property
    def is_searchpath(self):
        """Is this directory a search path

        .. note:: A compilation dependent property

        This property is setted at each front-end execution.
        Any application of a front-end reset this property since search paths can differ from one compilation to another.
        .. seealso:: :func:`autowig.parser.preprocessing`
        """
        if hasattr(self, '_is_searchpath'):
            return self._is_searchpath
        else:
            return False

    @is_searchpath.setter
    def is_searchpath(self, is_searchpath):
        self._asg._nodes[self._node]['_is_searchpath'] = is_searchpath

    @is_searchpath.deleter
    def is_searchpath(self):
        self._asg._nodes[self._node].pop('_is_searchpath', False)

class FileProxy(FilesystemProxy):
    """Abstract semantic graph node proxy for a filename

    .. seealso:: :class:`DirectoryProxy`
    """

    @property
    def parent(self):
        """Parent directory"""
        return self._asg[self.globalname[:self.globalname.rfind(os.sep)+1]]

    @property
    def localname(self):
        """File local name

        The file local name is computed by removing the parent directory global name in the file global name

        .. seealso:: :attr:`globalname`
        """
        return self.globalname[self.globalname.rfind(os.sep)+1:]

    @property
    def prefix(self):
        """File prefix

        The file prefix is the path of the local name posterior to the `.` character

        .. seealso:: :attr:`localname`
        """
        return self.localname[:self.localname.rfind('.')]

    @property
    def suffix(self):
        """File prefix

        The file prefix is the path of the local name anterior to the `.` character

        .. seealso:: :attr:`localname`
        """
        index = self.localname.rfind('.')
        if index > 0:
            return self.localname[index:]
        else:
            return ''

    def write(self):
        """Write the file and its ancestral directories into the filesystem

        :Optional Parameters:
         - `database` ({str:str}) - A database interfaced as a dictionnary.
                                    A database key correspond to a file global name.
                                    A database value correspond to a file md5.
                                    If the database is given, the file is written to the disk
                                    only if its current md5 is the same as the one stored in the database.
                                    If a file is written to the disk, its md5 is updated.
         - `force` (bool) - If set to true, files are written to disk whatever the md5 stored in the database.
                            Yet, if its current md5 is the same as the one stored in the database,
                            a warning is displayed.
        """
        if not self.on_disk:
            parent = self.parent
            if not parent.on_disk:
                parent.makedirs()
        content = self.content
        if content:
            with open(self.globalname, 'w') as filehandler:
                filehandler.write(self.content)

    def remove(self):
        if self.on_disk:
            os.remove(self.globalname)

    @property
    def is_empty(self):
        """Is the file empty"""
        return self.content == ""

def get_content(self):
    if hasattr(self, '_content'):
        return self._content
    elif self.on_disk:
        with open(self.globalname, 'r') as filehandler:
            content = filehandler.read()
        return content
    else:
        return ""

def set_content(self, content):
    self._asg._nodes[self._node]['_content'] = content

def del_content(self):
    self._asg._nodes[self._node].pop('_content', "")

FileProxy.content = property(get_content, set_content, del_content, doc="""File content

.. warning:: The content can be different of the content of the real file content on the disk.

.. seealso:: :func:`write`
""")
del get_content, set_content, del_content

class HeaderProxy(FileProxy):
    """Abstract semantic graph node proxy for a header file"""

    @property
    def _clean_default(self):
        return self.is_external_dependency

    @property
    def include(self):
        """Header including this header

        .. warning:: If no header include this header, `None` is returned
        """
        if self._node in self._asg._include_edges:
            return self._asg[self._asg._include_edges[self._node]]

    @property
    def depth(self):
        """Depth of the header

        The depth of a header is `0` if it is not included by any header or the depth of the including header plus `1`.

        .. seealso:: :attr:`include`
        """
        if not hasattr(self, '_depth'):
            include = self.include
            if include is None:
                self._asg._nodes[self._node]['_depth'] = 0
            else:
                self._asg._nodes[self._node]['_depth'] = include.depth + 1
        return self._depth

    @property
    def searchpath(self):
        """Path to file relatively to search path directories"""
        incpath = self.localname
        parent = self.parent
        while parent is not None and not parent.is_searchpath:
            incpath = parent.localname + incpath
            parent = parent.parent
        return incpath

    @property
    def is_external_dependency(self):
        if hasattr(self, '_is_external_dependency'):
            return self._is_external_dependency
        else:
            return True

    @is_external_dependency.setter
    def is_external_dependency(self, is_external_dependency):
        self._asg._nodes[self._node]['_is_external_dependency'] = is_external_dependency

    @is_external_dependency.deleter
    def is_external_dependency(self):
        self._asg._nodes[self._node].pop('_is_external_dependency', True)

def get_language(self):
    return self._language

def set_language(self, language):
    if not isinstance(language, basestring):
        raise TypeError('\'language\' parameter')
    language = language.lower()
    if language not in ['c', 'c++']:
        raise ValueError('\'language\' parameter')
    self._asg._nodes[self._node]['_language'] = language

HeaderProxy.language = property(get_language, set_language, doc="""Language of the header file

Possible languages for a header file is either `c` or `c++`
""")
del get_language, set_language

def get_is_self_contained(self):
    if hasattr(self, '_is_self_contained'):
        return self._is_self_contained
    else:
        return False

def set_is_self_contained(self, is_self_contained):
    self._asg._nodes[self._node]['_is_self_contained'] = is_self_contained

def del_is_self_contained(self):
    self._asg._nodes[self._node].pop('_is_self_contained', None)

HeaderProxy.is_self_contained = property(get_is_self_contained, set_is_self_contained, del_is_self_contained, doc="""Is this a stand-alone header

A header is considered as stand-alone if it can be included in a source file without producing any errors.
By default, only header given as input of an AutoWIG front-end are considered as stand-alone.

.. seealso:: :func:`autowig.parser.postprocessing`""")
del get_is_self_contained, set_is_self_contained, del_is_self_contained

class DeclarationProxy(NodeProxy):
    """Abstract semantic graph node proxy for a declaration
    """

    @property
    def _clean_default(self):
        header = self.header
        return header is None or header.clean

    @property
    def header(self):
        """File in which the declaration has been written

        .. warning:: Some declarations are not really declared in headers.
                     In particular:

                       * The global scope (`::`) or fundamental types are not declared in any headers, therefore the result is `None`.
                       * A class template specialization can be instantiated or declared.
                         In the former case, the header in which the template class has been declared is returned.
                         In the latter case, the header in which the template class specialization has been declared is returned.

        .. seealso:: :class:`NamespaceProxy`, :class:`FundamentalTypeProxy` and :class:`ClassTemplateSpecializationProxy`.
        """
        if not hasattr(self, '_header'):
            if isinstance(self, ClassTemplateSpecializationProxy):
                return self.specialize.header
            else:
                return self.parent.header
        else:
            return self._asg[self._header]

    @property
    def globalname(self):
        if isinstance(self, (FunctionProxy, ConstructorProxy)):
            return re.sub('::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', '', self._node)
        else:
            return self._node

    @property
    def localname(self):
        localname = self.globalname
        if isinstance(self, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
            delimiter = 1
            current = -2
            while current > -len(localname):
                if localname[current] == '<':
                    delimiter -= 1
                    current -= 1
                elif localname[current] == '>':
                    delimiter += 1
                    current -= 1
                elif localname[current-2:current] == '::' and delimiter == 0:
                    break
                else:
                    current -= 1
            return localname[current:]
        else:
            return localname[localname.rindex(':')+1:]

    @property
    def access(self): 
        return getattr(self, '_access', "none")

    @access.setter
    def access(self, access):
        self._access = access

    @property
    def parent(self):
        if not hasattr(self, '_parent'):
            if not self._node == '::':
                parentname = self.globalname[:-len(self.localname)-2]
                if isinstance(self, EnumerationProxy):
                    if parentname.startswith('enum '):
                        parentname = parentname[len('enum '):]
                elif isinstance(self, (ClassProxy, ClassTemplatePartialSpecializationProxy)):
                    if parentname.startswith('class '):
                        parentname = parentname[len('class '):]
                    elif parentname.startswith('struct '):
                        parentname = parentname[len('struct '):]
                    elif parentname.startswith('union '):
                        parentname = parentname[len('union '):]
                elif isinstance(self, ClassTemplateProxy):
                    parentname = parentname[len('class '):]
                if parentname == '':
                    return self._asg['::']
                else:
                    parent = None
                    for keyword in self._pakwargs:
                        if keyword + parentname in self._asg:
                            parent =  self._asg[keyword + parentname]
                            if isinstance(parent, ClassProxy):
                                if not parent.is_complete:
                                    parent = None
                                else:
                                    break
                            else:
                                break
                    if isinstance(parent, TypedefProxy):
                        return parent.qualified_type.desugared_type.unqualified_type
                    else:
                        return parent
        else:
            return self._asg[self._parent]

    @parent.setter
    def parent(self, parent):
        if isinstance(parent, basestring):
            parent = self._asg[parent]
        if not isinstance(parent, DeclarationProxy):
            raise TypeError('\'parent\' parameter')
        self._asg._syntax_edges[self.parent._node].remove(self._node)
        self._asg._syntax_edges[parent._node].append(self._node)
        self._asg._nodes[self._node]['_parent'] = parent._node

    @parent.deleter
    def parent(self):
        self._asg._syntax_edges[self.parent._node].remove(self._node)
        self._asg._nodes[self._node].pop('_parent', None)
        self._asg._syntax_edges[self.parent._node].append(self._node)

    @property
    def comment(self):
        if hasattr(self, '_comment'):
            return self._comment
        else:
            return ""

class FundamentalTypeProxy(DeclarationProxy):
    """Abstract semantic graph node proxy for a fundamental type

    .. seealso:: `C++ fundamental types <http://en.cppreference.com/w/cpp/language/types>`
    """

    is_assignable = True

    @property
    def globalname(self):
        """Fundamental type global name

        For fundamental types, the global name is computed from its identifier minus the global scope operator (`::`)
        """
        return self._node.lstrip('::')

    @property
    def localname(self):
        """Fundamental type local name

        The fundamental type local name is the same as its global name

        .. seealso:: :attr:`globalname`
        """
        return self.globalname

    @property
    def parent(self):
        """Global scope"""
        return self._asg['::']

class CharacterFundamentalTypeProxy(FundamentalTypeProxy):
    """
    """
    
    pass

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

    _node = "::int"
    
class SignedShortIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::short int"

class SignedLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::long int"

class SignedLongLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    _node = "::long long int"

class UnsignedIntegerTypeProxy(FundamentalTypeProxy):
    """
    """
    
    _node = "::unsigned int"
class UnsignedShortIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned short int"

class UnsignedLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned long int"

class UnsignedLongLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    _node = "::unsigned long long int"

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

class ComplexFloatTypeProxy(ComplexTypeProxy):

    _node = "::_Complex float"

class ComplexDoubleTypeProxy(ComplexTypeProxy):

    _node = "::_Complex double"

class ComplexLongDoubleTypeProxy(ComplexTypeProxy):

    _node = "::_Complex long double"

class NullPtrTypeProxy(FundamentalTypeProxy):
    """
    """

    _node = "::nullptr_t"

class VoidTypeProxy(FundamentalTypeProxy):
    """
    """

    is_assignable = False

    _node = "::void"


class QualifiedTypeProxy(EdgeProxy):
    """Abstract semantic graph edge proxy for qualified type.

    A (possibly-)qualified type.

    For efficiency, we don't store CV-qualified types as nodes on their own:
    instead each reference to a type stores the qualifiers.
    This greatly reduces the number of nodes we need to allocate for
    types (for example we only need one for 'int', 'const int', 'volatile int', 'const volatile int', etc).

    As an added efficiency bonus, instead of making this a pair, we just store
    the two bits we care about in the low bits of the pointer.
    To handle the packing/unpacking, we make QualType be a simple generator
    class that acts like a smart pointer.
    A third bit indicates whether there are extended qualifiers present, in which 
    case the pointer points to a special structure.

    .. seealso::

        * `CV type qualifiers <http://en.cppreference.com/w/cpp/language/cv>`
        * `Pointer declaration <http://en.cppreference.com/w/cpp/language/pointer>`
        * `Reference declaration <http://en.cppreference.com/w/cpp/language/reference>`
    """

    def __init__(self, asg, source, target, qualifiers):
        self._asg = asg
        self._source = source
        self._target = target
        self._qualifiers = qualifiers

    def __repr__(self):
        return self.globalname

    @property
    def unqualified_type(self):
        """Unqualified type

        The unqualified type is the node without qualifiers and without aliases possibly masking some qualifiers
        """
        return self._asg[self._target]

    @property
    def globalname(self):
        """Qualified type global name

        The qualified type global name is computed using the target global name
        """
        return self.unqualified_type.globalname + ' ' + self.qualifiers

    @property
    def localname(self):
        """Qualified type local name

        The qualified type local name is computed using the target local name
        """
        return self.unqualified_type.localname + ' ' + self.qualifiers

    @property
    def desugared_type(self):
        desugared_type = self._asg[self._target]
        qualifiers = self.qualifiers
        while isinstance(desugared_type, TypedefProxy):
            desugared_type = desugared_type.qualified_type
            qualifiers = desugared_type.qualifiers + ' ' + qualifiers
        if isinstance(desugared_type, QualifiedTypeProxy):
            desugared_type = self._asg[desugared_type._target]
        return QualifiedTypeProxy(self._asg, self._source, desugared_type._node, qualifiers)

    @property
    def qualifiers(self):
        """Type qualifiers"""
        return self._qualifiers.strip()

    @property
    def is_qualified(self):
        """
        """
        return bool(self._qualifiers)

    @property
    def is_fundamental_type(self):
        """Is the unqualified type a fundamental type"""
        return isinstance(self.unqualified_type, FundamentalTypeProxy)

    @property
    def is_enumeration(self):
        """Is the unqualified type an enumeration type"""
        return isinstance(self.unqualified_type, EnumerationProxy)

    @property
    def is_class(self):
        """Is the unqualified type an enumeration type"""
        return isinstance(self.unqualified_type, ClassProxy)

    @property
    def is_pointer(self):
        """Is the qualified type a pointer"""
        return '*' in self.qualifiers

    @property
    def is_pointer_chain(self):
        """Is the qualified type a chain of pointers"""
        return self.qualifiers.count('*') > 1

    @property
    def is_reference(self):
        """Is the qualified type a reference"""
        return self.qualifiers.endswith('&') or self.qualifiers.endswith('& const')

    @property
    def is_rvalue_reference(self):
        """Is the qualified type a r-value reference"""
        return self.qualifiers.endswith('&&') or self.qualifiers.endswith('&& const')

    @property
    def is_lvalue_reference(self):
        """Is the qualified type an l-value reference"""
        return self.is_reference and not self.is_rvalue_reference

    @property
    def is_const(self):
        """Is the qualified type const qualified"""
        if self.qualifiers.endswith('&&'):
            return self.qualifiers.endswith('const &&') or self.qualifiers.endswith('const volatile &&')
        elif self.qualifiers.endswith('&'):
            return self.qualifiers.endswith('const &') or self.qualifiers.endswith('const volatile &')
        else:
            return self.qualifiers.endswith('const') or self.qualifiers.endswith('const volatile')

    @property
    def is_volatile(self):
        """Is the qualified type volatile qualified"""
        if self.qualifiers.endswith('&&'):
            return self.qualifiers.endswith('volatile &&') or self.qualifiers.endswith('volatile const &&')
        elif self.qualifiers.endswith('&'):
            return self.qualifiers.endswith('volatile &') or self.qualifiers.endswith('volatile const')
        else:
            return self.qualifiers.endswith('volatile') or self.qualifiers.endswith('volatile const')

class EnumeratorProxy(DeclarationProxy):
    """

    .. seealso:: `Enumerators <http://en.cppreference.com/w/cpp/language/enum>`
    """

    _pakwargs = ['enum ', 'class ', 'struct ', 'union ', '']

class EnumerationProxy(DeclarationProxy):
    """

    .. seealso:: `Enumerations <http://en.cppreference.com/w/cpp/language/enum>`
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def is_complete(self):
        return len(self._asg._syntax_edges[self._node]) > 0

    is_assignable = True

    @property
    def is_scoped(self):
        return self._is_scoped

    @is_scoped.setter
    def is_scoped(self, is_scoped):
        self._asg._nodes[self._node]['_is_scoped'] = is_scoped

    @property
    def enumerators(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

class TypedefProxy(DeclarationProxy):
    """

    .. seealso:: `Typedefs <http://en.cppreference.com/w/cpp/language/typedef>`
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def qualified_type(self):
        return QualifiedTypeProxy(self._asg, self._node, **self._asg._type_edges[self._node])

class VariableProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['', 'class ', 'struct ', 'union ']

    @property
    def qualified_type(self):
        return QualifiedTypeProxy(self._asg, self._node, **self._asg._type_edges[self._node])

class FieldProxy(VariableProxy):
    """
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def is_mutable(self):
        return self._is_mutable

    @property
    def is_bit_field(self):
        return self._is_bit_field

    @property
    def is_static(self):
        return self._is_static

class ParameterProxy(EdgeProxy):
    """
    """

    @property
    def qualified_type(self):
        return QualifiedTypeProxy(self._asg, 
                                  self._source,
                                  self._asg._parameter_edges[self._source][self._target]['target'],
                                  self._asg._parameter_edges[self._source][self._target]['qualifiers'])

    @property
    def localname(self):
        return self._asg._parameter_edges[self._source][self._target]['name']

    @localname.setter
    def localname(self, name):
        if not isinstance(name, basestring):
            raise TypeError('\'name\' parameter')
        self._asg._parameter_edges[self._source][self._target]['name'] = name

    @property
    def globalname(self):
        return self._asg[self._source].globalname + '::' + self.localname

    @property
    def hash(self):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, self.globalname + '::' + str(self._target))).replace('-', '')

    @property
    def index(self):
        return self._target

class FunctionProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['', 'class ', 'struct ', 'union ']

    @property
    def is_operator(self):
        return self.localname.startswith('operator')

    @property
    def return_type(self):
        return QualifiedTypeProxy(self._asg, self._node, **self._asg._type_edges[self._node])

    @property
    def nb_parameters(self):
        return len(self._asg._parameter_edges[self._node])

    @property
    def parameters(self):
        return [ParameterProxy(self._asg, self._node, index) for index in range(self.nb_parameters)]

    @property
    def is_overloaded(self):
        if not hasattr(self, '_is_overloaded'):
            return not len(self.overloads) == 1
        else:
            return self._is_overloaded

    @is_overloaded.setter
    def is_overloaded(self, is_overloaded):
        self._asg._nodes[self._node]["_is_overloaded"] = is_overloaded

    @is_overloaded.deleter
    def is_overloaded(self):
        self._asg._nodes[self._node].pop("_is_overloaded", False)

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
    def prototype(self):
        return self.return_type.desugared_type.globalname + ' ' + self.localname + '(' + \
        ', '.join(parameter.qualified_type.desugared_type.globalname for parameter in self.parameters) + ')'

class MethodProxy(FunctionProxy):
    """
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def is_static(self):
        return self._is_static

    @property
    def is_const(self):
        return self._is_const

    @property
    def is_volatile(self):
        return self._is_volatile

    @property
    def is_virtual(self):
        return self._is_virtual

    @property
    def is_pure(self):
        return self._is_pure

    @property
    def overrides(self):
        if self.is_virtual:
            methods = []
            for base in self.parent.bases(inherited = True):
                for method in base.methods():
                    if method.prototype == self.prototype:
                        methods.append(method)
            if len(methods) > 0:
                return methods

    @property
    def prototype(self):
        return 'static ' * self.is_static + self.return_type.desugared_type.globalname + ' ' + self.localname + '(' + \
        ', '.join(parameter.qualified_type.desugared_type.globalname for parameter in self.parameters) + ')' + ' const' * self.is_const + ' volatile' * self.is_volatile

class ConstructorProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def nb_parameters(self):
        return len(self._asg._parameter_edges[self._node])

    @property
    def parameters(self):
        return [ParameterProxy(self._asg, self._node, index) for index in range(self.nb_parameters)]

    @property
    def is_virtual(self):
        return self._is_virtual

    @property
    def prototype(self):
        return self.parent.localname + '(' + ', '.join(parameter.qualified_type.desugared_type.globalname for parameter in self.parameters) + ')'

    @property
    def is_copy_constructor(self):
        return self.nb_parameters == 1 and self.parameters[0].qualified_type.desugared_type.unqualified_type.globalname == self.parent.globalname
        
class DestructorProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def is_virtual(self):
        return self._is_virtual

class ClassProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/class>_`
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    @property
    def is_complete(self):
        return self._is_complete # or len(self.declarations()) > 0

    @property
    def is_abstract(self):
        return self._is_abstract

    @is_abstract.setter
    def is_abstract(self, is_abstract):
        self._asg._nodes[self._node]['_is_abstract'] = is_abstract

    @property
    def is_instantiable(self):
        if hasattr(self, '_is_instantiable'):
            return self._is_instantiable
        else:
            return self.destructor is not None and self.destructor.access == 'public'

    @property
    def is_assignable(self):
        if hasattr(self, '_is_assignable'):
            return self._is_assignable
        else:
            return all(method.access == 'public' for method in self.methods(pattern='.*operator=', access='deleted'))

    @property
    def is_derived(self):
        return len(self._asg._base_edges[self._node]) > 0

    @property
    def is_iterator(self):
        return getattr(self, '_is_iterator', False)

    @is_iterator.setter
    def is_iterator(self, is_iterator):
        self._asg._nodes[self._node]['_is_iterator'] = is_iterator

    @is_iterator.deleter
    def is_iterator(self):
        self._asg._nodes[self._node].pop('_is_iterator', False)

    def bases(self, inherited=False, access='private'):
        bases = []
        already = set()
        for base in self._asg._base_edges[self._node]:
            if not base['base'] in already:
                already.add(base['base'])
                bases.append(self._asg[base['base']])
                bases[-1].access = base['_access']
                bases[-1].is_virtual_base = base['_is_virtual']
        if access == 'public':
            bases = [base for base in bases if base.access == 'public']
        elif access == 'protected':
            bases = [base for base in bases if base.access in ['public', 'protected']]
        elif not access == 'private':
            raise ValueError('\'access\' parameter')
        bases = [base.qualified_type.desugared_type.unqualified_type if isinstance(base, TypedefProxy) else base for base in bases]
        if not inherited:
            return bases
        else:
            inheritedbases = []
            for base in bases:
                if isinstance(base, TypedefProxy):
                    basebases = base.qualified_type.desugared_type.unqualified_type.bases(True, access=access)
                else:
                    basebases = base.bases(True, access=access)
                if base.access == 'protected':
                    for basebase in basebases:
                        if basebase.access == 'public':
                            basebase.access = 'protected'
                elif base.access == 'private':
                    for basebase in basebases:
                        basebase.access = 'private'
                inheritedbases += basebases
            return bases + inheritedbases

    def subclasses(self, recursive=False):
        return [cls for cls in self._asg.classes() if any(base._node == self._node for base in cls.bases(inherited=recursive))]

    @property
    def depth(self):
        if not self.is_derived:
            return 0
        else:
            if not hasattr(self, '_depth'):
                depth = max([base.depth for base in self.bases()]) + 1
                self._asg._nodes[self._node]['_depth'] = depth
            return self._depth

    def declarations(self, pattern=None, inherited=False, access='private'):
        if inherited is None:
            declarations = self.declarations(pattern=pattern, inherited=False, access=access) + \
                self.declarations(pattern=pattern, inherited=True, access=access)
        elif inherited:
            declarations = self.declarations(pattern=pattern, inherited=False, access=access)
            for base in self.bases(True):
                if isinstance(base, TypedefProxy):
                    basedeclarations = [basedeclaration for basedeclaration in base.qualified_type.desugared_type.unqualified_type.declarations(pattern=pattern, inherited=False) \
                                        if not basedeclaration.access == 'private']
                else:
                    basedeclarations = [basedeclaration for basedeclaration in base.declarations(pattern=pattern, inherited=False) \
                                        if not basedeclaration.access == 'private']
                if base.access == 'protected':
                    for basedeclaration in basedeclarations:
                        if basedeclaration.access == 'public':
                            basedeclaration.access = 'protected'
                elif base.access == 'private':
                    for basedeclaration in basedeclarations:
                        if not basedeclaration.access == 'deleted':
                            basedeclaration.access = 'private'
                declarations += basedeclarations
            declarations = reversed(sorted(declarations, key= lambda declaration: declaration.parent.depth))
        else:
            if pattern is None:
                declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node]]
            else:
                declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node] if re.match(pattern, node)]
        if access == 'public':
            return [declaration for declaration in declarations if declaration.access == 'public']
        elif access == 'protected':
            return [declaration for declaration in declarations if declaration.access in ['public', 'protected']]
        elif access == 'private':
            return [declaration for declaration in declarations if not declaration.access == 'deleted']
        elif access == 'deleted':
            return declarations
        else:
            raise ValueError('\'access\' parameter')

    def enumerations(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, EnumerationProxy)]

    def enumerators(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, EnumeratorProxy)]

    def typedefs(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, TypedefProxy)]

    def fields(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, FieldProxy)]

    def functions(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, FunctionProxy) and not isinstance(dcl, MethodProxy)]

    def methods(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, MethodProxy)]

    def classes(self, templated=None, specialized=None, **kwargs):
        if templated is None:
            if specialized is None:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, (ClassProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy))]
            elif specialized:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy))]
            else:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, (ClassProxy, ClassTemplateProxy)) and not isinstance(cls, ClassTemplateSpecializationProxy)]
        elif templated:
            if specialized is None:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, (ClassTemplateProxy, ClassTemplatePartialSpecializationProxy))]
            elif specialized:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, ClassTemplatePartialSpecializationProxy)]
            else:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, ClassTemplateProxy)]
        else:
            if specialized is None:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, ClassProxy)]
            elif specialized:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, ClassTemplateSpecializationProxy)]
            else:
                return [cls for cls in self.declarations(**kwargs) \
                        if isinstance(cls, ClassProxy) and not isinstance(cls, ClassTemplateSpecializationProxy)]

    def constructors(self, **kwargs):
        return [ctr for ctr in self.declarations(inherited=False, **kwargs) \
                if isinstance(ctr, ConstructorProxy)]

    @property
    def destructor(self):
        try:
            return [dtr for dtr in self.declarations(inherited=False) if isinstance(dtr, DestructorProxy)].pop()
        except:
            return None

    @property
    def is_error(self):
        if not hasattr(self, '_is_error'):
            self.is_error = self._node == 'class ::std::exception' or any(base.is_error for base in self.bases())
        return self._is_error

    @is_error.setter
    def is_error(self, is_error):
        self._asg._nodes[self._node]['_is_error'] = is_error

    @is_error.deleter
    def is_error(self):
        self._asg._nodes[self._node].pop('_is_error', None)

    @property
    def is_copyable(self):
        if not hasattr(self, '_is_copyable'):
            is_copyable = True
            for ctr in self.constructors(access='deleted'):
                if ctr.is_copy_constructor:
                    is_copyable = ctr.access == 'public'
                    break
            return is_copyable
        else:
            return self._is_copyable

    @is_copyable.setter
    def is_copyable(self, copyable):
        self._asg._nodes[self._node]['_is_copyable'] = copyable

class TemplateSpecializationProxy(object):
    """
    """

    @property
    def specialize(self):
        specialize = self.globalname
        delimiter = 1
        current = -2
        while current > -len(specialize):
            if specialize[current] == '<':
                delimiter -= 1
            elif specialize[current] == '>':
                delimiter += 1
            if delimiter == 0:
                break
            else:
                current -= 1
        specialize = specialize[:current]
        if specialize.startswith('struct '):
            specialize = 'class ' + specialize[len('struct '):]
        elif specialize.startswith('union '):
            specialize = 'class ' + specialize[len('union '):]
        elif not specialize.startswith('class '):
            specialize = 'class ' + specialize
        return self._asg[specialize]

    @property
    def access(self):
        return self._asg._nodes[self._node].get('_access', self.specialize.access)

    @property
    def is_copyable(self):
        return self.specialize.is_copyable

class ClassTemplateSpecializationProxy(ClassProxy, TemplateSpecializationProxy):
    """
    """

    @property
    def header(self):
        if not hasattr(self, '_header'):
            return self.specialize.header
        else:
            return self._asg[self._header]

    @property
    def is_explicit(self):
        return self._is_explicit

    @property
    def templates(self):
        return [QualifiedTypeProxy(self._asg, self._node, **template) for template in self._asg._template_edges[self._node]] #TODO

    @property
    def access(self):
        accesses = ['none', 'public', 'protected', 'private']
        access = accesses.index(getattr(self, '_access', self.specialize.access))
        for template in self.templates:
            access = max(access, accesses.index(template.desugared_type.unqualified_type.access))
        return accesses[access]

    @access.setter
    def access(self, access):
        self._access = access

class ClassTemplateProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

    def specializations(self, partial=None):
        if partial is None:
            return [self._asg[spc] for spc in self._asg._specialization_edges[self._node]]
        elif partial:
            return [spec for spec in self.specializations(None) if isinstance(spec, ClassTemplatePartialSpecializationProxy)]
        else:
            return [spec for spec in self.specializations(None) if isinstance(spec, ClassTemplateSpecializationProxy)]

    @property
    def is_copyable(self):
        return getattr(self, '_is_copyable', True)

    @is_copyable.setter
    def is_copyable(self, is_copyable):
        self._asg._nodes[self._node]['_is_copyable'] = is_copyable

    @is_copyable.deleter
    def del_is_copyable(self):
        self._asg._nodes[self._node].pop('_is_copyable', False)


class ClassTemplatePartialSpecializationProxy(DeclarationProxy, TemplateSpecializationProxy):
    """
    """

    _pakwargs = ['class ', 'struct ', 'union ', '']

class NamespaceProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/namespace>_`
    """

    _pakwargs = ['']

    @property
    def is_inline(self):
        return self._is_inline

    @property
    def header(self):
        return None

    @property
    def anonymous(self):
        return '-' in self._node

    @property
    def is_empty(self):
        return len(self.declarations(True)) == 0

    def declarations(self, pattern=None, nested=False):
        if pattern is None:
            declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node]]
        else:
            declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node] if re.match(pattern, node)]
        if not nested:
            return declarations
        else:
            return [declaration for declaration in declarations if not isinstance(declaration, NamespaceProxy)] + list(itertools.chain(*[namespace.declarations(pattern=pattern, nested=False) for namespace in self.namespaces(pattern=pattern, nested=True)]))

    def enumerations(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, EnumerationProxy)]

    def enumerators(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, EnumeratorProxy)]

    def typedefs(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, TypedefProxy)]

    def variables(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, VariableProxy)]

    def functions(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, FunctionProxy)]

    def classes(self, **kwargs):
        return [dcl for dcl in self.declarations(**kwargs) if isinstance(dcl, ClassProxy)]

    def namespaces(self, pattern=None, nested=False):
        if pattern is None:
            namespaces = [self._asg[node] for node in self._asg._syntax_edges[self._node]]
        else:
            namespaces = [self._asg[node] for node in self._asg._syntax_edges[self._node] if re.match(pattern, node)]
        namespaces = [nsp for nsp in namespaces if isinstance(nsp, NamespaceProxy)]
        if not nested:
            return namespaces
        else:
            return namespaces + list(itertools.chain(*[namespace.namespaces(pattern=pattern, nested=nested) for namespace in namespaces]))

class AbstractSemanticGraph(object):

    def __init__(self):
        self._nodes = dict()
        self._syntax_edges = dict()
        self._base_edges = dict()
        self._type_edges = dict()
        self._parameter_edges = dict()
        self._template_edges = dict()
        self._specialization_edges = dict()
        self._include_edges = dict()

    def merge(self, other):
        if not isinstance(other, AbstractSemanticGraph):
            raise TypeError('\'other\' parameter must be a `' + self.__class__.__name__ + '` instance')
        self._nodes.update(other._nodes)
        self._syntax_edges.update(other._syntax_edges)
        self._base_edges.update(other._base_edges)
        self._type_edges.update(other._type_edges)
        self._parameter_edges.update(other._parameter_edges)
        self._template_edges.update(other._template_edges)
        self._specialization_edges.update(other._specialization_edges)
        self._include_edges.update(other._include_edges)

    def __len__(self):
        return len(self._nodes)

    def add_directory(self, dirname):
        dirname = Path(dirname).abspath()
        initname = str(dirname)
        if not initname.endswith(os.sep):
            initname += os.sep
        if initname not in self._nodes:
            idparent = initname
            if idparent not in self._syntax_edges:
                self._syntax_edges[idparent] = []
            while not dirname == os.sep:
                idnode = idparent
                if not idnode.endswith(os.sep):
                    idnode += os.sep
                if idnode not in self._nodes:
                    self._nodes[idnode] = dict(_proxy=DirectoryProxy)
                    dirname = dirname.parent
                    idparent = str(dirname)
                    if not idparent.endswith(os.sep):
                        idparent += os.sep
                    if idparent not in self._syntax_edges:
                        self._syntax_edges[idparent] = []
                    self._syntax_edges[idparent].append(idnode)
                else:
                    break
            if dirname == os.sep and os.sep not in self._nodes:
                self._nodes[os.sep] = dict(_proxy=DirectoryProxy)
        return self[initname]

    def add_file(self, filename, **kwargs):
        filename = Path(filename).abspath()
        initname = str(filename)
        proxy = kwargs.pop('proxy', FileProxy)
        if initname not in self._nodes:
            idnode = str(filename)
            self._nodes[idnode] = dict(_proxy=proxy, **kwargs)
            idparent = str(filename.parent)
            if not idparent.endswith(os.sep):
                idparent += os.sep
            if idparent not in self._syntax_edges:
                self._syntax_edges[idparent] = []
            self._syntax_edges[idparent].append(idnode)
            self.add_directory(idparent)
        else:
            self._nodes[initname].update(kwargs)
        return self[initname]

    def nodes(self, pattern=None):
        if pattern is None:
            return [self[node] for node in self._nodes.keys()]
        else:
            return [self[node] for node in self._nodes.keys() if re.match(pattern, node)]

    def directories(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, DirectoryProxy)]

    def files(self, header=None, **kwargs):
        if header is None:
            return [node for node in self.nodes(**kwargs) if isinstance(node, FileProxy)]
        elif header:
            return [node for node in self.files(header=None, **kwargs) if isinstance(node, HeaderProxy)]
        else:
            return [node for node in self.files(header=None, **kwargs) if not isinstance(node, HeaderProxy)]

    def declarations(self, free=None, **kwargs):
        if free is None:
            return [node for node in self.nodes(**kwargs) if isinstance(node, DeclarationProxy)]
        elif free:
            return [node for node in self.declarations(free=None, **kwargs) if not isinstance(node.parent, (ClassProxy, EnumerationProxy))]
        else:
            return [node for node in self.declarations(free=None, **kwargs) if isinstance(node.parent, (ClassProxy, EnumerationProxy))]

    def fundamental_types(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, FundamentalTypeProxy)]

    def typedefs(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, TypedefProxy)]

    def enumerations(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, EnumerationProxy)]

    def enumerators(self, anonymous=None, **kwargs):
        if anonymous is None:
            return [node for node in self.declarations(**kwargs) if isinstance(node, EnumeratorProxy)]
        elif anonymous:
            return [node for node in self.enumerators(anonymous=None, **kwargs) if not isinstance(node.parent, EnumerationProxy)]
        else:
            return [node for node in self.enumerators(anonymous=None, **kwargs) if isinstance(node.parent, EnumerationProxy)]

    def variables(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, VariableProxy)]

    def functions(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, FunctionProxy)]

    def constructors(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, ConstructorProxy)]

    def destructors(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, DestructorProxy)]

    def classes(self, specialized=None, templated=False, **kwargs):
        if specialized is None:
            if templated is None:
                return self.classes(specialized=None, templated=True) + self.classes(specialized=None, templated=False)
            elif templated:
                return [node for node in self.declarations(**kwargs) if isinstance(node, ClassTemplateProxy)]
            else:
                return [node for node in self.declarations(**kwargs) if isinstance(node, ClassProxy)]
        elif specialized:
            return [cls for cls in self.classes(specialized=None, templated=templated, **kwargs) if isinstance(cls, TemplateSpecializationProxy)]
        else:
            return [cls for cls in self.classes(specialized=None, templated=templated, **kwargs) if not isinstance(cls, TemplateSpecializationProxy)]

    def namespaces(self, **kwargs):
        return [node for node in self.declarations(**kwargs) if isinstance(node, NamespaceProxy)]

    def dependencies(self, *nodes):
        white = []
        for node in nodes:
            if isinstance(node, basestring):
                node = self[node]
            if isinstance(node, DeclarationProxy) and visitor(node):
                white.append(node)
        black = set()
        gray = set()

        while len(white) > 0:
            node = white.pop()
            if node._node not in black:
                black.add(node._node)
                parent = node.parent
                if not isinstance(parent, NamespaceProxy) and visitor(parent):
                    white.append(parent)
                if isinstance(node, FundamentalTypeProxy):
                    continue
                elif isinstance(node, EnumeratorProxy):
                    if not isinstance(parent, EnumerationProxy):
                        gray.add(node._node)
                    continue
                elif isinstance(node, EnumerationProxy):
                    gray.add(node._node)
                elif isinstance(node, ClassTemplatePartialSpecializationProxy):
                    continue
                elif isinstance(node, (VariableProxy, TypedefProxy)):
                    unqualified_type = node.qualified_type.unqualified_type
                    if visitor(unqualified_type):
                        white.append(unqualified_type)
                elif isinstance(node, FunctionProxy):
                    unqualified_types = [node.return_type.desugared_type.unqualified_type] + [prm.qualified_type.desugared_type.unqualified_type for prm in node.parameters]
                    for unqualified_type in unqualified_types:
                        if visitor(unqualified_type):
                            white.append(unqualified_type)
                elif isinstance(node, ConstructorProxy):
                    unqualified_types = [prm.qualified_type.desugared_type.unqualified_type for prm in node.parameters]
                    for unqualified_type in unqualified_types:
                        if visitor(unqualified_type):
                            white.append(unqualified_type)
                elif isinstance(node, DestructorProxy):
                    continue
                elif isinstance(node, ClassProxy):
                    gray.add(node._node)
                    for base in node.bases():
                        if visitor(base):
                            white.append(base)
                    for declaration in node.declarations():
                        if visitor(declaration):
                            white.append(declaration)
                    if isinstance(node, ClassTemplateSpecializationProxy):
                        for template in node.templates:
                            if visitor(template):
                                white.append(template.desugared_type.unqualified_type)
                elif isinstance(node, ClassTemplateProxy):
                    continue
                elif isinstance(node, NamespaceProxy):
                    continue
                else:
                    raise NotImplementedError(node.__class__.__name__)

        return [self[node] for node in gray]

    def includes(self, *nodes):
        plugin = visitor.plugin
        visitor.plugin = 'all'
        headers = []
        for node in self.dependencies(*nodes):
            header = node.header
            while header is not None and not header.is_self_contained:
                header = header.include
            if header is not None:
                headers.append(header)
        visitor.plugin = plugin

        white = [self[node] if isinstance(node, basestring) else node for node in nodes]
        while len(white) > 0:
            node = white.pop()
            if isinstance(node, FunctionProxy):
                header = node.header
                while header is not None and not header.is_self_contained:
                    header = header.include
                if header is not None:
                    headers.append(header)
            elif isinstance(node, ClassProxy):
                white.extend(node.functions())

        headers = {header.globalname for header in headers}
        headers = sorted([self[header] for header in headers], key = lambda header: header.depth)
        _headers = {header.globalname for header in headers if header.depth == 0}
        for header in [header for header in headers if header.depth > 0]:
            include = header.include
            while include is not None and include.globalname not in _headers:
                include = include.include
            if include is None:
                _headers.add(header.globalname)
        return sorted([self[header] for header in _headers], key = lambda header: header.depth)

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if isinstance(node, NodeProxy):
            node = node.globalname
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if node in self._nodes:
            return self._nodes[node]["_proxy"](self, node)
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
                node = Path(node)
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
