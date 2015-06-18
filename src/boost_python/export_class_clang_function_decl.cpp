#include <boost/python.hpp>
#include <clang/AST/Decl.h>
#include <clang/AST/Type.h>
namespace autowig
{
    ::clang::ParmVarDecl * (::clang::FunctionDecl::*getParamDecl_bcf16746_a256_5ff0_b50d_96e603e57d27)(unsigned int) = &::clang::FunctionDecl::getParamDecl;
}

void export_class_clang_function_decl()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::FunctionDecl, ::clang::FunctionDecl *, boost::python::bases< ::clang::DeclaratorDecl, ::clang::DeclContext >, boost::noncopyable >("FunctionDecl", boost::python::no_init)
        .def("is_deleted", &::clang::FunctionDecl::isDeleted)
        .def("get_num_params", &::clang::FunctionDecl::getNumParams)
        .def("get_param_decl", autowig::getParamDecl_bcf16746_a256_5ff0_b50d_96e603e57d27, boost::python::return_value_policy< boost::python::reference_existing_object >())
        .def("get_return_type", &::clang::FunctionDecl::getReturnType);
}