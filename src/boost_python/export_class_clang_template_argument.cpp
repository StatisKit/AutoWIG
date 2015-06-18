#include <boost/python.hpp>
#include <clang/AST/Decl.h>
#include <clang/AST/TemplateBase.h>
#include <clang/AST/Type.h>

void export_class_clang_template_argument()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::TemplateArgument, ::clang::TemplateArgument *, boost::noncopyable >("TemplateArgument", boost::python::no_init)
        .def("get_kind", &::clang::TemplateArgument::getKind)
        .def("get_as_type", &::clang::TemplateArgument::getAsType)
        .def("get_as_decl", &::clang::TemplateArgument::getAsDecl, boost::python::return_value_policy< boost::python::reference_existing_object >());
}