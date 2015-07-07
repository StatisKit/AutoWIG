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

__all__ = []

def set_libclang_front_end(filepath=None, dirpath=None):
    if not Config.loaded:
        if not dirpath is None:
            Config.set_library_path(dirpath)
        elif not filepath is None:
            Config.set_library_file(filepath)
        else:
            raise IOError('cannot set libclang path or file')

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

    def _front_end(self, content, flags, ersatz=False):
        index = Index.create()
        tempfilehandler = NamedTemporaryFile(delete=False)
        tempfilehandler.write(content)
        tempfilehandler.close()
        tu = index.parse(tempfilehandler.name, args=flags, unsaved_files=None, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        os.unlink(tempfilehandler.name)
        if ersatz:
            ast = AbstractSyntaxTree.create(tu)
        self._read_translation_unit(tu)
        if ersatz:
            return ast

    AbstractSemanticGraph._front_end = _front_end
    del _front_end

    def _read_translation_unit(self, tu):
        for child in tu.cursor.get_children():
            self._read_cursor(child, '::')

    AbstractSemanticGraph._read_translation_unit = _read_translation_unit
    del _read_translation_unit

    def _read_qualified_type(self, qtype):
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
                    return self[spelling].id, specifiers
                except:
                    warnings.warn('record not found')
                    break
            else:
                target, _specifiers = self._read_builtin_type(qtype)
                return target, _specifiers + specifiers

    AbstractSemanticGraph._read_qualified_type = _read_qualified_type
    del _read_qualified_type

    def _read_builtin_type(self, btype):
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

    AbstractSemanticGraph._read_builtin_type = _read_builtin_type
    del _read_builtin_type

    def _read_enum(self, cursor, scope):
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
                    children.extend(self._read_enum_constant(child, spelling))
                    decls.append(child)
            filename = str(path(str(cursor.location.file)).abspath())
            self.add_file(filename, language=self._language)
            for childspelling, child in zip(children, decls):
                self._nodes[childspelling]['_header'] = filename
                self._nodes[spelling]['cursor'] = child
            return children
        else:
            spelling = 'enum ' + spelling
            if not spelling in self._nodes :
                self._syntax_edges[spelling] = []
                self._nodes[spelling] = dict(proxy=EnumProxy)
                self._syntax_edges[scope].append(spelling)
            elif not self[spelling].is_complete:
                self._syntax_edges[scope].remove(spelling)
                self._syntax_edges[scope].append(spelling)
            if not self[spelling].is_complete:
                for child in cursor.get_children():
                    self._read_enum_constant(child, spelling)
            if self[spelling].is_complete:
                filename = str(path(str(cursor.location.file)).abspath())
                self.add_file(filename, language=self._language)
                self._nodes[spelling]['_header'] = filename
                self._nodes[spelling]['cursor'] = cursor
            return [spelling]

    AbstractSemanticGraph._read_enum = _read_enum
    del _read_enum

    def _read_enum_constant(self, cursor, scope):
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        spelling = spelling.replace('enum ', '')
        self._nodes[spelling] = dict(proxy=EnumConstantProxy)
        self._syntax_edges[scope].append(spelling)
        return [spelling]

    AbstractSemanticGraph._read_enum_constant = _read_enum_constant
    del _read_enum_constant

    def _read_typedef(self, typedef, scope):
        if not scope.endswith('::'):
            spelling = scope + "::" + typedef.spelling
        else:
            spelling = scope + typedef.spelling
        if not spelling in self._nodes:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    target, specifiers = self._read_qualified_type(typedef.underlying_typedef_type)
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

    AbstractSemanticGraph._read_typedef = _read_typedef
    del _read_typedef

    def _read_variable(self, cursor, scope):
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
                    target, specifiers = self._read_qualified_type(cursor.type)
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

    AbstractSemanticGraph._read_variable = _read_variable
    del _read_variable

    def _read_function(self, cursor, scope):
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
                    for child in cursor.get_children():
                        if child.kind is CursorKind.PARM_DECL:
                            self._read_variable(child, spelling)
                    if not cursor.kind in [CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:
                        target, specifiers = self._read_qualified_type(cursor.result_type)
                        self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Warning as warning:
                self._syntax_edges[scope].remove(spelling)
                self._syntax_edges.pop(spelling)
                self._nodes.pop(spelling)
                if not spelling.endswith('::'):
                    spelling += '::'
                for child in cursor.get_children():
                    if child.kind is CursorKind.PARM_DECL:
                        self._nodes.pop(spelling + child.spelling, None)
                        self._syntax_edges.pop(spelling + child.spelling, None)
                        self._type_edges.pop(spelling, None)
                warnings.warn(str(warning), warning.__class__)
                return []
            else:
                return [spelling]

    AbstractSemanticGraph._read_function = _read_function
    del _read_function

    def _read_field(self, cursor, scope):
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
                target, specifiers = self._read_qualified_type(cursor.type)
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
        except Exception as error:
            self._syntax_edges[scope].remove(spelling)
            self._nodes.pop(spelling)
            warnings.warn(str(error))
            return []
        else:
            return [spelling]

    AbstractSemanticGraph._read_field = _read_field
    del _read_field

    def _read_tag(self, cursor, scope):
        if cursor.kind is CursorKind.ENUM_DECL:
            return self._read_enum(cursor, scope)
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
            if not spelling in self._nodes:
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
                        if childspelling in self._nodes:
                            access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                            self._base_edges[spelling].append(dict(base=self[childspelling].id,
                                access=access,
                                is_virtual=False))
                        else:
                            warnings.warn('Base not found')
                    else:
                        for childspelling in self._read_cursor(child, spelling):
                            self._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                            dict.pop(self._nodes[childspelling], "_header", None)
                self._nodes[spelling]['is_complete'] = len(self._base_edges[spelling]) + len(self._syntax_edges[spelling]) > 0
                if self[spelling].is_complete:
                    filename = str(path(str(cursor.location.file)).abspath())
                    self.add_file(filename, language=self._language)
                    self._nodes[spelling]['_header'] = filename
                    self._nodes[spelling]['cursor'] = cursor
            return [spelling]

    AbstractSemanticGraph._read_tag = _read_tag
    del _read_tag

    def _read_namespace(self, cursor, scope):
            if not scope.endswith('::'):
                spelling = scope + "::" + cursor.spelling
            else:
                spelling = scope + cursor.spelling
            if cursor.spelling == '':
                children = []
                if not spelling == '::':
                    spelling = spelling[:-2]
                with warnings.catch_warnings():
                    warnings.simplefilter('always')
                    for child in cursor.get_children():
                        children.extend(self._read_cursor(child, spelling))
                return children
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(proxy=NamespaceProxy)
                    self._syntax_edges[spelling] = []
                if not spelling in self._syntax_edges[scope]:
                    self._syntax_edges[scope].append(spelling)
                with warnings.catch_warnings():
                    warnings.simplefilter('always')
                    for child in cursor.get_children():
                        self._read_cursor(child, spelling)
                return [spelling]

    AbstractSemanticGraph._read_namespace = _read_namespace
    del _read_namespace

    def _read_cursor(self, cursor, scope):
        if cursor.kind is CursorKind.UNEXPOSED_DECL:
            if cursor.spelling == '':
                children = []
                for child in cursor.get_children():
                    children.extend(self._read_cursor(child, scope))
                return children
            else:
                warnings.warn('Named unexposed cursor not read')
                return []
        elif cursor.kind is CursorKind.TYPEDEF_DECL:
            return self._read_typedef(cursor, scope)
        elif cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL]:
            return self._read_variable(cursor, scope)
        elif cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
                CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
            return self._read_function(cursor, scope)
        elif cursor.kind is CursorKind.FIELD_DECL:
            return self._read_field(cursor, scope)
        elif cursor.kind in [CursorKind.ENUM_DECL, CursorKind.STRUCT_DECL,
                CursorKind.UNION_DECL, CursorKind.CLASS_DECL]:
            return self._read_tag(cursor, scope)
        elif cursor.kind is CursorKind.NAMESPACE:
            return self._read_namespace(cursor, scope)
        elif cursor.kind in [CursorKind.NAMESPACE_ALIAS, CursorKind.FUNCTION_TEMPLATE,
                CursorKind.USING_DECLARATION, CursorKind.USING_DIRECTIVE,
                CursorKind.UNEXPOSED_ATTR, CursorKind.CLASS_TEMPLATE,
                CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
                CursorKind.CXX_ACCESS_SPEC_DECL, CursorKind.CONVERSION_FUNCTION]:
            return []
        else:
            warnings.warn('Undefined behaviour for \'' + str(cursor.kind) + '\' cursor')
            return []

    AbstractSemanticGraph._read_cursor = _read_cursor
    del _read_cursor

    def create(cls, tu):
        self = AbstractSyntaxTree()
        self._node = 0
        node = self._node
        self._nodes[node] = tu.cursor
        self._children[node] = []
        self._node += 1
        for child in tu.cursor.get_children():
            self._children[node].append(self._read_cursor(child))
        del self._node
        return self

    AbstractSyntaxTree.create = classmethod(create)
    del create

    def _read_cursor(self, cursor):
        node = self._node
        self._nodes[node] = cursor
        self._children[node] = []
        self._node += 1
        for child in cursor.get_children():
            self._children[node].append(self._read_cursor(child))
        return node

    AbstractSyntaxTree._read_cursor = _read_cursor
    del _read_cursor
