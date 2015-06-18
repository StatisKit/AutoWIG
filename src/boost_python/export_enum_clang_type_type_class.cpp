#include <boost/python.hpp>
#include <clang/AST/Type.h>

void export_enum_clang_type_type_class()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    std::string Type_83a6901d_26ba_5555_888c_763986eafc9e_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + "._type");
    boost::python::object Type_83a6901d_26ba_5555_888c_763986eafc9e_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(Type_83a6901d_26ba_5555_888c_763986eafc9e_name.c_str()))));
    boost::python::scope().attr("_type") = Type_83a6901d_26ba_5555_888c_763986eafc9e_module;
    boost::python::scope Type_83a6901d_26ba_5555_888c_763986eafc9e_scope = Type_83a6901d_26ba_5555_888c_763986eafc9e_module;
    boost::python::enum_< ::clang::Type::TypeClass >("TypeClass")
        .value("Builtin", ::clang::Type::TypeClass::Builtin)
        .value("Complex", ::clang::Type::TypeClass::Complex)
        .value("Pointer", ::clang::Type::TypeClass::Pointer)
        .value("BlockPointer", ::clang::Type::TypeClass::BlockPointer)
        .value("LValueReference", ::clang::Type::TypeClass::LValueReference)
        .value("RValueReference", ::clang::Type::TypeClass::RValueReference)
        .value("MemberPointer", ::clang::Type::TypeClass::MemberPointer)
        .value("ConstantArray", ::clang::Type::TypeClass::ConstantArray)
        .value("IncompleteArray", ::clang::Type::TypeClass::IncompleteArray)
        .value("VariableArray", ::clang::Type::TypeClass::VariableArray)
        .value("DependentSizedArray", ::clang::Type::TypeClass::DependentSizedArray)
        .value("DependentSizedExtVector", ::clang::Type::TypeClass::DependentSizedExtVector)
        .value("Vector", ::clang::Type::TypeClass::Vector)
        .value("ExtVector", ::clang::Type::TypeClass::ExtVector)
        .value("FunctionProto", ::clang::Type::TypeClass::FunctionProto)
        .value("FunctionNoProto", ::clang::Type::TypeClass::FunctionNoProto)
        .value("UnresolvedUsing", ::clang::Type::TypeClass::UnresolvedUsing)
        .value("Paren", ::clang::Type::TypeClass::Paren)
        .value("Typedef", ::clang::Type::TypeClass::Typedef)
        .value("Adjusted", ::clang::Type::TypeClass::Adjusted)
        .value("Decayed", ::clang::Type::TypeClass::Decayed)
        .value("TypeOfExpr", ::clang::Type::TypeClass::TypeOfExpr)
        .value("TypeOf", ::clang::Type::TypeClass::TypeOf)
        .value("Decltype", ::clang::Type::TypeClass::Decltype)
        .value("UnaryTransform", ::clang::Type::TypeClass::UnaryTransform)
        .value("Record", ::clang::Type::TypeClass::Record)
        .value("Enum", ::clang::Type::TypeClass::Enum)
        .value("Elaborated", ::clang::Type::TypeClass::Elaborated)
        .value("Attributed", ::clang::Type::TypeClass::Attributed)
        .value("TemplateTypeParm", ::clang::Type::TypeClass::TemplateTypeParm)
        .value("SubstTemplateTypeParm", ::clang::Type::TypeClass::SubstTemplateTypeParm)
        .value("SubstTemplateTypeParmPack", ::clang::Type::TypeClass::SubstTemplateTypeParmPack)
        .value("TemplateSpecialization", ::clang::Type::TypeClass::TemplateSpecialization)
        .value("Auto", ::clang::Type::TypeClass::Auto)
        .value("InjectedClassName", ::clang::Type::TypeClass::InjectedClassName)
        .value("DependentName", ::clang::Type::TypeClass::DependentName)
        .value("DependentTemplateSpecialization", ::clang::Type::TypeClass::DependentTemplateSpecialization)
        .value("PackExpansion", ::clang::Type::TypeClass::PackExpansion)
        .value("ObjCObject", ::clang::Type::TypeClass::ObjCObject)
        .value("ObjCInterface", ::clang::Type::TypeClass::ObjCInterface)
        .value("ObjCObjectPointer", ::clang::Type::TypeClass::ObjCObjectPointer)
        .value("Atomic", ::clang::Type::TypeClass::Atomic)
        .value("TypeLast", ::clang::Type::TypeClass::TypeLast)
        .value("TagFirst", ::clang::Type::TypeClass::TagFirst)
        .value("TagLast", ::clang::Type::TypeClass::TagLast);
}