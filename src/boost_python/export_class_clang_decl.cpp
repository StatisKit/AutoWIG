#include <boost/python.hpp>
#include <clang/AST/DeclBase.h>
#include <clang/Basic/Specifiers.h>
namespace autowig
{
    ::clang::DeclContext * (::clang::Decl::*getDeclContext_9b074587_2f89_5a1e_8310_6509f80ab876)() = &::clang::Decl::getDeclContext;
}

void export_class_clang_decl()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::Decl, ::clang::Decl *, boost::noncopyable >("Decl", boost::python::no_init)
        .def("get_kind", &::clang::Decl::getKind)
        .def("get_decl_context", autowig::getDeclContext_9b074587_2f89_5a1e_8310_6509f80ab876, boost::python::return_value_policy< boost::python::reference_existing_object >())
        .def("get_access_unsafe", &::clang::Decl::getAccessUnsafe)
        .def("is_implicit", &::clang::Decl::isImplicit);
}