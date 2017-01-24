##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (16)                       #
#                                                                                #
##################################################################################

"""
"""

from path import path
from clang.cindex import Config, conf, Cursor, Index, TranslationUnit, CursorKind, TypeKind, AccessSpecifier
import pickle
from tempfile import NamedTemporaryFile
import numpy
import os
import warnings
import uuid

from .asg import (CharTypeProxy, 
                 UnsignedCharTypeProxy,
                 SignedCharTypeProxy,
                 Char16TypeProxy,
                 Char32TypeProxy,
                 WCharTypeProxy,
                 SignedShortIntegerTypeProxy,
                 SignedIntegerTypeProxy,
                 SignedLongIntegerTypeProxy,
                 SignedLongLongIntegerTypeProxy,
                 UnsignedShortIntegerTypeProxy,
                 UnsignedIntegerTypeProxy,
                 UnsignedLongIntegerTypeProxy,
                 UnsignedLongLongIntegerTypeProxy,
                 SignedFloatTypeProxy,
                 SignedDoubleTypeProxy,
                 SignedLongDoubleTypeProxy,
                 BoolTypeProxy, 
                 ComplexTypeProxy,
                 VoidTypeProxy,
                 HeaderProxy,
                 EnumerationProxy,
                 EnumeratorProxy, 
                 TypedefProxy,
                 VariableProxy,
                 FunctionProxy,
                 MethodProxy,
                 ConstructorProxy,
                 DestructorProxy,
                 FieldProxy,
                 ClassProxy,
                 NamespaceProxy)
                 
                 
from ._parser import pre_processing, post_processing

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

def libclang_parser(asg, filepaths, flags, silent=False, **kwargs):
    warnings.warn('The libclang parser is no more maintened', DeprecationWarning)
    content = pre_processing(asg, filepaths, flags, **kwargs)
    if content:
        #         if libpath is not None:
        #             if Config.loaded:
        #                 warnings.warn('\'libpath\' parameter not used since libclang config is already loaded', SyntaxWarning)
        #             else:
        #                 libpath = path(libpath)
        #                 libpath = libpath.abspath()
        #                 if not libpath.exists():
        #                     raise ValueError('\'libpath\' parameter: \'' + str(libpath) + '\' doesn\'t exists')
        #                 if libpath.isdir():
        #                     Config.set_library_path(str(libpath))
        #                 elif libpath.isfile():
        #                     Config.set_library_file(str(libpath))
        #                 else:
        #                     raise ValueError('\'libpath\' parameter: should be a path to a directory or a file')
        #         else:
        #             if not Config.loaded:
        #                 import sys
        #                 Config.set_library_path(os.path.join(sys.prefix, 'lib'))
        #                 #raise ValueError('\'libpath\' parameter: should not be set to \'None\'')
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
    for node in asg._syntax_edges.keys():
        asg._syntax_edges[node] = list(set(asg._syntax_edges[node]))
    post_processing(asg, flags, **kwargs)
    filehandler = NamedTemporaryFile(delete=False)
    pickle.dump(asg, filehandler, 0)
    filehandler.close()
    with open(filehandler.name, 'r') as filehandler:
        _asg = filehandler.read()
        for fct in asg.functions():
            _asg.replace(fct._node,  fct.globalname + '::' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.prototype)))
        for cls in asg.classes():
            for ctr in cls.constructors():
                _asg.replace(ctr._node,  ctr.globalname + '::' + str(uuid.uuid5(uuid.NAMESPACE_X500, ctr.prototype)))
    with open(filehandler.name, 'w') as filehandler:
        filehandler.write(_asg)
    with open(filehandler.name, 'r') as filehandler:
        asg = pickle.load(filehandler)
    for node, edges in asg._syntax_edges.items():
        if edges:
            asg._syntax_edges[node] = numpy.unique(edges).tolist()
    os.unlink(filehandler.name)
    return asg

def read_access(asg, access, *args):
    if access is AccessSpecifier.PUBLIC:
        for arg in args:
            asg._nodes[arg]['_access'] = 'public'
    elif access is AccessSpecifier.PROTECTED:
        for arg in args:
            asg._nodes[arg]['_access'] = 'protected'
    elif access is AccessSpecifier.PRIVATE:
        for arg in args:
            asg._nodes[arg]['_access'] = 'private'

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
        if qtype.is_const_qualified() and not specifiers.startswith(' const'):
            specifiers = ' const' + specifiers
        if qtype.is_volatile_qualified() and not specifiers.startswith(' volatile'):
            specifiers = ' volatile' + specifiers
        if qtype.kind is TypeKind.POINTER:
            specifiers = ' *' + specifiers
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
                elif cursor.kind is CursorKind.STRUCT_DECL:
                    spelling = 'struct ' + spelling
                elif cursor.kind is CursorKind.UNION_DECL:
                    spelling = 'union ' + spelling
                elif cursor.kind is CursorKind.CLASS_DECL:
                    spelling = 'class ' + spelling
                try:
                    if spelling == '::':
                        raise Exception
                    return asg[spelling]._node, specifiers
                except:
                    warnings.warn('record not found')
        else:
            target = read_builtin_type(asg, qtype)
            return target, specifiers

def read_builtin_type(asg, btype):
    if btype.kind in [TypeKind.CHAR_U, TypeKind.CHAR_S]:
        return CharTypeProxy._node
    elif btype.kind is TypeKind.UCHAR:
        return UnsignedCharTypeProxy._node
    elif btype.kind is TypeKind.SCHAR:
        return SignedCharTypeProxy._node
    elif btype.kind is TypeKind.CHAR16:
        return Char16TypeProxy._node
    elif btype.kind is TypeKind.CHAR32:
        return Char32TypeProxy._node
    elif btype.kind is TypeKind.WCHAR:
        return WCharTypeProxy._node
    elif btype.kind is TypeKind.SHORT:
        return SignedShortIntegerTypeProxy._node
    elif btype.kind is TypeKind.INT:
        return SignedIntegerTypeProxy._node
    elif btype.kind is TypeKind.LONG:
        return SignedLongIntegerTypeProxy._node
    elif btype.kind is TypeKind.LONGLONG:
        return SignedLongLongIntegerTypeProxy._node
    elif btype.kind is TypeKind.USHORT:
        return UnsignedShortIntegerTypeProxy._node
    elif btype.kind is TypeKind.UINT:
        return UnsignedIntegerTypeProxy._node
    elif btype.kind is TypeKind.ULONG:
        return UnsignedLongIntegerTypeProxy._node
    elif btype.kind is TypeKind.ULONGLONG:
        return UnsignedLongLongIntegerTypeProxy._node
    elif btype.kind is TypeKind.FLOAT:
        return SignedFloatTypeProxy._node
    elif btype.kind is TypeKind.DOUBLE:
        return SignedDoubleTypeProxy._node
    elif btype.kind is TypeKind.LONGDOUBLE:
        return SignedLongDoubleTypeProxy._node
    elif btype.kind is TypeKind.BOOL:
        return BoolTypeProxy._node
    elif btype.kind is TypeKind.COMPLEX:
        return ComplexTypeProxy._node
    elif btype.kind is TypeKind.VOID:
        return VoidTypeProxy._node
    else:
        warnings.warn('\'' + str(btype.kind) + '\'', Warning)

def read_enum(asg, cursor, scope):
    spelling = scope
    if spelling.startswith('class '):
        spelling = spelling[6:]
    elif spelling.startswith('struct '):
        spelling = spelling[7:]
    if not scope.endswith('::'):
        spelling = spelling + "::" + cursor.spelling
    else:
        spelling = spelling + cursor.spelling
    if cursor.spelling == '':
        children = []
        decls = []
        #if not spelling == '::':
        #    spelling = spelling[:-2]
        spelling = scope
        for child in cursor.get_children():
            if child.kind is CursorKind.ENUM_CONSTANT_DECL:
                children.extend(read_enum_constant(asg, child, spelling))
                decls.append(child)
        filename = str(path(str(cursor.location.file)).abspath())
        asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
        for childspelling, child in zip(children, decls):
            asg._nodes[childspelling]['_header'] = filename
        read_access(asg, cursor.access_specifier, *children)
        return children
    else:
        spelling = 'enum ' + spelling
        if spelling not in asg:
            asg._syntax_edges[spelling] = []
            asg._nodes[spelling] = dict(_proxy = EnumerationProxy,
                                        _comment = "",
                                        _is_scoped = False) # TODO
            read_access(asg, cursor.access_specifier, spelling)
            asg._syntax_edges[scope].append(spelling)
        elif not asg[spelling].is_complete:
            asg._syntax_edges[scope].remove(spelling)
            asg._syntax_edges[scope].append(spelling)
        if not asg[spelling].is_complete:
            read_access(asg, cursor.access_specifier, spelling)
            for child in cursor.get_children():
                read_enum_constant(asg, child, spelling)
        if asg[spelling].is_complete:
            filename = str(path(str(cursor.location.file)).abspath())
            asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
            asg._nodes[spelling]['_header'] = filename
        return [spelling]

def read_enum_constant(asg, cursor, scope):
    spelling = scope
    if spelling.startswith('enum '):
        spelling = spelling[5:]
    elif spelling.startswith('class '):
        spelling = spelling[6:]
    elif spelling.startswith('struct '):
        spelling = spelling[7:]
    if not scope.endswith('::'):
        spelling = spelling + "::" + cursor.spelling
    else:
        spelling = spelling + cursor.spelling
    asg._nodes[spelling] = dict(_proxy=EnumeratorProxy)
    asg._syntax_edges[scope].append(spelling)
    return [spelling]

def read_typedef(asg, typedef, scope):
    spelling = scope
    if spelling.startswith('class '):
        spelling = spelling[6:]
    elif spelling.startswith('union '):
        spelling = spelling[6:]
    elif spelling.startswith('struct '):
        spelling = spelling[7:]
    if not scope.endswith('::'):
        spelling = spelling + "::" + typedef.spelling
    else:
        spelling = spelling + typedef.spelling
    if spelling not in asg:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                target, specifiers = read_qualified_type(asg, typedef.underlying_typedef_type)
        except Warning as warning:
            warnings.warn(str(warning) + ' for typedef \'' + spelling + '\'', warning.__class__)
            return []
        else:
            asg._nodes[spelling] = dict(_proxy=TypedefProxy)
            asg._type_edges[spelling] = dict(target=target, qualifiers=specifiers)
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
        spelling = scope
        if spelling.startswith('class '):
            spelling = spelling[6:]
        elif spelling.startswith('union '):
            spelling = spelling[6:]
        elif spelling.startswith('struct '):
            spelling = spelling[7:]
        if not scope.endswith('::'):
            spelling = spelling + "::" + cursor.spelling
        else:
            spelling = spelling + cursor.spelling
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = read_qualified_type(asg, cursor.type)
                asg._type_edges[spelling] = dict(target=target, qualifiers=specifiers)
        except Warning as warning:
            warnings.warn(str(warning) + ' for variable \'' + spelling + '\'', warning.__class__)
            return []
        else:
            if isinstance(asg[scope], ClassProxy):
                asg._nodes[spelling] = dict(_proxy=FieldProxy,
                                            _is_mutable=False,
                                            _is_static=True,
                                            _is_bit_field=False)
            else:
                asg._nodes[spelling] = dict(_proxy=VariableProxy)
            filename = str(path(str(cursor.location.file)).abspath())
            asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
            read_access(asg, cursor.access_specifier, spelling)
            asg._nodes[spelling]['_header'] = filename
            asg._syntax_edges[scope].append(spelling)
            return [spelling]

def read_function(asg, cursor, scope):
    spelling = scope
    if spelling.startswith('class '):
        spelling = spelling[6:]
    elif spelling.startswith('union '):
        spelling = spelling[6:]
    elif spelling.startswith('struct '):
        spelling = spelling[7:]
    if not scope.endswith('::'):
        spelling = spelling + "::" + cursor.spelling
    else:
        spelling = spelling + cursor.spelling
    if cursor.kind in [CursorKind.DESTRUCTOR, CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR] and cursor.lexical_parent.kind is CursorKind.NAMESPACE:
        return []
    else:
        if cursor.kind is not CursorKind.DESTRUCTOR:
            spelling = spelling + '::' + str(uuid.uuid4())
        if cursor.kind is CursorKind.FUNCTION_DECL:
            asg._nodes[spelling] = dict(_proxy=FunctionProxy,
                                        _comment="")
            if cursor.location is not None:
                filename = str(path(str(cursor.location.file)).abspath())
                asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
                asg._nodes[spelling]['_header'] = filename
        elif cursor.kind is CursorKind.CXX_METHOD:
            asg._nodes[spelling] = dict(_proxy=MethodProxy,
                    _is_static=cursor.is_static_method(),
                    _is_volatile=False,
                    _is_virtual=True,
                    _is_const=cursor.is_const_method(),
                    _is_pure=True,
                    _comment="")
        elif cursor.kind is CursorKind.CONSTRUCTOR:
            asg._nodes[spelling] = dict(_proxy=ConstructorProxy,
                     _is_virtual=False, #TODO
                     _comment="")
        else:
            asg._nodes[spelling] = dict(_proxy=DestructorProxy,
                    is_virtual=True,
                    _comment="")
        asg._parameter_edges[spelling] = []
        asg._syntax_edges[scope].append(spelling)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                if cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
                    target, specifiers = read_qualified_type(asg, cursor.result_type)
                    asg._type_edges[spelling] = dict(target=target, qualifiers=specifiers)
                for child in [child for child in cursor.get_children() if child.kind is CursorKind.PARM_DECL]:
                    target, specifiers = read_qualified_type(asg, child.type)
                    asg._parameter_edges[spelling].append(dict(name = child.spelling, target=target, qualifiers=specifiers))
        except Warning as warning:
            asg._syntax_edges[scope].remove(spelling)
            asg._type_edges.pop(spelling, None)
            asg._parameter_edges.pop(spelling, None)
            asg._nodes.pop(spelling)
            warnings.warn(str(warning), warning.__class__)
            return []
        else:
            read_access(asg, cursor.access_specifier, spelling)
            return [spelling]

def read_field(asg, cursor, scope):
    if cursor.spelling == '':
        # TODO warning
        return []
    else:
        spelling = scope
        if spelling.startswith('class '):
            spelling = spelling[6:]
        elif spelling.startswith('union '):
            spelling = spelling[6:]
        elif spelling.startswith('struct '):
            spelling = spelling[7:]
        if not scope.endswith('::'):
            spelling = spelling + "::" + cursor.spelling
        else:
            spelling = spelling + cursor.spelling
        asg._nodes[spelling] = dict(_proxy=FieldProxy,
                _is_mutable=False,
                _is_static=False,
                _is_bit_field=cursor.is_bitfield())
        asg._syntax_edges[scope].append(spelling)
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = read_qualified_type(asg, cursor.type)
                asg._type_edges[spelling] = dict(target=target, qualifiers=specifiers)
        except Exception as error:
            asg._syntax_edges[scope].remove(spelling)
            asg._nodes.pop(spelling)
            warnings.warn(str(error))
            return []
        else:
            read_access(asg, cursor.access_specifier, spelling)
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
        spelling = scope
        if spelling.startswith('class '):
            spelling = spelling[6:]
        elif spelling.startswith('union '):
            spelling = spelling[6:]
        elif spelling.startswith('struct '):
            spelling = spelling[7:]
        if not scope.endswith('::'):
            spelling = spelling + "::" + cursor.spelling
        else:
            spelling = spelling + cursor.spelling
        if cursor.kind is CursorKind.STRUCT_DECL:
            spelling = 'struct ' + spelling
        elif cursor.kind is CursorKind.UNION_DECL:
            spelling = 'union ' + spelling
        else:
            spelling = 'class ' + spelling
        if spelling not in asg:
            if cursor.kind in [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
                asg._nodes[spelling] = dict(_proxy=ClassProxy,
                        _is_abstract=True,
                        _is_copyable=False,
                        _is_complete=False,
                        _is_explicit=True,
                        _comment="")
            elif cursor.kind is CursorKind.CLASS_DECL:
                asg._nodes[spelling] = dict(_proxy=ClassProxy,
                            _is_abstract=True,
                            _is_copyable=False,
                            _is_complete=False,
                            _is_explicit=True,
                            _comment="")
            asg._syntax_edges[spelling] = []
            asg._base_edges[spelling] = []
            asg._syntax_edges[scope].append(spelling)
        elif not asg[spelling].is_complete:
            asg._syntax_edges[scope].remove(spelling)
            asg._syntax_edges[scope].append(spelling)
        if not asg[spelling].is_complete:
            for child in cursor.get_children():
                if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                    #if spelling == 'class ::clang::FriendDecl':
                    #    import pdb
                    #    pdb.set_trace()
                    childspelling = '::' + child.type.spelling
                    childcursor = child.type.get_declaration()
                    if childcursor.kind is CursorKind.STRUCT_DECL:
                        childspelling = 'struct ' + childspelling
                    elif childcursor.kind is CursorKind.UNION_DECL:
                        childspelling = 'union ' + childspelling
                    elif childcursor.kind is CursorKind.CLASS_DECL:
                        childspelling = 'class ' + childspelling
                    # TODO
                    if childspelling in asg:
                        access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                        asg._base_edges[spelling].append(dict(base=asg[childspelling]._node,
                            _access=access,
                            _is_virtual=False))
                    else:
                        warnings.warn('Base not found')
                else:
                    for childspelling in read_cursor(asg, child, spelling):
                        asg._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                        dict.pop(asg._nodes[childspelling], "_header", None)
            asg._nodes[spelling]['_is_complete'] = len(asg._base_edges[spelling]) + len(asg._syntax_edges[spelling]) > 0
            if asg[spelling].is_complete:
                filename = str(path(str(cursor.location.file)).abspath())
                asg.add_file(filename, proxy=HeaderProxy, _language=asg._language)
                asg._nodes[spelling]['_header'] = filename
        read_access(asg, cursor.access_specifier, spelling)
        return [spelling]

def read_namespace(asg, cursor, scope):
    spelling = scope
    if not scope.endswith('::'):
        spelling = spelling + "::" + cursor.spelling
    else:
        spelling = spelling + cursor.spelling
    if spelling not in asg:
        asg._nodes[spelling] = dict(_proxy=NamespaceProxy,
                                    _is_inline=False) # TODO
        asg._syntax_edges[spelling] = []
    if spelling not in asg._syntax_edges[scope]:
        asg._syntax_edges[scope].append(spelling)
    for child in cursor.get_children():
        read_cursor(asg, child, spelling)
    read_access(asg, cursor.access_specifier, spelling)
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
