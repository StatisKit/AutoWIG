import time
from path import path
from ConfigParser import ConfigParser
from clang.cindex import Config, conf, Cursor, Index, TranslationUnit, CursorKind, Type, TypeKind
from ConfigParser import ConfigParser
from tempfile import NamedTemporaryFile
import os
import warnings
import uuid

from .ast import AbstractSyntaxTree
from .asg import *
from .tools import remove_regex, split_scopes, remove_templates
from .custom_warnings import NotWrittenFileWarning, ErrorWarning, NoneTypeWarning,  UndeclaredParentWarning, MultipleDeclaredParentWarning, MultipleDefinitionWarning, NoDefinitionWarning, SideEffectWarning, ProtectedFileWarning, InfoWarning, TemplateParentWarning, TemplateParentWarning, AnonymousWarning, AnonymousFunctionWarning, AnonymousFieldWarning, AnonymousClassWarning, NotImplementedWarning, NotImplementedTypeWarning, NotImplementedDeclWarning, NotImplementedParentWarning, NotImplementedOperatorWarning, NotImplementedTemplateWarning

def is_virtual_method(self):
    """Returns True if the cursor refers to a C++ member function that
    is declared 'virtual'.
    """
    return conf.lib.clang_CXXMethod_isVirtual(self)

Cursor.is_virtual_method = is_virtual_method
del is_virtual_method

def is_pure_virtual_method(self):
    """Returns True if the cursor refers to a C++ member function that
    is declared pure 'virtual'.
    """
    return conf.lib.clang_CXXMethod_isPureVirtual(self)

Cursor.is_pure_virtual_method = is_pure_virtual_method
del is_pure_virtual_method

def is_abstract_record(self):
    """Returns True if the cursor refers to a C++ member function that
    is declared pure 'virtual'.
    """
    return conf.lib.clang_CXXRecord_isAbstract(self)

Cursor.is_abstract_record = is_abstract_record
del is_abstract_record

def is_copyable_record(self):
    """Returns True if the cursor refers to a C++ member function that
    is declared pure 'virtual'.
    """
    return conf.lib.clang_CXXRecord_isCopyable(self)

Cursor.is_copyable_record = is_copyable_record
del is_copyable_record

class LibclangDiagnostic(object):

    name = 'libclang'

    def __init__(self):
        self.parsing = 0.
        self.translating = 0.

    @property
    def total(self):
        return self.parsing + self.translating

    def __str__(self):
        string = "Processing: " + str(self.total)
        string += "\n" + " * Parsing: " + str(self.parsing)
        string += "\n" + " * Translating: " + str(self.translating)
        return string

def _libclang_front_end(self, content, flags, libpath=None, silent=False):
    diagnostic = LibclangDiagnostic()
    step = []
    prev = time.time()
    if not libpath is None:
        libpath = path(libpath)
        libpath = libpath.abspath()
        if not libpath.exists():
            raise ValueError('\'libpath\' parameter: \'' + str(libpath) + '\' doesn\'t exists')
        if libpath.isdir():
            Config.set_library_path(str(libpath))
        elif libpath.isfile():
            Config.set_library_file(str(libpath))
        else:
            raise ValueError('\'libpath\' parameter: should be a path to a directory or a file')
    else:
        if not Config.loaded:
            raise ValueError('\'libpath\' parameter: should not be set to \'None\'')
    index = Index.create()
    tempfilehandler = NamedTemporaryFile(delete=False)
    tempfilehandler.write(content)
    tempfilehandler.close()
    tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
    os.unlink(tempfilehandler.name)
    curr = time.time()
    diagnostic.parsing = curr - prev
    prev = time.time()
    with warnings.catch_warnings() as cw:
        if silent:
            warnings.simplefilter('ignore')
        else:
            warnings.simplefilter('always')
        self._libclang_read_translation_unit(tu)
    curr = time.time()
    diagnostic.translating = curr - prev
    return diagnostic

AbstractSemanticGraph._libclang_front_end = _libclang_front_end
AbstractSyntaxTree._libclang_front_end = _libclang_front_end
del _libclang_front_end

def _libclang_read_translation_unit(self, tu):
    for child in tu.cursor.get_children():
        self._libclang_read_cursor(child, '::')

AbstractSemanticGraph._libclang_read_translation_unit = _libclang_read_translation_unit
del _libclang_read_translation_unit

def _libclang_read_translation_unit(self, tu):
    self._nodes = dict()
    self._children = dict()
    self._nodes[0] = tu.cursor
    self._children[0] = []
    self._node = 1
    for child in tu.cursor.get_children():
        self._children[0].append(self._libclang_read_cursor(child))
    del self._node

AbstractSyntaxTree._libclang_read_translation_unit = _libclang_read_translation_unit
del _libclang_read_translation_unit

def _libclang_read_qualified_type(self, qtype):
    specifiers = ''
    while True:
        if qtype.kind is TypeKind.POINTER:
            specifiers = ' *' + ' const' * qtype.is_const_qualified() + specifiers
            qtype = qtype.get_pointee()
        elif qtype.kind is TypeKind.LVALUEREFERENCE:
            specifiers = ' &' + specifiers
            qtype = qtype.get_pointee()
        elif qtype.kind is TypeKind.RVALUEREFERENCE:
            specifiers = ' &&' + specifiers
            qtype = qtype.get_pointee()
        elif qtype.kind in [TypeKind.RECORD, TypeKind.TYPEDEF, TypeKind.ENUM, TypeKind.UNEXPOSED]:
            cursor = qtype.get_declaration()
            spelling = '::' + cursor.type.spelling
            if cursor.kind is CursorKind.ENUM_DECL:
                spelling = 'enum ' + spelling
            if qtype.is_const_qualified():
                specifiers = ' const' + specifiers
            if qtype.is_volatile_qualified():
                specifiers = ' volatile' + specifiers
            try:
                return self[spelling].node, specifiers
            except:
                warnings.warn('record not found')
                break
        else:
            target, _specifiers = self._libclang_read_builtin_type(qtype)
            return target, _specifiers + specifiers

AbstractSemanticGraph._libclang_read_qualified_type = _libclang_read_qualified_type
del _libclang_read_qualified_type

def _libclang_read_builtin_type(self, btype):
    if btype.kind in [TypeKind.CHAR_U, TypeKind.CHAR_S]:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return CharTypeProxy.node, specifiers
    elif btype.kind is TypeKind.UCHAR:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return UnsignedCharTypeProxy.node, specifiers
    elif btype.kind is TypeKind.SCHAR:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedCharTypeProxy.node, specifiers
    elif btype.kind is TypeKind.CHAR16:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return Char16TypeProxy.node, specifiers
    elif btype.kind is TypeKind.CHAR32:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return Char32TypeProxy.node, specifiers
    elif btype.kind is TypeKind.WCHAR:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return WCharTypeProxy.node, specifiers
    elif btype.kind is TypeKind.SHORT:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedShortIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.INT:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.LONG:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedLongIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.LONGLONG:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedLongLongIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.USHORT:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return UnsignedShortIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.UINT:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return UnsignedIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.ULONG:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return UnsignedLongIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.ULONGLONG:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return UnsignedLongLongIntegerTypeProxy.node, specifiers
    elif btype.kind is TypeKind.FLOAT:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedFloatTypeProxy.node, specifiers
    elif btype.kind is TypeKind.DOUBLE:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedDoubleTypeProxy.node, specifiers
    elif btype.kind is TypeKind.LONGDOUBLE:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return SignedLongDoubleTypeProxy.node, specifiers
    elif btype.kind is TypeKind.BOOL:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return BoolTypeProxy.node, specifiers
    elif btype.kind is TypeKind.COMPLEX:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return ComplexTypeProxy.node, specifiers
    elif btype.kind is TypeKind.VOID:
        if btype.is_const_qualified():
            specifiers = ' const'
        else:
            specifiers = ''
        return VoidTypeProxy.node, specifiers
    else:
        warnings.warn('\'' + str(btype.kind) + '\'', NotImplementedTypeWarning)

AbstractSemanticGraph._libclang_read_builtin_type = _libclang_read_builtin_type
del _libclang_read_builtin_type

def _libclang_read_enum(self, cursor, scope):
    if not scope.endswith('::'):
        spelling = scope + "::" + cursor.spelling
    else:
        spelling = scope + cursor.spelling
    if cursor.spelling == '':
        children = []
        decls = []
        if not spelling == '::':
            spelling = spelling[:-2]
        for child in cursor.get_children():
            if child.kind is CursorKind.ENUM_CONSTANT_DECL:
                children.extend(self._libclang_read_enum_constant(child, spelling))
                decls.append(child)
        filename = str(path(str(cursor.location.file)).abspath())
        self.add_file(filename, language=self._language)
        for childspelling, child in zip(children, decls):
            self._nodes[childspelling]['_header'] = filename
            self._nodes[spelling]['cursor'] = child
        return children
    else:
        spelling = 'enum ' + spelling
        if not spelling in self :
            self._syntax_edges[spelling] = []
            self._nodes[spelling] = dict(proxy=EnumProxy)
            self._syntax_edges[scope].append(spelling)
        elif not self[spelling].is_complete:
            self._syntax_edges[scope].remove(spelling)
            self._syntax_edges[scope].append(spelling)
        if not self[spelling].is_complete:
            for child in cursor.get_children():
                self._libclang_read_enum_constant(child, spelling)
        if self[spelling].is_complete:
            filename = str(path(str(cursor.location.file)).abspath())
            self.add_file(filename, language=self._language)
            self._nodes[spelling]['_header'] = filename
            self._nodes[spelling]['cursor'] = cursor
        return [spelling]

AbstractSemanticGraph._libclang_read_enum = _libclang_read_enum
del _libclang_read_enum

def _libclang_read_enum_constant(self, cursor, scope):
    if not scope.endswith('::'):
        spelling = scope + "::" + cursor.spelling
    else:
        spelling = scope + cursor.spelling
    spelling = spelling.replace('enum ', '')
    self._nodes[spelling] = dict(proxy=EnumConstantProxy)
    self._syntax_edges[scope].append(spelling)
    return [spelling]

AbstractSemanticGraph._libclang_read_enum_constant = _libclang_read_enum_constant
del _libclang_read_enum_constant

def _libclang_read_typedef(self, typedef, scope):
    if not scope.endswith('::'):
        spelling = scope + "::" + typedef.spelling
    else:
        spelling = scope + typedef.spelling
    if not spelling in self:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                target, specifiers = self._libclang_read_qualified_type(typedef.underlying_typedef_type)
        except Warning as warning:
            warnings.warn(str(warning) + ' for typedef \'' + spelling + '\'', warning.__class__)
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

AbstractSemanticGraph._libclang_read_typedef = _libclang_read_typedef
del _libclang_read_typedef

def _libclang_read_variable(self, cursor, scope):
    if any(child.kind in [CursorKind.TEMPLATE_NON_TYPE_PARAMETER, CursorKind.TEMPLATE_TYPE_PARAMETER, CursorKind.TEMPLATE_TEMPLATE_PARAMETER] for child in cursor.get_children()):
        return []
    else:
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = self._libclang_read_qualified_type(cursor.type)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
        except Warning as warning:
            warnings.warn(str(warning) + ' for variable \'' + spelling + '\'', warning.__class__)
            return []
        else:
            self._nodes[spelling] = dict(proxy=VariableProxy)
            filename = str(path(str(cursor.location.file)).abspath())
            self.add_file(filename, language=self._language)
            self._nodes[spelling]['_header'] = filename
            self._nodes[spelling]['cursor'] = cursor
            self._syntax_edges[scope].append(spelling)
            return [spelling]

AbstractSemanticGraph._libclang_read_variable = _libclang_read_variable
del _libclang_read_variable

def _libclang_read_function(self, cursor, scope):
    if not scope.endswith('::'):
        spelling = scope + "::" + cursor.spelling
    else:
        spelling = scope + cursor.spelling
    if cursor.kind in [CursorKind.DESTRUCTOR, CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR] and cursor.lexical_parent.kind is CursorKind.NAMESPACE:
        return []
    else:
        if not cursor.kind is CursorKind.DESTRUCTOR:
            spelling = spelling + '::' + str(uuid.uuid4())
        if cursor.kind is CursorKind.FUNCTION_DECL:
            self._nodes[spelling] = dict(proxy=FunctionProxy, cursor=cursor)
            if not cursor.location is None:
                filename = str(path(str(cursor.location.file)).abspath())
                self.add_file(filename, language=self._language)
                self._nodes[spelling]['_header'] = filename
        elif cursor.kind is CursorKind.CXX_METHOD:
            self._nodes[spelling] = dict(proxy=MethodProxy,
                    is_static=cursor.is_static_method(),
                    is_virtual=True,
                    is_const=False,
                    is_pure_virtual=True,
                    cursor=cursor)
        elif cursor.kind is CursorKind.CONSTRUCTOR:
            self._nodes[spelling] = dict(proxy=ConstructorProxy,
                    cursor=cursor)
        else:
            self._nodes[spelling] = dict(proxy=DestructorProxy,
                    is_virtual=True,
                    cursor=cursor)
        self._syntax_edges[spelling] = []
        self._syntax_edges[scope].append(spelling)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                if cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
                    target, specifiers = self._libclang_read_qualified_type(cursor.result_type)
                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                for index, child in enumerate([child for child in cursor.get_children() if child.kind is CursorKind.PARM_DECL]):
                    childspelling = spelling + '::' + child.spelling
                    if childspelling.endswith('::'):
                        childspelling += 'parm_' + str(index)
                    target, specifiers = self._libclang_read_qualified_type(child.type)
                    self._type_edges[childspelling] = dict(target=target, specifiers=specifiers)
                    self._nodes[childspelling] = dict(proxy=VariableProxy)
                    self._syntax_edges[spelling].append(childspelling)
        except Warning as warning:
            self._syntax_edges[scope].remove(spelling)
            self._syntax_edges.pop(spelling)
            self._type_edges.pop(spelling, None)
            self._nodes.pop(spelling)
            for index, child in enumerate([child for child in cursor.get_children() if child.kind is CursorKind.PARM_DECL]):
                childspelling = spelling + '::' + child.spelling
                if childspelling.endswith('::'):
                    childspelling += 'parm_' + str(index)
                self._nodes.pop(childspelling, None)
                self._type_edges.pop(childspelling, None)
            warnings.warn(str(warning), warning.__class__)
            return []
        else:
            return [spelling]

AbstractSemanticGraph._libclang_read_function = _libclang_read_function
del _libclang_read_function

def _libclang_read_field(self, cursor, scope):
    if cursor.spelling == '':
        # TODO warning
        return []
    else:
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        self._nodes[spelling] = dict(proxy=FieldProxy,
                is_mutable=False,
                is_static=False,
                cursor=cursor)
        self._syntax_edges[scope].append(spelling)
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = self._libclang_read_qualified_type(cursor.type)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
        except Exception as error:
            self._syntax_edges[scope].remove(spelling)
            self._nodes.pop(spelling)
            warnings.warn(str(error))
            return []
        else:
            return [spelling]

AbstractSemanticGraph._libclang_read_field = _libclang_read_field
del _libclang_read_field

def _libclang_read_tag(self, cursor, scope):
    if cursor.kind is CursorKind.ENUM_DECL:
        return self._libclang_read_enum(cursor, scope)
    else:
        if cursor.spelling == '':
            warnings.warn('Anonymous struc/union/class in scope \'' + scope + '\' not read')
            return []
        elif not cursor.spelling == cursor.displayname:
            warnings.warn('Class template specialization \'' + scope + '::' + cursor.displayname + '\' not read')
            return []
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        #if cursor.kind is CursorKind.STRUCT_DECL:
        #    spelling = 'struct ' + spelling
        #elif cursor.kind is CursorKind.UNION_DECL:
        #    spelling = 'union ' + spelling
        #else:
        #    spelling = 'class ' + spelling
        if not spelling in self:
            if cursor.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
                self._nodes[spelling] = dict(proxy=ClassProxy,
                        default_access='public',
                        is_abstract=True,
                        _is_copyable=False,
                        is_complete=False)
            elif cursor.kind is CursorKind.CLASS_DECL:
                self._nodes[spelling] = dict(proxy=ClassProxy,
                            default_access='private',
                            is_abstract=True,
                            _is_copyable=False,
                            is_complete=False)
            self._syntax_edges[spelling] = []
            self._base_edges[spelling] = []
            self._syntax_edges[scope].append(spelling)
        elif not self[spelling].is_complete:
            self._syntax_edges[scope].remove(spelling)
            self._syntax_edges[scope].append(spelling)
        if not self[spelling].is_complete:
            for child in cursor.get_children():
                if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                    childspelling = '::' + child.type.spelling
                    # TODO
                    if childspelling in self:
                        access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                        self._base_edges[spelling].append(dict(base=self[childspelling].node,
                            access=access,
                            is_virtual=False))
                    else:
                        warnings.warn('Base not found')
                else:
                    for childspelling in self._libclang_read_cursor(child, spelling):
                        self._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                        dict.pop(self._nodes[childspelling], "_header", None)
            self._nodes[spelling]['is_complete'] = len(self._base_edges[spelling]) + len(self._syntax_edges[spelling]) > 0
            if self[spelling].is_complete:
                filename = str(path(str(cursor.location.file)).abspath())
                self.add_file(filename, language=self._language)
                self._nodes[spelling]['_header'] = filename
                self._nodes[spelling]['cursor'] = cursor
        return [spelling]

AbstractSemanticGraph._libclang_read_tag = _libclang_read_tag
del _libclang_read_tag

def _libclang_read_namespace(self, cursor, scope):
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        if cursor.spelling == '':
            children = []
            if not spelling == '::':
                spelling = spelling[:-2]
            for child in cursor.get_children():
                children.extend(self._libclang_read_cursor(child, spelling))
            return children
        else:
            if not spelling in self:
                self._nodes[spelling] = dict(proxy=NamespaceProxy)
                self._syntax_edges[spelling] = []
            if not spelling in self._syntax_edges[scope]:
                self._syntax_edges[scope].append(spelling)
            for child in cursor.get_children():
                self._libclang_read_cursor(child, spelling)
            return [spelling]

AbstractSemanticGraph._libclang_read_namespace = _libclang_read_namespace
del _libclang_read_namespace

def _libclang_read_cursor(self, cursor, scope):
    if cursor.kind is CursorKind.UNEXPOSED_DECL:
        if cursor.spelling == '':
            children = []
            for child in cursor.get_children():
                children.extend(self._libclang_read_cursor(child, scope))
            return children
        else:
            warnings.warn('Named unexposed cursor not read')
            return []
    elif cursor.kind is CursorKind.TYPEDEF_DECL:
        return self._libclang_read_typedef(cursor, scope)
    elif cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL]:
        return self._libclang_read_variable(cursor, scope)
    elif cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
            CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
        return self._libclang_read_function(cursor, scope)
    elif cursor.kind is CursorKind.FIELD_DECL:
        return self._libclang_read_field(cursor, scope)
    elif cursor.kind in [CursorKind.ENUM_DECL, CursorKind.STRUCT_DECL,
            CursorKind.UNION_DECL, CursorKind.CLASS_DECL]:
        return self._libclang_read_tag(cursor, scope)
    elif cursor.kind is CursorKind.NAMESPACE:
        return self._libclang_read_namespace(cursor, scope)
    elif cursor.kind in [CursorKind.NAMESPACE_ALIAS, CursorKind.FUNCTION_TEMPLATE,
            CursorKind.USING_DECLARATION, CursorKind.USING_DIRECTIVE,
            CursorKind.UNEXPOSED_ATTR, CursorKind.CLASS_TEMPLATE,
            CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
            CursorKind.CXX_ACCESS_SPEC_DECL, CursorKind.CONVERSION_FUNCTION]:
        return []
    else:
        warnings.warn('Undefined behaviour for \'' + str(cursor.kind) + '\' cursor')
        return []

AbstractSemanticGraph._libclang_read_cursor = _libclang_read_cursor
del _libclang_read_cursor

def _libclang_read_cursor(self, cursor):
    self._node += 1
    node = self._node
    self._nodes[node] = cursor
    self._children[node] = []
    for child in cursor.get_children():
        self._children[node].append(self._libclang_read_cursor(child))
    return node

AbstractSyntaxTree._libclang_read_cursor = _libclang_read_cursor
del _libclang_read_cursor

def create(cls, tu):
    self = AbstractSyntaxTree()
    self.node = 0
    node = self.node
    self._nodes[node] = tu.cursor
    self._children[node] = []
    self.node += 1
    for child in tu.cursor.get_children():
        self._children[node].append(self._libclang_read_cursor(child))
    del self.node
    return self

AbstractSyntaxTree.create = classmethod(create)
del create

def _libclang_read_cursor(self, cursor):
    node = self._node
    self._nodes[node] = cursor
    self._children[node] = []
    self._node += 1
    for child in cursor.get_children():
        self._children[node].append(self._libclang_read_cursor(child))
    return node

AbstractSyntaxTree._libclang_read_cursor = _libclang_read_cursor
del _libclang_read_cursor
