from _autowig import *

clang.ASTUnit.get_nb_children = clang.tooling.ast_get_nb_children
del clang.tooling.ast_get_nb_children
clang.DeclContext.get_nb_children = clang.tooling.decl_get_nb_children
del clang.tooling.decl_get_nb_children
clang.DeclContext.cast_as_namespace = clang.tooling.decl_cast_as_namespace
del clang.tooling.decl_cast_as_namespace
clang.DeclContext.cast_as_record = clang.tooling.decl_cast_as_record
del clang.tooling.decl_cast_as_record
clang.ClassTemplateDecl.get_nb_children = clang.tooling.tcls_get_nb_children
del clang.tooling.tcls_get_nb_children

clang.ASTUnit.get_child = clang.tooling.ast_get_child
del clang.tooling.ast_get_child
clang.DeclContext.get_child = clang.tooling.decl_get_child
del clang.tooling.decl_get_child
clang.ClassTemplateDecl.get_child = clang.tooling.tcls_get_child
del clang.tooling.tcls_get_child

def get_children(self):
    return [self.get_child(index) for index in range(self.get_nb_children())]

clang.ASTUnit.get_children = get_children
clang.DeclContext.get_children = get_children
clang.ClassTemplateDecl.get_children = get_children
del get_children

def get_children(self):
    if self.get_nb_children() == 0:
        return []
    else:
        return [self.get_child(index) for index in range(1, self.get_nb_children())]

clang.CXXRecordDecl.get_children = get_children
del get_children

clang.CXXRecordDecl.get_base = clang.tooling.cxxrecord_get_base
del clang.tooling.cxxrecord_get_base

def get_bases(self):
    return [self.get_base(index) for index in range(self.get_num_bases())]

clang.CXXRecordDecl.get_bases = get_bases
del get_bases

clang.CXXRecordDecl.get_virtual_base = clang.tooling.cxxrecord_get_virtual_base
del clang.tooling.cxxrecord_get_virtual_base

def get_virtual_bases(self):
    return [self.get_virtual_base(index) for index in range(self.get_num_vbases())]

clang.CXXRecordDecl.get_virtual_bases = get_virtual_bases
del get_virtual_bases

def get_children(self):
    return [self.get_param_decl(index) for index in range(self.get_num_params())]

clang.FunctionDecl.get_children = get_children
del get_children

clang.QualType.get_as_string = clang.tooling.get_as_string
del clang.tooling.get_as_string

import re
from functools import wraps

def wrapper(func):
    @wraps(func)
    def spelling(self):
        return re.sub('::(:*)', '::', func(self))

clang.NamedDecl._spelling = clang.tooling.decl_spelling
del clang.tooling.decl_spelling

def spelling(self):
    spelling = re.sub('::(:*)', '::', re.sub(r'\(anonymous\)', '', self._spelling()))
    if spelling.endswith('::'):
        return '::' + spelling[:-2]
    else:
        return '::' + spelling

clang.NamedDecl.spelling = spelling
del spelling

clang.CXXRecordDecl.is_copyable = clang.tooling.cxxrecord_is_copyable
del clang.tooling.cxxrecord_is_copyable

clang.Decl.get_filename = clang.tooling.decl_get_filename
del clang.tooling.decl_get_filename
