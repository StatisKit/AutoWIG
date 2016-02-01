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

__all__ = ['AbstractSemanticGraph']

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

    @property
    def globalname(self):
        """Node global name

        The node name is not neccessarily unique in the abstract semantic graph (e.g. overload functions)

        .. seealso:: :attr:`node`
        """
        return self._node

    @property
    def children(self):
        """Node children
        """
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

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

    def __dir__(self):
        return sorted([key for key in self._asg._nodes[self._node].keys() if not key.startswith('_')] + [key for key in dir(self.__class__) if not key.startswith('_')])

    def __getattr__(self, attr):
        if not attr in dir(self):
            raise AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')
        else:
            try:
                return self._asg._nodes[self._node][attr]
            except:
                raise

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
        self.asg._nodes[self.node]['_clean'] = clean

    @clean.deleter
    def clean(self):
        self.asg._nodes[self.node].pop('_clean', self._clean_default)

class EdgeProxy(object):
    """Abstract semantic graph node proxy

    .. seealso:: :class:`AbstractSemanticGraph`
    """

    def __init__(self, asg, source, target):
        self._asg = asg
        self._source = source
        self._target = target

    @property
    def asg(self):
        """Edge abstract semantic graph"""
        return self._asg

class FilesytemProxy(NodeProxy):
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
        return self.globalname[self.globalname.rfind(os.sep, 0, -1)+1:]

    @property
    def parent(self):
        """Parent directory

        .. warning:: The parent directory is `None` only for the system root directory
        """
        if self._node == os.sep:
            return None
        else:
            return self._asg[self.globalname[:self.globalname.rfind(os.sep, 0, -1)]]

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

    #@property
    #def directories(self):
    #    return [d for d in [self._asg[d] for d in self._asg._syntax_edges[self._node]] if isinstance(d, DirectoryProxy)]

    #@property
    #def files(self):
    #    return [f for f in [self._asg[f] for f in self._asg._syntax_edges[self._node]] if isinstance(f, FileProxy)]

    #def walkdirs(self, pattern=None):
    #    if pattern is None:
    #        directories = self.directories
    #    else:
    #        directories = [d for d in self.directories if fnmatch(d.globalname, pattern)]
    #    return directories + list(itertools.chain(*[d.walkdirs(pattern=pattern) for d in self.directories]))

    #def walkfiles(self, pattern=None):
    #    if pattern is None:
    #        files = self.files
    #    else:
    #        files =  [f for f in self.files if fnmatch(f.globalname, pattern)]
    #    return files + list(itertools.chain(*[d.walkfiles(pattern=pattern) for d in self.directories]))

def get_is_searchpath(self):
    if hasattr(self, '_is_searchpath'):
        return self._is_searchpath
    else:
        return False

def set_is_searchpath(self, is_searchpath):
    self._asg._nodes[self._node]['_is_searchpath'] = is_searchpath

def del_is_searchpath(self):
    self._asg._nodes[self._node].pop('_is_searchpath', False)

DirectoryProxy.is_searchpath = property(get_is_searchpath, set_is_searchpath, del_is_searchpath, doc = """Is this directory a search path

.. note:: A compilation dependent property

    This property is setted at each front-end execution.
    Any application of a front-end reset this property since search paths can differ from one compilation to another.

.. seealso:: :func:`autowig.front_end.preprocessing`""")
del get_is_searchpath, set_is_searchpath, del_is_searchpath

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

    #@property
    #def sloc(self):
    #    return sloc_count(self.content, language=self.language)

    def write(self, database=None, force=False):
        """Write the file and its ancestral directories into the filesystem

        :Optional Parameters:
         - `database` ({str:str}) - A database interfaced as a dictionnary.
                                    A database key correspond to a file global name.
                                    A database value correspond to a file md5.
                                    If the database is given, the file is written to the disk only if its current md5 is the same as the one stored in the database.
                                    If a file is written to the disk, its md5 is updated.
         - `force` (bool) - If set to true, files are written to disk whatever the md5 stored in the database.
                            Yet, if its current md5 is the same as the one stored in the database, a warning is displayed.
        """
        if database:
            if self.on_disk and self.globalname in database:
                with open(self.globalname, 'r') as filehandler:
                    if not hashlib.md5(filehandler.read()).hexdigest() == database[self.globalname]:
                        if force:
                            warnings.warn('File written to disk while md5 signature was not up to date', UserWarning)
                        else:
                            raise IOError('File not written to disk since md5 signature was not up to date')
            elif not self.on_disk:
                parent = self.parent
                if not parent.on_disk:
                    parent.makedirs()
            with open(self.globalname, 'w') as filehandler:
                filehandler.write(self.content)
                database[self.globalname] = hashlib.md5(self.content).hexdigest()
        else:
            if not self.on_disk:
                parent = self.parent
                if not parent.on_disk:
                    parent.makedirs()
            with open(self.globalname, 'w') as filehandler:
                filehandler.write(self.content)

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
        if parent is None:
            return '/' + incpath
        else:
            return incpath

def get_language(self):
    return self._language

def set_language(self, language):
    if not isinstance(language, basestring):
        raise TypeError('\'language\' parameter')
    language = language.lower()
    if not language in ['c', 'c++']:
        raise ValueError('\'language\' parameter')
    self._asg._nodes[self._node]['_language'] = language

HeaderProxy.language = property(get_language, set_language, doc="""Language of the header file

Possible languages for a header file is either `c` or `c++`
""")
del get_language, set_language

def get_is_standalone(self):
    if hasattr(self, '_is_standalone'):
        return self._is_standalone
    else:
        return False

def set_is_standalone(self, is_standalone):
    self._asg._nodes[self._node]['_is_standalone'] = is_standalone

def del_is_standalone(self):
    self._asg._nodes[self._node].pop('_is_standalone', None)

HeaderProxy.is_standalone = property(get_is_standalone, set_is_standalone, del_is_standalone, doc="""Is this a stand-alone header

A header is considered as stand-alone if it can be included in a source file without producing any errors.
By default, only header given as input of an AutoWIG front-end are considered as stand-alone.

.. seealso:: :func:`autowig.front_end.postprocessing`""")
del get_is_standalone, set_is_standalone, del_is_standalone

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
        if isinstance(self, FunctionProxy):
            return re.sub('::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', '', self._node)
        else:
            return self._node

    @property
    def localname(self):
        localname = self.globalname
        if isinstance(self, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
            delimiter = 0
            current = 0
            while current < len(localname):
                if localname[current] == '<':
                    delimiter += 1
                    current += 1
                elif localname[current] == '>':
                    delimiter -= 1
                    current += 1
                elif localname[current:current+2] == '::' and delimiter == 0:
                    break
                else:
                    current += 1
            return localname[current:]
        else:
            return localname[localname.rindex(':'):]

    @property
    def parent(self):
        parentname = self.globalname[:len(self.localname)-2]
        if isinstance(self, EnumerationProxy):
            if parentname.startswith('enum '):
                parentname = parentname[len('enum '):]
        elif isinstance(self, ClassProxy):
            if parentname.startswith('class '):
                parentname = parentname[len('class '):]
            elif parentname.startswith('struct '):
                parentname = parentname[len('struct '):]
            elif parentname.startswith('union '):
                parentname = parentname[len('union '):]
        elif isinstance(self, ClassTemplateProxy):
            parentname = parentname[len('class ':]
        if parent == '':
            return self._asg['::']
        else:
            for keyword in self._pakwargs:
                if keyword + parentname in self._asg:
                    parent = self._asg[keyword + parentname]
                    break
            return parent

class FundamentalTypeProxy(DeclarationNodeProxy):
    """Abstract semantic graph node proxy for a fundamental type

    .. seealso:: `C++ fundamental types <http://en.cppreference.com/w/cpp/language/types>`
    """

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

    node = "::short int"

class SignedIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::int"

class SignedLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::long int"

class SignedLongLongIntegerTypeProxy(SignedIntegerTypeProxy):
    """
    """

    node = "::long long int"

class UnsignedIntegerTypeProxy(FundamentalTypeProxy):
    """
    """

class UnsignedShortIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned short int"

class UnsignedIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned int"

class UnsignedLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned long int"

class UnsignedLongLongIntegerTypeProxy(UnsignedIntegerTypeProxy):
    """
    """

    node = "::unsigned long long int"

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

class ComplexFloatTypeProxy(ComplexTypeProxy):

    node = "::_Complex float"

class ComplexDoubleTypeProxy(ComplexTypeProxy):

    node = "::_Complex double"

class ComplexLongDoubleTypeProxy(ComplexTypeProxy):

    node = "::_Complex long double"

class NullPtrTypeProxy(FundamentalTypeProxy):
    """
    """

    node = "::nullptr_t"

class VoidTypeProxy(FundamentalTypeProxy):
    """
    """

    node = "::void"


class QualifiedTypeProxy(EdgeProxy):
    """Abstract semantic graph edge proxy for qualified type.

    A (possibly-)qualified type.

    For efficiency, we don't store CV-qualified types as nodes on their own: instead each reference to a type stores the qualifiers.
    This greatly reduces the number of nodes we need to allocate for types (for example we only need one for 'int', 'const int', 'volatile int', 'const volatile int', etc).

    As an added efficiency bonus, instead of making this a pair, we just store the two bits we care about in the low bits of the pointer.
    To handle the packing/unpacking, we make QualType be a simple wrapper class that acts like a smart pointer.
    A third bit indicates whether there are extended qualifiers present, in which case the pointer points to a special structure.

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
            desugared_type = desugared_type.qualifed_type
        return QualifiedTypeProxy(self._asg, self._source, desugared_type._node, qualifiers)

    @property
    def qualifiers(self):
        """Type qualifiers"""
        return self._qualifiers

    def is_fundamental_type(self):
        """Is the unqualified type a fundamental type"""
        return isinstance(self.unqualified_type, FundamentalTypeProxy)

    def is_pointer(self):
        """Is the qualified type a pointer"""
        return '*' in self.qualifiers

    def is_pointer_chain(self):
        """Is the qualified type a chain of pointers"""
        return self.qualifiers.count('*') > 1

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

    def is_const(self):
        """Is the qualified type const qualified"""
        if self.qualifiers.endswith('&&'):
            return self.qualifiers.endswith('const &&') or self.qualifiers.endswith('const volatile &&')
        elif self.qualifiers.endswith('&'):
            return self.qualifiers.endswith('const &') or self.qualifiers.endswith('const volatile &')
        else:
            return self.qualifiers.endswith('const') or self.qualifiers.endswith('const volatile')

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

    _pakwargs = ['enum ', 'class ', '']

class EnumerationProxy(DeclarationProxy):
    """

    .. seealso:: `Enumerations <http://en.cppreference.com/w/cpp/language/enum>`
    """

    _pakwargs = ['', 'class ']

    @property
    def is_complete(self):
        return len(self._asg._syntax_edges[self._node]) > 0

    @property
    def enumerators(self):
        return [self._asg[node] for node in self._asg._syntax_edges[self._node]]

class TypedefProxy(DeclarationProxy):
    """

    .. seealso:: `Typedefs <http://en.cppreference.com/w/cpp/language/typedef>`
    """

    _pakwargs = ['', 'class ']

    @property
    def qualified_type(self):
        return QualifiedType(self._asg, self._node, **self._asg._type_edges[self._node])


class VariableProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['', 'class ']

    @property
    def qualified_type(self):
        return QualifiedType(self._asg, self._node, **self._asg._type_edges[self._node])

class FieldProxy(VariableProxy):
    """
    """

    @property
    def is_mutable(self):
        return self._is_mutable

    @property
    def is_static(self):
        return self._is_static


class ParameterProxy(EdgeProxy):
    """
    """

    @property
    def qualified_type(self):
        return QualifiedType(self._asg, self._source, self._asg._parameter_edges[self._source][self._target]['target'], self._asg._parameter_edges[self._source][self._target]['specifiers'])

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

class FunctionProxy(DeclarationProxy):
    """
    """

    _pakwargs = ['', 'class ']

    @property
    def return_type(self):
        return QualifiedType(self._asg, self._node, **self._asg._type_edges[self._node])

    @property
    def nb_parameters(self):
        return len(self._asg._parameter_edges[self._node])

    @property
    def parameters(self):
        return [ParameterProxy(self._asg, self._node, index) for index in range(self.nb_parameters)]

    @property
    def overloads(self):
        parent = self.parent
        if isinstance(parent, NamespaceProxy):
            return [overload for overload in self.parent.functions() if overload.localname == self.localname]
        elif isinstance(parent, ClassProxy):
            return [overload for overload in self.parent.methods() if overload.localname == self.localname]
        else:
            raise NotImplementedError('For parent class \'' + parent.__class__.__name__ + '\'')

    def signature(self, scoped=False, desugared=True):
        if scoped:
            signature = self.globalname
        else:
            signature = self.localname
        if desugared:
            return self.return_type.desugared_type.globalname + ' ' + signature + '(' + ', '.join(parameter.qualified_type.desugared_type.globalname for parameter in self.parameters) + ')'
        else:
            return self.return_type.globalname + ' ' + signature + '(' + ', '.join(parameter.qualified_type.globalname for parameter in self.parameters) + ')'

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
    def is_static(self):
        return self._is_static

    @property
    def is_const(self):
        return self._is_const

    @propertyglobalname
    def is_volatile(self):
        return self._is_volatile

    @property
    def is_virtual(self):
        return self._is_virtual

    @property
    def is_pure(self):
        return self._is_pure

#class ConversionProxy(DeclarationProxy):
#    """
#    """
#
#    @property
#    def parent(self):
#        parent = remove_templates(self.globalname)
#        parent = parent[:parent.rindex(':')-1]
#        if parent == '':
#            return self._asg['::']
#        else:
#            for decorator in ['class', 'struct', 'union']:
#                decorator += ' ' + parent
#                if decorator in self._asg._nodes:
#                    parent = self._asg[decorator]
#                    break
#            if not isinstance(parent, NodeProxy):
#                if not parent in self._asg._nodes:
#                    raise ValueError('\'' + self.globalname + '\' parent (\'' + parent + '\') was not found')
#                parent = self._asg[parent]
#            return parent
#
#    @property
#    def type(self):
#        return TypeSpecifiersProxy(self._asg, **self._asg._type_edges[self._node])

class ConstructorProxy(DeclarationProxy):
    """
    """

    @property
    def nb_parameters(self):
        return len(self._asg._parameter_edges[self._node])

    @property
    def parameters(self):
        return [ParameterProxy(self._asg, self._node, index) for index in range(self.nb_parameters)]

    @property
    def is_virtual(self):
        return self._is_virtual

class DestructorProxy(DeclarationProxy):
    """
    """

    @property
    def is_virtual(self):
        return self._is_virtual

class ClassProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/class>_`
    """

    @property
    def is_complete(self):
        return self._is_complete

    @property
    def is_abstract(self):
        return self._is_abstract

    @property
    def is_copyable(self):
        return self._is_copyable

    @property
    def is_derived(self):
        return len(self._asg._base_edges[self._node]) > 0

    def bases(self, inherited=False):
        bases = []
        already = set()
        for base in self._asg._base_edges[self._node]:
            if not base['base'] in already:
                already.add(base['base'])
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
        return [cls for cls in self._asg.classes() if any(base.node == self._node for base in cls.bases(inherited=recursive))]

    @property
    def depth(self):
        if not self.is_derived:
            return 0
        else:
            if not hasattr(self, '_depth'):
                self._asg._nodes[self._node]['_depth'] = max([base.type.target.depth if isinstance(base, TypedefProxy) else base.depth for base in self.bases()])+1
            return self._depth

    def declarations(self, pattern=None, inherited=False, access='all'):
        if pattern is None:
            declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node]]
        else:
            declarations = [self._asg[node] for node in self._asg._syntax_edges[self._node] if re.match(pattern, node)]
        for declaration in declarations:
            declaration.access = self._asg._node[declaration._node]['_access']
        if inherited:
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
        if access == 'public':
            return [declaration for declaration in declarations if declaration.access == 'public']
        elif access == 'protected':
            return [declaration for declaration in declarations if declaration.access == 'protected']
        elif access == 'private':
            return [declaration for declaration in declarations if declaration.access == 'private']
        elif access == 'all':
            return declarations
        else:
            raise ValueError('\'access\' parameter')

    def enumerations(self, **kwargs):
        return [dcl for dcl in self.declarations(metaclass=metaclass, **kwargs) if isinstance(dcl, EnumerationProxy)]

    def enumerators(self, **kwargs):
        return [dcl for dcl in self.declarations(metaclass=metaclass, **kwargs) if isinstance(dcl, EnumeratorProxy)]

    def typedefs(self, **kwargs):
        return [dcl for dcl in self.declarations(metaclass=metaclass, **kwargs) if isinstance(dcl, TypedefProxy)]

    def fields(self, **kwargs):
        return [dcl for dcl in self.declarations(metaclass=metaclass, **kwargs) if isinstance(dcl, FieldProxy)]

    def methods(self, **kwargs):
        return [dcl for dcl in self.declarations(metaclass=metaclass, **kwargs) if isinstance(dcl, MethodProxy)]

    def classes(self, templated=None, specialized=None, **kwargs):
        if templated is None:
            if specialized is None:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, (ClassProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy))]
            elif specialized:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy))]
            else:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, (ClassProxy, ClassTemplateProxy)) and not isinstance(cls, ClassTemplateSpecializationProxy)]
        elif templated:
            if specialized is None:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, (ClassTemplateProxy, ClassTemplatePartialSpecializationProxy))]
            elif specialized:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, ClassTemplatePartialSpecializationProxy)]
            else:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, ClassTemplateProxy)]
        else:
            if specialized is None:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, ClassProxy)]
            elif specialized:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, ClassTemplateSpecializationProxy)]
            else:
                return [cls for cls in self.declarations(**kwargs) if isinstance(cls, ClassProxy) and not isinstance(cls, ClassTemplateSpecializationProxy)]

    @property
    def constructors(self):
        return [ctr for ctr in self.declarations(inherited=False) if isinstance(ctr, ConstructorProxy)]

    @property
    def destructor(self):
        try:
            return [dtr for dtr in self.declarations(inherited=False) if isinstance(dtr, DestructorProxy)].pop()
        except:
            return None

def get_is_copyable(self):
    return self._is_copyable

def set_is_copyable(self, copyable):
    self._asg._nodes[self._node]['_is_copyable'] = copyable

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
#        return self._asg[self._target['target']]
#
#    @property
#    def specifiers(self):
#        return self._target["specifiers"]

class TemplateSpecializationProxy(object):
    """
    """

    @property
    def specialize(self):
        specialize = self.globalname
        delimiter = 0
        current = 0
        while current < len(localname):
            if localname[current] == '<':
                delimiter += 1
                current += 1
            elif localname[current] == '>':
                delimiter -= 1
                current += 1
            elif localname[current:current+2] == '::' and delimiter == 0:
                break
            else:
                current += 1
        if specialize.startswith('struct '):
            specialize = 'class ' + specialize[len('struct '):]
        elif specialize.startswith('union '):
            specialize = 'class ' + specialize[len('union '):]
        elif not specialize.startswith('class '):
            specialize = 'class ' + specialize
        return self._asg[specialize]

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
        return [QualifiedTypeProxy(self._asg, **template) for template in self._asg._template_edges[self._node]] #TODO


class ClassTemplateProxy(DeclarationProxy):
    """
    """

    def specializations(self, partial=None):
        if partial is None:
            return [self._asg[spc] for spc in self._asg._specialization_edges[self._node]]
        elif partial:
            return [spec for spec in self.specializations(None) if isinstance(spec, ClassTemplatePartialSpecializationProxy)]
        else:
            return [spec for spec in self.specializations(None) if isinstance(spec, ClassTemplateSpecializationProxy)]

class ClassTemplatePartialSpecializationProxy(ClassTemplateProxy, TemplateSpecializationProxy):
    """
    """

class NamespaceProxy(DeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/namespace>_`
    """

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

    def __init__(self, *args, **kwargs):
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
                    self._nodes[idnode] = dict(_proxy=DirectoryProxy)
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
                self._nodes[os.sep] = dict(_proxy=DirectoryProxy)
        return self[initname]

    def add_file(self, filename, **kwargs):
        filename = path(filename).abspath()
        initname = str(filename)
        proxy = kwargs.pop('proxy', FileProxy)
        if not initname in self._nodes:
            idnode = str(filename)
            self._nodes[idnode] = dict(_proxy=proxy, **kwargs)
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

    def nodes(self, pattern=None):
        if pattern is None:
            return [self[node] for node in self._nodes.keys()]
        else:
            return [self[node] for node in self._nodes.keys() if re.match(pattern, node)]

    def directories(self, pattern=None):
        class _MetaClass(object):
            __metaclass__ = ABCMeta
        _MetaClass.register(DirectoryProxy)
        metaclass = _MetaClass
        return self._nodes(pattern, metaclass=metaclass)
        return [node for node in self.nodes(**kwargs) if isinstance(node, )]

    def files(self, pattern=None, header=None):
        return [node for node in self.nodes(**kwargs) if isinstance(node, )]

        if header is None:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(FileProxy)
            metaclass = _MetaClass
            return self._nodes(pattern, metaclass=metaclass)
        elif header:
            class _MetaClass(object):
                __metaclass__ = ABCMeta
            _MetaClass.register(HeaderProxy)
            metaclass = _MetaClass
            return self._nodes(pattern, metaclass=metaclass)
        else:
            return [f for f in self.files(pattern=pattern, header=None) if not isinstance(f, HeaderProxy)]

    def declarations(self, free=None, **kwargs):
        if free is None:
            return [node for node in self.nodes(**kwargs) if isinstance(node, DeclarationProxy)]
        elif free:
            return [node for node in self.nodes(free=None, **kwargs) if not isinstance(node.parent, ClassProxy)]
        else:
            return [node for node in self.nodes(free=None, **kwargs) if isinstance(node.parent, ClassProxy)]

    def fundamental_types(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, FundamentalTypeProxy)]

    def typedefs(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, TypedefProxy)]

    def enumarations(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, EnumerationProxy)]

    def enumerators(self, anonymous=None, **kwargs):
        if anonymous is None:
            return [node for node in self.nodes(**kwargs) if isinstance(node, EnumeratorProxy)]
        elif anonymous:
            return [node for node in self.enumerators(anonymous=None, **kwargs) if not isinstance(node.parent, EnumerationProxy)]
        else:
            return [node for node in self.enumerators(anonymous=None, **kwargs) if isinstance(node.parent, EnumerationProxy)]

    def variables(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, VariableProxy)]

    def functions(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, FunctionProxy)]

    def classes(self, specialized=None, templated=False, **kwargs):
        if spelicalized is None:
            if templated is None:
                return self.classes(specialized=None, templated=True) + self.classes(specialized=None, templated=False)
            elif templated
                return [node for node in self.nodes(**kwargs) if isinstance(node, ClassTemplateProxy)]
            else:
                return [node for node in self.nodes(**kwargs) if isinstance(node, ClassProxy)]
        elif specialized:
            return [cls for cls in self.classes(specialized=None, templated=templated, **kwargs) if isinstance(cls, TemplateSpecializationProxy)]
        else:
            return [cls for cls in self.classes(specialized=None, templated=templated, **kwargs) if not isinstance(cls, TemplateSpecializationProxy)]

    def namespaces(self, **kwargs):
        return [node for node in self.nodes(**kwargs) if isinstance(node, NamespaceProxy)]

    #def include_path(self, header, absolute=False):
    #    if not header.is_standalone:
    #        include = header.include
    #        while include is not None and not include.is_indepentent:
    #            include = include.include
    #        if include is None:
    #            raise ValueError('\'header\' parameter is not independent and has no include parent file independent')
    #        header = include
    #    if absolute:
    #        return header.globalname
    #    else:
    #        include = header.localname
    #        parent = header.parent
    #        while not parent.localname == '/' and not parent.is_searchpath:
    #            include = parent.localname + include
    #            parent = parent.parent
    #        if parent.localname == '/':
    #            return '/' + include
    #        else:
    #            return include

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
                elif isinstance(node, EnumeratorProxy):
                    pass
                elif isinstance(node, EnumerationProxy):
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
                while not header is None and not header.is_standalone:
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

    def clean(self):
        """
        """
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
            if isinstance(node, HeaderProxy):
                include = node.include
                if not include is None:
                    if include.clean:
                        temp.append(include)
                    else:
                        include.clean = False
            elif isinstance(node, (TypedefProxy, VariableProxy)):
                target = node.type.target
                if target.clean:
                    temp.append(target)
                else:
                    target.clean = False
            elif isinstance(node, EnumerationProxy):
                for enumerator in node.enumerators:
                    if enumerator.clean:
                        temp.append(enumerator)
                    else:
                        enumerator.clean = False
            elif isinstance(node, FunctionProxy):
                result_type = node.result_type.target
                if result_type.clean:
                    temp.append(result_type)
                else:
                    result_type.clean = False
                for parameter in node.parameters:
                    target = parameter.type.target
                    if target.clean:
                        temp.append(target)
                    else:
                        target.clean = False
            elif isinstance(node, ConstructorProxy):
                for parameter in node.parameters:
                    target = parameter.type.target
                    if target.clean:
                        temp.append(target)
                    else:
                        target.clean = False
            elif isinstance(node, ClassProxy):
                for base in node.bases():
                    if base.clean:
                        temp.append(base)
                    else:
                        base.clean = False
                for dcl in node.declarations():
                    if dcl.clean:
                        temp.append(dcl)
                    else:
                        dcl.clean = False
                if isinstance(node, ClassTemplateSpecializationProxy):
                    specialize = node.specialize
                    if specialize.clean:
                        temp.append(node.specialize)
                    else:
                        specialize.clean = False
                    for template in node.templates:
                        target = template.target
                        if target.clean:
                            temp.append(target)
                        else:
                            target.clean = False
            elif isinstance(node, ClassTemplateProxy):
                pass
        for tdf in self.typedefs():
            if tdf.clean and not tdf.type.target.clean and not tdf.parent.clean:
                tdf.clean = False
                include = tdf.header
                while not include is None:
                    include.clean = False
                    include = include.include
        nodes = [node for node in self.nodes() if node.clean]
        for node in nodes:
            if not node.node in ['::', '/']:
                self._syntax_edges[node.parent.node].remove(node.node)
                if isinstance(node, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
                    self._specialization_edges[node.specialize.node].remove(node.node)
        for node in nodes:
            self._nodes.pop(node.node)
            self._include_edges.pop(node.node, None)
            self._syntax_edges.pop(node.node, None)
            self._base_edges.pop(node.node, None)
            self._type_edges.pop(node.node, None)
            self._parameter_edges.pop(node.node, None)
            self._specialization_edges.pop(node.node, None)
        nodes = set([node.node for node in nodes])
        for node in self.nodes():
            if isinstance(node, ClassProxy):
                self._base_edges[node.node] = [base for base in self._base_edges[node.node] if not base['base'] in nodes]
            del node.clean
        for node, clean in cleanbuffer:
            if node.node in self:
                node.clean = clean

__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(NodeProxy)]
__all__ += [subclass.__name__.rsplit('.', 1).pop() for subclass in subclasses(EdgeProxy)]
