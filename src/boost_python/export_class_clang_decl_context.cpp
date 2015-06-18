#include <boost/python.hpp>
#include <clang/AST/DeclBase.h>
namespace autowig
{
    ::clang::DeclContext * (::clang::DeclContext::*getParent_7c737552_afb9_5b52_90d6_92ce8b8d8477)() = &::clang::DeclContext::getParent;
    ::clang::DeclContext * (::clang::DeclContext::*getLexicalParent_2e3defbf_2fc1_52a6_8ce3_8c466866c52a)() = &::clang::DeclContext::getLexicalParent;
    ::clang::DeclContext * (::clang::DeclContext::*getLookupParent_51938c39_09f4_5a0c_bbc2_ff30ce68f2eb)() = &::clang::DeclContext::getLookupParent;
}

void export_class_clang_decl_context()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::DeclContext, ::clang::DeclContext *, boost::noncopyable >("DeclContext", boost::python::no_init)
        .def("get_decl_kind", &::clang::DeclContext::getDeclKind)
        .def("get_parent", autowig::getParent_7c737552_afb9_5b52_90d6_92ce8b8d8477, boost::python::return_value_policy< boost::python::reference_existing_object >())
        .def("get_lexical_parent", autowig::getLexicalParent_2e3defbf_2fc1_52a6_8ce3_8c466866c52a, boost::python::return_value_policy< boost::python::reference_existing_object >())
        .def("get_lookup_parent", autowig::getLookupParent_51938c39_09f4_5a0c_bbc2_ff30ce68f2eb, boost::python::return_value_policy< boost::python::reference_existing_object >());
}