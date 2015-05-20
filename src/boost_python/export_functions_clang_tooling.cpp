#include <boost/python.hpp>
#include <clang/Frontend/ASTUnit.h>
#include <clang/Tooling/Tooling.h>
#include <clang/AST/Decl.h>

namespace autowig
{
    clang::ASTUnit* build_ast_from_code_with_args(const std::string& _code, boost::python::object _args)
    {
        std::vector< std::string > args(boost::python::len(_args));
        for(unsigned int i = 0; i < args.size(); ++i)
        { args[i] = boost::python::extract< std::string >(_args[i]); }
        llvm::Twine code(_code);
        return clang::tooling::buildASTFromCodeWithArgs(code, args).release(); 
    }
    
    unsigned int ast_get_nb_children(clang::ASTUnit& ast)
    {
        unsigned int nb = 0;
        for(auto it = ast.top_level_begin(); it != ast.top_level_end(); ++it)
        { ++nb; }
        return nb;
    }
    
    unsigned int decl_get_nb_children(clang::DeclContext& decl)
    {
        unsigned int nb = 0;
        for(auto it = decl.decls_begin(); it != decl.decls_end(); ++it)
        { ++nb; }
        return nb;
    }
    
    clang::Decl* ast_get_child(clang::ASTUnit& ast, const unsigned int& child)
    {
        auto it = ast.top_level_begin();
        for(unsigned int i = 0; i < child; ++i)
        { ++it; }
        return *it;
    }
    
    clang::Decl* decl_get_child(const clang::DeclContext& decl, const unsigned int& child)
    {
        auto it = decl.decls_begin();
        for(unsigned int i = 0; i < child; ++i)
        { ++it; }
        return *it;
    }
    
    std::string (clang::QualType::*get_as_string)() const = &clang::QualType::getAsString;
}

void export_functions_clang_tooling()
{
    std::string clang_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_name.c_str()))));
    boost::python::scope().attr("clang") = clang_module;
    boost::python::scope clang_scope = clang_module;
    std::string tooling_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".tooling");
    boost::python::object tooling_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(tooling_name.c_str()))));
    boost::python::scope().attr("tooling") = tooling_module;
    boost::python::scope tooling_scope = tooling_module;
    boost::python::def("build_ast_from_code_with_args", ::autowig::build_ast_from_code_with_args, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("get_name", &::clang::NamedDecl::getNameAsString);
    boost::python::def("ast_get_nb_children", ::autowig::ast_get_nb_children);
    boost::python::def("decl_get_nb_children", ::autowig::decl_get_nb_children);
    boost::python::def("ast_get_child", ::autowig::ast_get_child, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("decl_get_child", ::autowig::decl_get_child, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("get_as_string", ::autowig::get_as_string);
}