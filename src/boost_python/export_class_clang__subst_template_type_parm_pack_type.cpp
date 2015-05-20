#include <boost/python.hpp>
#include <clang/AST/Type.h>


void export_class_clang__subst_template_type_parm_pack_type()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::SubstTemplateTypeParmPackType, ::clang::SubstTemplateTypeParmPackType*, boost::python::bases< ::clang::Type, ::llvm::FoldingSetNode >, boost::noncopyable >("SubstTemplateTypeParmPackType", boost::python::no_init);
}