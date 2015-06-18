#include <boost/python.hpp>
#include <clang/AST/Decl.h>
#include <clang/AST/Type.h>

void export_class_clang_type()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::class_< ::clang::Type, ::clang::Type *, boost::python::bases< ::clang::ExtQualsTypeCommonBase >, boost::noncopyable >("Type", boost::python::no_init)
        .def("get_type_class", &::clang::Type::getTypeClass)
        .def("is_builtin_type", &::clang::Type::isBuiltinType)
        .def("is_specific_builtin_type", &::clang::Type::isSpecificBuiltinType)
        .def("is_enumeral_type", &::clang::Type::isEnumeralType)
        .def("is_pointer_type", &::clang::Type::isPointerType)
        .def("is_lvalue_reference_type", &::clang::Type::isLValueReferenceType)
        .def("is_rvalue_reference_type", &::clang::Type::isRValueReferenceType)
        .def("is_structure_or_class_type", &::clang::Type::isStructureOrClassType)
        .def("is_union_type", &::clang::Type::isUnionType)
        .def("get_as_tag_decl", &::clang::Type::getAsTagDecl, boost::python::return_value_policy< boost::python::reference_existing_object >())
        .def("get_pointee_type", &::clang::Type::getPointeeType)
        .def("get_unqualified_desugared_type", &::clang::Type::getUnqualifiedDesugaredType, boost::python::return_value_policy< boost::python::reference_existing_object >())
        .def("get_canonical_type_internal", &::clang::Type::getCanonicalTypeInternal);
}