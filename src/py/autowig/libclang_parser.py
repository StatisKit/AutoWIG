"""
"""

from path import path
from clang.cindex import Config, conf, Cursor, Index, TranslationUnit, CursorKind, TypeKind
from tempfile import NamedTemporaryFile
import os
import warnings
import uuid

from .asg import CharTypeProxy, \
                 UnsignedCharTypeProxy, \
                 SignedCharTypeProxy, \
                 Char16TypeProxy, \
                 Char32TypeProxy, \
                 WCharTypeProxy, \
                 SignedShortIntegerTypeProxy, \
                 SignedIntegerTypeProxy, \
                 SignedLongIntegerTypeProxy, \
                 SignedLongLongIntegerTypeProxy, \
                 UnsignedShortIntegerTypeProxy, \
                 UnsignedIntegerTypeProxy, \
                 UnsignedLongIntegerTypeProxy, \
                 UnsignedLongLongIntegerTypeProxy, \
                 SignedFloatTypeProxy, \
                 SignedDoubleTypeProxy, \
                 SignedLongDoubleTypeProxy, \
                 BoolTypeProxy, \
                 
from .parser import preprocessing

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

def libclang_parser(asg, filepaths, flags, libpath=None, silent=False, cache=None, force=False, **kwargs):
    warnings.warn('The libclang parser is no more maintened', DeprecationWarning)
    content = preprocessing(asg, filepaths, flags, cache, force)
    if content:
        if not libpath is None:
            if Config.loaded:
                warnings.warn('\'libpath\' parameter not used since libclang config is already loaded', SyntaxWarning)
            else:
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
        with warnings.catch_warnings():
            if silent:
                warnings.simplefilter('ignore')
            else:
                warnings.simplefilter('always')
            read_translation_unit(asg, tu)
    #postprocessing(asg, filepaths, cache=cache, **kwargs)

def read_translation_unit(asg, tu):
    for child in tu.cursor.get_children():
        read_cursor(asg, child, '::')

#def read_translation_unit(asg, tu):
#    _nodes = dict()
#    _children = dict()
#    _nodes[0] = tu.cursor
#    asg._children[0] = []
#    asg._node = 1
#    for child in tu.cursor.get_children():
#        asg._children[0].append(read_cursor(child))
#    del asg._node

def read_qualified_type(asg, qtype):
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
            if cursor.kind is CursorKind.TYPEDEF_DECL:
                qtype = cursor.underlying_typedef_type
            else:
                spelling = '::' + cursor.type.spelling
                if cursor.kind is CursorKind.ENUM_DECL:
                    spelling = 'enum ' + spelling
                if qtype.is_const_qualified():
                    specifiers = ' const' + specifiers
                if qtype.is_volatile_qualified():
                    specifiers = ' volatile' + specifiers
                try:
                    return asg[spelling].node, specifiers
                except:
                    warnings.warn('record not found')
                    break
        else:
            target, _specifiers = read_builtin_type(asg, qtype)
            return target, _specifiers + specifiers

def read_builtin_type(asg, btype):
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
        warnings.warn('\'' + str(btype.kind) + '\'', Warning)

def read_enum(asg, cursor, scope):
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
                children.extend(read_enum_constant(asg, child, spelling))
                decls.append(child)
        filename = str(path(str(cursor.location.file)).abspath())
        asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
        for childspelling, child in zip(children, decls):
            asg._nodes[childspelling]['_header'] = filename
            asg._nodes[spelling]['cursor'] = child
        return children
    else:
        spelling = 'enum ' + spelling
        if not spelling in asg:
            asg._syntax_edges[spelling] = []
            asg._nodes[spelling] = dict(proxy=EnumerationProxy)
            asg._syntax_edges[scope].append(spelling)
        elif not asg[spelling].is_complete:
            asg._syntax_edges[scope].remove(spelling)
            asg._syntax_edges[scope].append(spelling)
        if not asg[spelling].is_complete:
            for child in cursor.get_children():
                read_enum_constant(asg, child, spelling)
        if asg[spelling].is_complete:
            filename = str(path(str(cursor.location.file)).abspath())
            asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
            asg._nodes[spelling]['_header'] = filename
            asg._nodes[spelling]['cursor'] = cursor
        return [spelling]

def read_enum_constant(asg, cursor, scope):
    if not scope.endswith('::'):
        spelling = scope + "::" + cursor.spelling
    else:
        spelling = scope + cursor.spelling
    spelling = spelling.replace('enum ', '')
    asg._nodes[spelling] = dict(proxy=EnumeratorProxy)
    asg._syntax_edges[scope].append(spelling)
    return [spelling]

def read_typedef(asg, typedef, scope):
    if not scope.endswith('::'):
        spelling = scope + "::" + typedef.spelling
    else:
        spelling = scope + typedef.spelling
    if not spelling in asg:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                target, specifiers = read_qualified_type(asg, typedef.underlying_typedef_type)
        except Warning as warning:
            warnings.warn(str(warning) + ' for typedef \'' + spelling + '\'', warning.__class__)
            return []
        else:
            asg._nodes[spelling] = dict(proxy=TypedefProxy)
            asg._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            asg._syntax_edges[scope].append(spelling)
            filename = str(path(str(typedef.location.file)).abspath())
            asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
            asg._nodes[spelling]['_header'] = filename
            return [spelling]
    else:
        return [spelling]

def read_variable(asg, cursor, scope):
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
                target, specifiers = read_qualified_type(asg, cursor.type)
                asg._type_edges[spelling] = dict(target=target, specifiers=specifiers)
        except Warning as warning:
            warnings.warn(str(warning) + ' for variable \'' + spelling + '\'', warning.__class__)
            return []
        else:
            asg._nodes[spelling] = dict(proxy=VariableProxy)
            filename = str(path(str(cursor.location.file)).abspath())
            asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
            asg._nodes[spelling]['_header'] = filename
            asg._nodes[spelling]['cursor'] = cursor
            asg._syntax_edges[scope].append(spelling)
            return [spelling]

def read_function(asg, cursor, scope):
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
            asg._nodes[spelling] = dict(proxy=FunctionProxy, cursor=cursor)
            if not cursor.location is None:
                filename = str(path(str(cursor.location.file)).abspath())
                asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
                asg._nodes[spelling]['_header'] = filename
        elif cursor.kind is CursorKind.CXX_METHOD:
            asg._nodes[spelling] = dict(proxy=MethodProxy,
                    is_static=cursor.is_static_method(),
                    is_virtual=True,
                    is_const=False,
                    is_pure=True,
                    cursor=cursor)
        elif cursor.kind is CursorKind.CONSTRUCTOR:
            asg._nodes[spelling] = dict(proxy=ConstructorProxy,
                    cursor=cursor)
        else:
            asg._nodes[spelling] = dict(proxy=DestructorProxy,
                    is_virtual=True,
                    cursor=cursor)
        asg._parameter_edges[spelling] = []
        asg._syntax_edges[scope].append(spelling)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                if cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
                    target, specifiers = read_qualified_type(asg, cursor.result_type)
                    asg._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                for index, child in enumerate([child for child in cursor.get_children() if child.kind is CursorKind.PARM_DECL]):
                    #childspelling = spelling + '::' + child.spelling
                    #if childspelling.endswith('::'):
                    #    childspelling += 'parm_' + str(index)
                    target, specifiers = read_qualified_type(asg, child.type)
                    asg._parameter_edges[spelling].append(dict(name = child.spelling, target=target, specifiers=specifiers))
                    #asg._type_edges[childspelling] = dict(target=target, specifiers=specifiers)
                    #asg._nodes[childspelling] = dict(proxy=VariableProxy)
                    #asg._syntax_edges[spelling].append(childspelling)
        except Warning as warning:
            asg._syntax_edges[scope].remove(spelling)
            #asg._syntax_edges.pop(spelling)
            asg._type_edges.pop(spelling, None)
            asg._parameter_edges.pop(spelling, None)
            asg._nodes.pop(spelling)
            #for index, child in enumerate([child for child in cursor.get_children() if child.kind is CursorKind.PARM_DECL]):
            #    childspelling = spelling + '::' + child.spelling
            #    if childspelling.endswith('::'):
            #        childspelling += 'parm_' + str(index)
            #    asg._nodes.pop(childspelling, None)
            #    asg._type_edges.pop(childspelling, None)
            warnings.warn(str(warning), warning.__class__)
            return []
        else:
            return [spelling]

def read_field(asg, cursor, scope):
    if cursor.spelling == '':
        # TODO warning
        return []
    else:
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        asg._nodes[spelling] = dict(proxy=FieldProxy,
                is_mutable=False,
                is_static=False,
                cursor=cursor)
        asg._syntax_edges[scope].append(spelling)
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = read_qualified_type(asg, cursor.type)
                asg._type_edges[spelling] = dict(target=target, specifiers=specifiers)
        except Exception as error:
            asg._syntax_edges[scope].remove(spelling)
            asg._nodes.pop(spelling)
            warnings.warn(str(error))
            return []
        else:
            return [spelling]

def read_tag(asg, cursor, scope):
    if cursor.kind is CursorKind.ENUM_DECL:
        return read_enum(asg, cursor, scope)
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
        if not spelling in asg:
            if cursor.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
                asg._nodes[spelling] = dict(proxy=ClassProxy,
                        default_access='public',
                        is_abstract=True,
                        _is_copyable=False,
                        is_complete=False)
            elif cursor.kind is CursorKind.CLASS_DECL:
                asg._nodes[spelling] = dict(proxy=ClassProxy,
                            default_access='private',
                            is_abstract=True,
                            _is_copyable=False,
                            is_complete=False)
            asg._syntax_edges[spelling] = []
            asg._base_edges[spelling] = []
            asg._syntax_edges[scope].append(spelling)
        elif not asg[spelling].is_complete:
            asg._syntax_edges[scope].remove(spelling)
            asg._syntax_edges[scope].append(spelling)
        if not asg[spelling].is_complete:
            for child in cursor.get_children():
                if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                    childspelling = '::' + child.type.spelling
                    # TODO
                    if childspelling in asg:
                        access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                        asg._base_edges[spelling].append(dict(base=asg[childspelling].node,
                            access=access,
                            is_virtual=False))
                    else:
                        warnings.warn('Base not found')
                else:
                    for childspelling in read_cursor(asg, child, spelling):
                        asg._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                        dict.pop(asg._nodes[childspelling], "_header", None)
            asg._nodes[spelling]['is_complete'] = len(asg._base_edges[spelling]) + len(asg._syntax_edges[spelling]) > 0
            if asg[spelling].is_complete:
                filename = str(path(str(cursor.location.file)).abspath())
                asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
                asg._nodes[spelling]['_header'] = filename
                asg._nodes[spelling]['cursor'] = cursor
        return [spelling]

def read_namespace(asg, cursor, scope):
        if not scope.endswith('::'):
            spelling = scope + "::" + cursor.spelling
        else:
            spelling = scope + cursor.spelling
        if cursor.spelling == '':
            children = []
            if not spelling == '::':
                spelling = spelling[:-2]
            for child in cursor.get_children():
                children.extend(read_cursor(asg, child, spelling))
            return children
        else:
            if not spelling in asg:
                asg._nodes[spelling] = dict(proxy=NamespaceProxy)
                asg._syntax_edges[spelling] = []
            if not spelling in asg._syntax_edges[scope]:
                asg._syntax_edges[scope].append(spelling)
            for child in cursor.get_children():
                read_cursor(asg, child, spelling)
            return [spelling]

def read_cursor(asg, cursor, scope):
    if cursor.kind is CursorKind.UNEXPOSED_DECL:
        if cursor.spelling == '':
            children = []
            for child in cursor.get_children():
                children.extend(read_cursor(asg, child, scope))
            return children
        else:
            warnings.warn('Named unexposed cursor not read')
            return []
    elif cursor.kind is CursorKind.TYPEDEF_DECL:
        return read_typedef(asg, cursor, scope)
    elif cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL]:
        return read_variable(asg, cursor, scope)
    elif cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
            CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
        return read_function(asg, cursor, scope)
    elif cursor.kind is CursorKind.FIELD_DECL:
        return read_field(asg, cursor, scope)
    elif cursor.kind in [CursorKind.ENUM_DECL, CursorKind.STRUCT_DECL,
            CursorKind.UNION_DECL, CursorKind.CLASS_DECL]:
        return read_tag(asg, cursor, scope)
    elif cursor.kind is CursorKind.NAMESPACE:
        return read_namespace(asg, cursor, scope)
    elif cursor.kind in [CursorKind.NAMESPACE_ALIAS, CursorKind.FUNCTION_TEMPLATE,
            CursorKind.USING_DECLARATION, CursorKind.USING_DIRECTIVE,
            CursorKind.UNEXPOSED_ATTR, CursorKind.CLASS_TEMPLATE,
            CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
            CursorKind.CXX_ACCESS_SPEC_DECL, CursorKind.CONVERSION_FUNCTION]:
        return []
    else:
        warnings.warn('Undefined behaviour for \'' + str(cursor.kind) + '\' cursor')
        return []

#def read_cursor(asg, cursor):
#    asg._node += 1
#    node = asg._node
#    asg._nodes[node] = cursor
#    asg._children[node] = []
#    for child in cursor.get_children():
#        asg._children[node].append(asg._libclang_read_cursor(child))
#    return node
#
#AbstractSyntaxTree._libclang_read_cursor = _libclang_read_cursor
#del _libclang_read_cursor
#
#def create(cls, tu):
#    asg = AbstractSyntaxTree()
#    asg.node = 0
#    node = asg.node
#    asg._nodes[node] = tu.cursor
#    asg._children[node] = []
#    asg.node += 1
#    for child in tu.cursor.get_children():
#        asg._children[node].append(asg._libclang_read_cursor(child))
#    del asg.node
#    return asg
#
#AbstractSyntaxTree.create = classmethod(create)
#del create
#
#def _libclang_read_cursor(asg, cursor):
#    node = asg._node
#    asg._nodes[node] = cursor
#    asg._children[node] = []
#    asg._node += 1
#    for child in cursor.get_children():
#        asg._children[node].append(asg._libclang_read_cursor(child))
#    return node
#
#AbstractSyntaxTree._libclang_read_cursor = _libclang_read_cursor
#del _libclang_read_cursor
