#include <boost/python.hpp>
#include <clang/AST/DeclObjC.h>


void export_class_clang__obj_cproperty_impl_decl()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::ObjCPropertyImplDecl, ::clang::ObjCPropertyImplDecl*, boost::python::bases< ::clang::Decl >, boost::noncopyable >("ObjCPropertyImplDecl", boost::python::no_init);
}