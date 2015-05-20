from _autowig import *

clang.ASTUnit.get_nb_children = clang.tooling.ast_get_nb_children
del clang.tooling.ast_get_nb_children
clang.DeclContext.get_nb_children = clang.tooling.decl_get_nb_children
del clang.tooling.decl_get_nb_children


clang.ASTUnit.get_child = clang.tooling.ast_get_child
del clang.tooling.ast_get_child
clang.DeclContext.get_child = clang.tooling.decl_get_child
del clang.tooling.decl_get_child

def get_children(self):
    return [self.get_child(index) for index in range(self.get_nb_children())]

clang.ASTUnit.get_children = get_children
clang.DeclContext.get_children = get_children
del get_children

clang.NamedDecl.get_name = clang.tooling.get_name
del clang.tooling.get_name

def get_children(self):
    return [self.get_param_decl(index) for index in range(self.get_num_params())]

clang.FunctionDecl.get_children = get_children
del get_children

clang.QualType.get_as_string = clang.tooling.get_as_string
del clang.tooling.get_as_string
