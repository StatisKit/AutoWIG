try:
    from _autowig import *

    def __str__(self):
        return 'ASTUnit'

    clang.ASTUnit.__str__ = __str__
    del __str__

    def __str__(self):
        return self.__class__.__name__#[self.__class__.__name__.rindex('.')+1:]

    clang.Decl.__str__ = __str__
    del __str__

    def __str__(self):
        text = self.get_name()
        kind = self.__class__.__name__#[self.__class__.__name__.rindex('.')+1:]
        return '{} {}'.format(kind, text)

    clang.NamedDecl.__str__ = __str__
    del __str__

    if hasattr(clang.tooling, 'ast_get_nb_children'):
        clang.ASTUnit.get_nb_children = clang.tooling.ast_get_nb_children
        del clang.tooling.ast_get_nb_children
    if hasattr(clang.tooling, 'decl_get_nb_children'):
        clang.DeclContext.get_nb_children = clang.tooling.decl_get_nb_children
        del clang.tooling.decl_get_nb_children
    if hasattr(clang.tooling, 'decl_cast_as_namespace'):
        clang.DeclContext.cast_as_namespace = clang.tooling.decl_cast_as_namespace
        del clang.tooling.decl_cast_as_namespace
    if hasattr(clang.tooling, 'decl_cast_as_record'):
        clang.DeclContext.cast_as_record = clang.tooling.decl_cast_as_record
        del clang.tooling.decl_cast_as_record
    if hasattr(clang.tooling, 'tcls_get_nb_children'):
        clang.ClassTemplateDecl.get_nb_children = clang.tooling.tcls_get_nb_children
        del clang.tooling.tcls_get_nb_children

    if hasattr(clang.tooling, 'ast_get_child'):
        clang.ASTUnit.get_child = clang.tooling.ast_get_child
        del clang.tooling.ast_get_child
    if hasattr(clang.tooling, 'decl_get_child'):
        clang.DeclContext.get_child = clang.tooling.decl_get_child
        del clang.tooling.decl_get_child
    if hasattr(clang.tooling, 'tcls_get_child'):
        clang.ClassTemplateDecl.get_child = clang.tooling.tcls_get_child
        del clang.tooling.tcls_get_child

    def get_children(self):
        return [self.get_child(index) for index in range(self.get_nb_children())]

    clang.DeclContext.get_children = get_children
    clang.ClassTemplateDecl.get_children = get_children
    del get_children

    def get_children(self):
        return [child for child in [self.get_child(index) for index in range(self.get_nb_children())] if not isinstance(child, clang.CXXMethodDecl)]

    clang.ASTUnit.get_children = get_children
    clang.NamespaceDecl.get_children = get_children
    del get_children

    def get_children(self):
        if self.get_nb_children() == 0:
            return []
        else:
            return [self.get_child(index) for index in range(1, self.get_nb_children())]

    clang.CXXRecordDecl.get_children = get_children
    del get_children

    if hasattr(clang.tooling, 'cxxrecord_get_base'):
        clang.CXXRecordDecl.get_base = clang.tooling.cxxrecord_get_base
        del clang.tooling.cxxrecord_get_base

    def get_bases(self):
        return [self.get_base(index) for index in range(self.get_num_bases())]

    clang.CXXRecordDecl.get_bases = get_bases
    del get_bases

    if hasattr(clang.tooling, 'cxxrecord_get_virtual_base'):
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

    if hasattr(clang.tooling, 'get_as_string'):
        clang.QualType.get_as_string = clang.tooling.get_as_string
        del clang.tooling.get_as_string

    if hasattr(clang.tooling, 'get_name'):
        clang.NamedDecl.get_name = clang.tooling.get_name
        del clang.tooling.get_name

    if hasattr(clang.tooling, 'spec_get_name'):
        clang.ClassTemplateSpecializationDecl.get_name = clang.tooling.spec_get_name
        del clang.tooling.spec_get_name

    import re
    from functools import wraps

    def wrapper(func):
        @wraps(func)
        def spelling(self):
            return re.sub('::(:*)', '::', func(self))

    if hasattr(clang.tooling, 'decl_spelling'):
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

    if hasattr(clang.tooling, 'cxxrecord_is_copyable'):
        clang.CXXRecordDecl.is_copyable = clang.tooling.cxxrecord_is_copyable
        del clang.tooling.cxxrecord_is_copyable
    if hasattr(clang.tooling, 'decl_get_filename'):
        clang.Decl.get_filename = clang.tooling.decl_get_filename
        del clang.tooling.decl_get_filename

    if hasattr(clang.tooling, 'func_get_mangling'):
        clang.FunctionDecl.get_mangling = clang.tooling.func_get_mangling
        del clang.tooling.func_get_mangling

    if hasattr(clang.tooling, 'decl_context_cast'):
        clang.FunctionDecl.cast = clang.tooling.decl_context_cast
        del clang.tooling.decl_context_cast

except:
    pass
