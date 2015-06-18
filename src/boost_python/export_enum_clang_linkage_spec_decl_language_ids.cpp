#include <boost/python.hpp>
#include <clang/AST/DeclCXX.h>

void export_enum_clang_linkage_spec_decl_language_ids()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    std::string LinkageSpecDecl_cc1a9fb0_93c8_5614_836d_03c79e84d854_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + "._linkage_spec_decl");
    boost::python::object LinkageSpecDecl_cc1a9fb0_93c8_5614_836d_03c79e84d854_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(LinkageSpecDecl_cc1a9fb0_93c8_5614_836d_03c79e84d854_name.c_str()))));
    boost::python::scope().attr("_linkage_spec_decl") = LinkageSpecDecl_cc1a9fb0_93c8_5614_836d_03c79e84d854_module;
    boost::python::scope LinkageSpecDecl_cc1a9fb0_93c8_5614_836d_03c79e84d854_scope = LinkageSpecDecl_cc1a9fb0_93c8_5614_836d_03c79e84d854_module;
    boost::python::enum_< ::clang::LinkageSpecDecl::LanguageIDs >("LanguageIDs")
        .value("lang_c", ::clang::LinkageSpecDecl::LanguageIDs::lang_c)
        .value("lang_cxx", ::clang::LinkageSpecDecl::LanguageIDs::lang_cxx);
}