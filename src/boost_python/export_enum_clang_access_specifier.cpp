#include <boost/python.hpp>
#include <clang/Basic/Specifiers.h>

void export_enum_clang_access_specifier()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::enum_< ::clang::AccessSpecifier >("AccessSpecifier")
        .value("AS_public", ::clang::AccessSpecifier::AS_public)
        .value("AS_protected", ::clang::AccessSpecifier::AS_protected)
        .value("AS_private", ::clang::AccessSpecifier::AS_private)
        .value("AS_none", ::clang::AccessSpecifier::AS_none);
}