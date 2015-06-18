#include <boost/python.hpp>
#include <clang/AST/DeclCXX.h>
#include <clang/AST/Decl.h>
#include <clang/AST/DeclObjC.h>
#include <clang/AST/DeclBase.h>
#include <clang/AST/DeclTemplate.h>

namespace autowig
{
	::clang::TranslationUnitDecl * cast_as_translation_unit_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::TranslationUnitDecl * >(decl); }

	::clang::ObjCCategoryDecl * cast_as_obj_ccategory_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ObjCCategoryDecl * >(decl); }

	::clang::BlockDecl * cast_as_block_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::BlockDecl * >(decl); }

	::clang::FunctionDecl * cast_as_function_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::FunctionDecl * >(decl); }

	::clang::CapturedDecl * cast_as_captured_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::CapturedDecl * >(decl); }

	::clang::ClassTemplateSpecializationDecl * cast_as_class_template_specialization_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ClassTemplateSpecializationDecl * >(decl); }

	::clang::CXXDestructorDecl * cast_as_cxxdestructor_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::CXXDestructorDecl * >(decl); }

	::clang::ObjCCategoryImplDecl * cast_as_obj_ccategory_impl_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ObjCCategoryImplDecl * >(decl); }

	::clang::ObjCProtocolDecl * cast_as_obj_cprotocol_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ObjCProtocolDecl * >(decl); }

	::clang::LinkageSpecDecl * cast_as_linkage_spec_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::LinkageSpecDecl * >(decl); }

	::clang::NamespaceDecl * cast_as_namespace_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::NamespaceDecl * >(decl); }

	::clang::RecordDecl * cast_as_record_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::RecordDecl * >(decl); }

	::clang::CXXRecordDecl * cast_as_cxxrecord_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::CXXRecordDecl * >(decl); }

	::clang::ExternCContextDecl * cast_as_extern_ccontext_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ExternCContextDecl * >(decl); }

	::clang::ClassTemplatePartialSpecializationDecl * cast_as_class_template_partial_specialization_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ClassTemplatePartialSpecializationDecl * >(decl); }

	::clang::EnumDecl * cast_as_enum_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::EnumDecl * >(decl); }

	::clang::ObjCInterfaceDecl * cast_as_obj_cinterface_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ObjCInterfaceDecl * >(decl); }

	::clang::CXXMethodDecl * cast_as_cxxmethod_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::CXXMethodDecl * >(decl); }

	::clang::CXXConversionDecl * cast_as_cxxconversion_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::CXXConversionDecl * >(decl); }

	::clang::ObjCMethodDecl * cast_as_obj_cmethod_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ObjCMethodDecl * >(decl); }

	::clang::ObjCImplementationDecl * cast_as_obj_cimplementation_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::ObjCImplementationDecl * >(decl); }

	::clang::CXXConstructorDecl * cast_as_cxxconstructor_decl(::clang::DeclContext* decl)
	{ return static_cast< ::clang::CXXConstructorDecl * >(decl); }
}

void export_functions_clang_cast()
{
    std::string clang_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_name.c_str()))));
    boost::python::scope().attr("clang") = clang_module;
    boost::python::scope clang_scope = clang_module;
    std::string cast_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".cast");
    boost::python::object cast_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(cast_name.c_str()))));
    boost::python::scope().attr("cast") = cast_module;
    boost::python::scope cast_scope = cast_module;	boost::python::def("cast_as_translation_unit_decl", ::autowig::cast_as_translation_unit_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_obj_ccategory_decl", ::autowig::cast_as_obj_ccategory_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_block_decl", ::autowig::cast_as_block_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_function_decl", ::autowig::cast_as_function_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_captured_decl", ::autowig::cast_as_captured_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_class_template_specialization_decl", ::autowig::cast_as_class_template_specialization_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_cxxdestructor_decl", ::autowig::cast_as_cxxdestructor_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_obj_ccategory_impl_decl", ::autowig::cast_as_obj_ccategory_impl_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_obj_cprotocol_decl", ::autowig::cast_as_obj_cprotocol_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_linkage_spec_decl", ::autowig::cast_as_linkage_spec_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_namespace_decl", ::autowig::cast_as_namespace_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_record_decl", ::autowig::cast_as_record_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_cxxrecord_decl", ::autowig::cast_as_cxxrecord_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_extern_ccontext_decl", ::autowig::cast_as_extern_ccontext_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_class_template_partial_specialization_decl", ::autowig::cast_as_class_template_partial_specialization_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_enum_decl", ::autowig::cast_as_enum_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_obj_cinterface_decl", ::autowig::cast_as_obj_cinterface_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_cxxmethod_decl", ::autowig::cast_as_cxxmethod_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_cxxconversion_decl", ::autowig::cast_as_cxxconversion_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_obj_cmethod_decl", ::autowig::cast_as_obj_cmethod_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_obj_cimplementation_decl", ::autowig::cast_as_obj_cimplementation_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
	boost::python::def("cast_as_cxxconstructor_decl", ::autowig::cast_as_cxxconstructor_decl, boost::python::return_value_policy< boost::python::reference_existing_object >());
}