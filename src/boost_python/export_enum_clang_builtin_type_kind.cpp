#include <boost/python.hpp>
#include <clang/AST/Type.h>

void export_enum_clang_builtin_type_kind()
{
    std::string clang_7bbff48d_1098_53e8_8270_b3595c663a99_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_7bbff48d_1098_53e8_8270_b3595c663a99_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_7bbff48d_1098_53e8_8270_b3595c663a99_name.c_str()))));
    boost::python::scope().attr("clang") = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    boost::python::scope clang_7bbff48d_1098_53e8_8270_b3595c663a99_scope = clang_7bbff48d_1098_53e8_8270_b3595c663a99_module;
    std::string BuiltinType_1318695b_23e9_53e0_883e_26a7efdbb653_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + "._builtin_type");
    boost::python::object BuiltinType_1318695b_23e9_53e0_883e_26a7efdbb653_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(BuiltinType_1318695b_23e9_53e0_883e_26a7efdbb653_name.c_str()))));
    boost::python::scope().attr("_builtin_type") = BuiltinType_1318695b_23e9_53e0_883e_26a7efdbb653_module;
    boost::python::scope BuiltinType_1318695b_23e9_53e0_883e_26a7efdbb653_scope = BuiltinType_1318695b_23e9_53e0_883e_26a7efdbb653_module;
    boost::python::enum_< ::clang::BuiltinType::Kind >("Kind")
        .value("Void", ::clang::BuiltinType::Kind::Void)
        .value("Bool", ::clang::BuiltinType::Kind::Bool)
        .value("Char_U", ::clang::BuiltinType::Kind::Char_U)
        .value("UChar", ::clang::BuiltinType::Kind::UChar)
        .value("WChar_U", ::clang::BuiltinType::Kind::WChar_U)
        .value("Char16", ::clang::BuiltinType::Kind::Char16)
        .value("Char32", ::clang::BuiltinType::Kind::Char32)
        .value("UShort", ::clang::BuiltinType::Kind::UShort)
        .value("UInt", ::clang::BuiltinType::Kind::UInt)
        .value("ULong", ::clang::BuiltinType::Kind::ULong)
        .value("ULongLong", ::clang::BuiltinType::Kind::ULongLong)
        .value("UInt128", ::clang::BuiltinType::Kind::UInt128)
        .value("Char_S", ::clang::BuiltinType::Kind::Char_S)
        .value("SChar", ::clang::BuiltinType::Kind::SChar)
        .value("WChar_S", ::clang::BuiltinType::Kind::WChar_S)
        .value("Short", ::clang::BuiltinType::Kind::Short)
        .value("Int", ::clang::BuiltinType::Kind::Int)
        .value("Long", ::clang::BuiltinType::Kind::Long)
        .value("LongLong", ::clang::BuiltinType::Kind::LongLong)
        .value("Int128", ::clang::BuiltinType::Kind::Int128)
        .value("Half", ::clang::BuiltinType::Kind::Half)
        .value("Float", ::clang::BuiltinType::Kind::Float)
        .value("Double", ::clang::BuiltinType::Kind::Double)
        .value("LongDouble", ::clang::BuiltinType::Kind::LongDouble)
        .value("NullPtr", ::clang::BuiltinType::Kind::NullPtr)
        .value("ObjCId", ::clang::BuiltinType::Kind::ObjCId)
        .value("ObjCClass", ::clang::BuiltinType::Kind::ObjCClass)
        .value("ObjCSel", ::clang::BuiltinType::Kind::ObjCSel)
        .value("OCLImage1d", ::clang::BuiltinType::Kind::OCLImage1d)
        .value("OCLImage1dArray", ::clang::BuiltinType::Kind::OCLImage1dArray)
        .value("OCLImage1dBuffer", ::clang::BuiltinType::Kind::OCLImage1dBuffer)
        .value("OCLImage2d", ::clang::BuiltinType::Kind::OCLImage2d)
        .value("OCLImage2dArray", ::clang::BuiltinType::Kind::OCLImage2dArray)
        .value("OCLImage3d", ::clang::BuiltinType::Kind::OCLImage3d)
        .value("OCLSampler", ::clang::BuiltinType::Kind::OCLSampler)
        .value("OCLEvent", ::clang::BuiltinType::Kind::OCLEvent)
        .value("Dependent", ::clang::BuiltinType::Kind::Dependent)
        .value("Overload", ::clang::BuiltinType::Kind::Overload)
        .value("BoundMember", ::clang::BuiltinType::Kind::BoundMember)
        .value("PseudoObject", ::clang::BuiltinType::Kind::PseudoObject)
        .value("UnknownAny", ::clang::BuiltinType::Kind::UnknownAny)
        .value("BuiltinFn", ::clang::BuiltinType::Kind::BuiltinFn)
        .value("ARCUnbridgedCast", ::clang::BuiltinType::Kind::ARCUnbridgedCast)
        .value("LastKind", ::clang::BuiltinType::Kind::LastKind);
}