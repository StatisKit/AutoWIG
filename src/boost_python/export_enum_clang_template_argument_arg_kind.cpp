#include <boost/python.hpp>
#include <clang/AST/TemplateBase.h>

void export_enum_clang_template_argument_arg_kind()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    std::string TemplateArgument_c43e6e6c_ea6e_5738_b674_cced4a8343c7_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + "._template_argument");
    boost::python::object TemplateArgument_c43e6e6c_ea6e_5738_b674_cced4a8343c7_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(TemplateArgument_c43e6e6c_ea6e_5738_b674_cced4a8343c7_name.c_str()))));
    boost::python::scope().attr("_template_argument") = TemplateArgument_c43e6e6c_ea6e_5738_b674_cced4a8343c7_module;
    boost::python::scope TemplateArgument_c43e6e6c_ea6e_5738_b674_cced4a8343c7_scope = TemplateArgument_c43e6e6c_ea6e_5738_b674_cced4a8343c7_module;
    boost::python::enum_< ::clang::TemplateArgument::ArgKind >("ArgKind")
        .value("Null", ::clang::TemplateArgument::ArgKind::Null)
        .value("Type", ::clang::TemplateArgument::ArgKind::Type)
        .value("Declaration", ::clang::TemplateArgument::ArgKind::Declaration)
        .value("NullPtr", ::clang::TemplateArgument::ArgKind::NullPtr)
        .value("Integral", ::clang::TemplateArgument::ArgKind::Integral)
        .value("Template", ::clang::TemplateArgument::ArgKind::Template)
        .value("TemplateExpansion", ::clang::TemplateArgument::ArgKind::TemplateExpansion)
        .value("Expression", ::clang::TemplateArgument::ArgKind::Expression)
        .value("Pack", ::clang::TemplateArgument::ArgKind::Pack);
}