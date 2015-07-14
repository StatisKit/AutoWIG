import re

from .asg import AbstractSemanticGraph, FileProxy
from .tools import lower

def _bootstrap_back_end(self, *args, **kwargs):
    diagnostic = self.back_end('boost_python', *args, **kwargs)
    modulenode = diagnostic[0]
    content = "#include <boost/python.hpp>\n"
    declcontext = self.classes('^(class |struct |)::clang::DeclContext$').pop()
    inheritors = [inheritor for inheritor in declcontext.inheritors(True)
            if inheritor.localname in [constant.localname+'Decl'
                for constant in self['enum ::clang::Decl::Kind'].constants]]
    headers = {header.globalname : header
            for header in [inheritor.header
                for inheritor in inheritors+[declcontext]]}.values()
    for header in headers:
        content += '#include <' + re.sub('(.*)include/(.*)', r'\2', header.globalname) + '>\n'

    content += '\nnamespace autowig\n{\n'
    for inheritor in inheritors:
        content += '\t' + inheritor.globalname + ' * cast_as_' + lower(inheritor.localname) + '(::clang::DeclContext* decl)\n'
        content += '\t{ return static_cast< ' + inheritor.globalname + ' * >(decl); }\n\n'
    content = content[:-1] + '}\n\n'

    content += __CAST__
    for inheritor in inheritors:
        content += '\tboost::python::def("cast_as_' + lower(inheritor.localname) + '", ::autowig::cast_as_' + lower(inheritor.localname) +', boost::python::return_value_policy< boost::python::reference_existing_object >());\n'
    content += '}'
    directory = modulenode.parent.globalname
    exportnode = modulenode.add_export(directory + 'export_namespace_clang_cast.cpp', proxy=FileProxy)
    exportnode.content = content
    on_disk = kwargs.pop('on_disk')
    if on_disk:
        exportnode.write()
    exportnode = modulenode.add_export(directory + 'export_namespace_clang_tooling.cpp', proxy=FileProxy)
    exportnode.content = __TOOLING__
    if on_disk:
        exportnode.write()
    if on_disk:
        modulenode.write()
    return diagnostic

AbstractSemanticGraph._bootstrap_back_end = _bootstrap_back_end
del _bootstrap_back_end

__CAST__ = """void export_namespace_clang_cast()
{
    std::string clang_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_name.c_str()))));
    boost::python::scope().attr("clang") = clang_module;
    boost::python::scope clang_scope = clang_module;
    std::string cast_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".cast");
    boost::python::object cast_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(cast_name.c_str()))));
    boost::python::scope().attr("cast") = cast_module;
    boost::python::scope cast_scope = cast_module;"""

__TOOLING__ = """#include <boost/python.hpp>
#include <clang/Frontend/ASTUnit.h>
#include <clang/Tooling/Tooling.h>
#include <clang/AST/Decl.h>
#include <clang/AST/DeclTemplate.h>
#include <clang/AST/Type.h>
#include <clang/AST/PrettyPrinter.h>
#include <llvm/Support/raw_ostream.h>
#include <clang/AST/Mangle.h>
#include <llvm/IR/DataLayout.h>
#include <llvm/IR/Mangler.h>
#include <clang/Basic/TargetInfo.h>

namespace autowig
{
    clang::ASTUnit* build_ast_from_code_with_args(const std::string& _code, boost::python::object _args)
    {
        std::vector< std::string > args(boost::python::len(_args));
        for(unsigned int i = 0; i < args.size(); ++i)
        { args[i] = boost::python::extract< std::string >(_args[i]); }
        llvm::Twine code(_code);
        return clang::tooling::buildASTFromCodeWithArgs(code, args).release();
    }

    unsigned int ast_get_nb_children(clang::ASTUnit& ast)
    {
        unsigned int nb = 0;
        for(auto it = ast.top_level_begin(); it != ast.top_level_end(); ++it)
        { ++nb; }
        return nb;
    }

    unsigned int tcls_get_nb_children(const clang::ClassTemplateDecl& cls)
    {
        unsigned int nb = 0;
        for(auto it = cls.spec_begin(); it != cls.spec_end(); ++it)
        { ++nb; }
        return nb;
    }

    unsigned int decl_get_nb_children(clang::DeclContext& decl)
    {
        unsigned int nb = 0;
        for(auto it = decl.decls_begin(); it != decl.decls_end(); ++it)
        { ++nb; }
        return nb;
    }

    clang::Decl* ast_get_child(clang::ASTUnit& ast, const unsigned int& child)
    {
        auto it = ast.top_level_begin();
        for(unsigned int i = 0; i < child; ++i)
        { ++it; }
        return *it;
    }

    clang::Decl* decl_get_child(const clang::DeclContext& decl, const unsigned int& child)
    {
        auto it = decl.decls_begin();
        for(unsigned int i = 0; i < child; ++i)
        { ++it; }
        return *it;
    }

    clang::Decl* tcls_get_child(const clang::ClassTemplateDecl& cls, const unsigned int& child)
    {
        auto it = cls.spec_begin();
        for(unsigned int i = 0; i < child; ++i)
        { ++it; }
        return *it;
    }

    std::string (clang::QualType::*get_as_string)() const = &clang::QualType::getAsString;

    std::string (clang::NamedDecl::*get_name_as_string)() const = &clang::NamedDecl::getNameAsString;

    std::string spec_get_name_as_string(clang::ClassTemplateSpecializationDecl* spec)
    {
        std::string spelling = "";
        llvm::raw_string_ostream os(spelling);
        os << spec->getName();
        const clang::TemplateArgumentList &args = spec->getTemplateArgs();
        clang::LangOptions lang;
        lang.CPlusPlus = true;
        clang::PrintingPolicy policy(lang);
        policy.SuppressScope = false;
        clang::TemplateSpecializationType::PrintTemplateArgumentList(os, args.data(),
                                                                  args.size(),
                                                                  policy);
        return os.str();
    }

    clang::NamespaceDecl * decl_cast_as_namespace(clang::DeclContext * decl)
    { return static_cast< clang::NamespaceDecl * >(decl); }

    clang::RecordDecl * decl_cast_as_record(clang::DeclContext * decl)
    { return static_cast< clang::RecordDecl * >(decl); }

    std::string decl_spelling(const clang::NamedDecl& decl)
    {
        std::string spelling = "";
        llvm::raw_string_ostream os(spelling);
        clang::LangOptions lang;
        lang.CPlusPlus = true;
        clang::PrintingPolicy policy(lang);
        policy.SuppressScope = false;
        decl.getNameForDiagnostic(os, policy, true);
        return os.str();
    }

    bool cxxrecord_is_copyable(const clang::CXXRecordDecl& decl)
    {
        bool res = false;
        auto it = decl.ctor_begin();
        while(!res && it != decl.ctor_end())
        {
            res = (*it)->isCopyConstructor() && !(*it)->isDeleted() && (*it)->getAccess() == clang::AccessSpecifier::AS_public;
            ++it;
        }
        return res;
    }

    clang::CXXBaseSpecifier const * cxxrecord_get_base(const clang::CXXRecordDecl& decl, const unsigned int& base)
    {
        auto it = decl.bases_begin();
        for(unsigned int i = 0; i < base; ++i)
        { ++it; }
        return it;
    }

    clang::CXXBaseSpecifier const * cxxrecord_get_virtual_base(const clang::CXXRecordDecl& decl, const unsigned int& base)
    {
        auto it = decl.vbases_begin();
        for(unsigned int i = 0; i < base; ++i)
        { ++it; }
        return it;
    }

    std::string decl_get_filename(clang::Decl* decl)
    {
        clang::ASTContext & ast = decl->getASTContext();
        clang::SourceManager &  sm = ast.getSourceManager();
        return sm.getFilename(decl->getLocation()).str();
    }

    std::string func_get_mangling(clang::FunctionDecl* decl)
    {

        clang::ASTContext & ast = decl->getASTContext();
        clang::MangleContext * mc = ast.createMangleContext();
        std::string frontend;
        llvm::raw_string_ostream frontendos(frontend);
        if(dynamic_cast< clang::CXXConstructorDecl * >(decl))
        { mc->mangleCXXCtor(dynamic_cast< clang::CXXConstructorDecl * >(decl), clang::CXXCtorType::Ctor_Complete, frontendos); }
        else if(dynamic_cast< clang::CXXDestructorDecl * >(decl))
        { mc->mangleCXXDtor(dynamic_cast< clang::CXXDestructorDecl * >(decl), clang::CXXDtorType::Dtor_Complete, frontendos); }
        else
        { mc->mangleName(decl, frontendos); }
        llvm::DataLayout* data_layout = new llvm::DataLayout(ast.getTargetInfo().getTargetDescription());
        llvm::Mangler middleend(data_layout);

        std::string backend;
        llvm::raw_string_ostream backendos(backend);
        middleend.getNameWithPrefix(backendos, llvm::Twine(frontendos.str()));
        delete data_layout;
        return backendos.str();
    }
}

void export_namespace_clang_tooling()
{
    std::string clang_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_name.c_str()))));
    boost::python::scope().attr("clang") = clang_module;
    boost::python::scope clang_scope = clang_module;
    std::string tooling_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".tooling");
    boost::python::object tooling_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(tooling_name.c_str()))));
    boost::python::scope().attr("tooling") = tooling_module;
    boost::python::scope tooling_scope = tooling_module;
    boost::python::def("build_ast_from_code_with_args", ::autowig::build_ast_from_code_with_args, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("get_name", &::clang::NamedDecl::getNameAsString);
    boost::python::def("ast_get_nb_children", ::autowig::ast_get_nb_children);
    boost::python::def("decl_get_nb_children", ::autowig::decl_get_nb_children);
    boost::python::def("tcls_get_nb_children", ::autowig::tcls_get_nb_children);
    boost::python::def("ast_get_child", ::autowig::ast_get_child, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("decl_get_child", ::autowig::decl_get_child, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("tcls_get_child", ::autowig::tcls_get_child, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("get_as_string", ::autowig::get_as_string);
    boost::python::def("get_name", ::autowig::get_name_as_string);
    boost::python::def("spec_get_name", ::autowig::spec_get_name_as_string);
    boost::python::def("decl_cast_as_namespace", ::autowig::decl_cast_as_namespace, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("decl_cast_as_record", ::autowig::decl_cast_as_record, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("decl_spelling", ::autowig::decl_spelling);
    boost::python::def("cxxrecord_is_copyable", ::autowig::cxxrecord_is_copyable);
    boost::python::def("cxxrecord_get_base", ::autowig::cxxrecord_get_base, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("cxxrecord_get_virtual_base", ::autowig::cxxrecord_get_virtual_base, boost::python::return_value_policy< boost::python::reference_existing_object >());
    boost::python::def("decl_get_filename", ::autowig::decl_get_filename);
    boost::python::def("func_get_mangling", ::autowig::func_get_mangling);
}"""
