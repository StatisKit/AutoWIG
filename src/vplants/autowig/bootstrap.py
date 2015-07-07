import re

from .tools import lower

def bootstrap_middle_end(self, include=None):
    """
    """

    if include is None:
        def include(header):
            return '<' + re.sub('(.*)include/(.*)', r'\2', header.globalname) + '>'
    if not callable(include):
        raise TypeError('\'include\' parameter')

    for node in self.nodes():
        node.clean = True

    self.classes('^(class | union|struct |)::clang::ASTUnit$').pop().clean = False

    for node in self.classes('^(class | union|struct |)::clang::([a-zA-Z]*(Decl|Type)|DeclContext)$'):
        node.clean = False

    self.enums('^(enum |)::clang::AccessSpecifier').pop().clean = False

    self.classes('^(class | union|struct |)::clang::CXXBaseSpecifier').pop().clean = False
    for function in self.functions('^::clang::CXXBaseSpecifier::getAccessSpecifier', free=False):
        if function.localname == 'getAccessSpecifier':
            function.clean = False
            break
    for function in self.functions('^::clang::CXXBaseSpecifier::getType', free=False):
        if function.localname == 'getType':
            function.clean = False
            break

    node = self.classes('^(class | union|struct |)::clang::QualType$').pop()
    self._nodes[node.id]['is_abstract'] = False
    self._nodes[node.id]['_is_copyable'] = True
    self.functions('^::clang::QualType::isConstQualified', free=False).pop().clean = False
    self.functions('^::clang::QualType::isVolatileQualified', free=False).pop().clean = False
    self.functions('^::clang::QualType::getTypePtrOrNull', free=False).pop().clean = False

    self.functions('^(class | union|struct |)::clang::Type::isBuiltinType', free=False).pop().clean = False
    for function in self.functions('^::clang::Type::isSpecificBuiltinType', free=False):
        if function.localname == 'isSpecificBuiltinType':
            function.clean = False
            break
    self.functions('^::clang::Type::isPointerType', free=False).pop().clean = False
    self.functions('^::clang::Type::isLValueReferenceType', free=False).pop().clean = False
    self.functions('^::clang::Type::isRValueReferenceType', free=False).pop().clean = False
    self.functions('^::clang::Type::getPointeeType', free=False).pop().clean = False
    self.functions('^::clang::Type::isStructureOrClassType', free=False).pop().clean = False
    self.functions('^::clang::Type::isEnumeralType', free=False).pop().clean = False
    self.functions('^::clang::Type::isUnionType', free=False).pop().clean = False
    self.functions('^::clang::Type::getAsTagDecl', free=False).pop().clean = False
    self.enums('(enum |)::clang::Type::TypeClass').pop().clean = False
    self.functions('^::clang::Type::isBuiltinType', free=False).pop().clean = False
    self.functions('^::clang::Type::getUnqualifiedDesugaredType', free=False).pop().clean = False
    self.functions('^::clang::Type::getCanonicalTypeInternal', free=False).pop().clean = False
    for function in self.functions('^::clang::Type::getTypeClass', free=False):
        if function.localname == 'getTypeClass':
            function.clean = False
            break

    self.functions('::clang::ElaboratedType::getNamedType', free=False).pop().clean = False
    self.functions('::clang::ElaboratedType::desugar', free=False).pop().clean = False

    self.enums('^(enum |)::clang::BuiltinType::Kind$').pop().clean = False

    self.functions('^::clang::Decl::isImplicit', free=False).pop().clean = False
    self.functions('^::clang::Decl::getAccessUnsafe', free=False).pop().clean = False
    self.enums('(enum |)::clang::Decl::Kind').pop().clean = False
    self.functions('^::clang::Decl::getKind').pop().clean = False
    for function in self.functions('^::clang::Decl::getDeclContext', free=False):
        if function.result_type.globalname in [prefix + '::clang::DeclContext *' for prefix in ['', 'class ']]:
            function.is_overloaded = True
            function.clean = False
            break
    for function in self.functions('^::clang::DeclContext::getDeclKind', free=False):
        if function.localname == 'getDeclKind':
            function.clean = False
            break
    for function in self.functions('^::clang::DeclContext::getParent', free=False):
        if function.result_type.globalname in [prefix + '::clang::DeclContext *' for prefix in ['', 'class ']]:
            function.is_overloaded = True
            function.clean = False
            break
    for function in self.functions('^::clang::DeclContext::getLexicalParent', free=False):
        if function.result_type.globalname in [prefix + '::clang::DeclContext *' for prefix in ['', 'class ']]:
            function.is_overloaded = True
            function.clean = False
            break
    for function in self.functions('^::clang::DeclContext::getLookupParent', free=False):
        if function.result_type.globalname in [prefix + '::clang::DeclContext *' for prefix in ['', 'class ']]:
            function.is_overloaded = True
            function.clean = False
            break

    self.functions('^::clang::LinkageSpecDecl::getLanguage', free=False).pop().clean = False
    self.enums('(enum |)::clang::LinkageSpecDecl::LanguageIDs').pop().clean = False

    self.functions('^::clang::ValueDecl::getType').pop().clean = False

    self.functions('^::clang::FieldDecl::isMutable').pop().clean = False

    for fct in self.functions('^::clang::FunctionDecl::isDeleted'):
        if fct.localname == 'isDeleted':
            fct.clean = False
    self.functions('^::clang::FunctionDecl::getNumParams').pop().clean = False
    for function in self.functions('^::clang::FunctionDecl::getParamDecl', free=False):
        if function.result_type.globalname in [prefix + '::clang::ParmVarDecl *' for prefix in ['', 'class ']]:
            function.is_overloaded = True
            function.clean = False
    for function in self.functions('^::clang::FunctionDecl::getReturnType', free=False):
        if function.localname == 'getReturnType':
            function.clean = False
            break

    for function in self.functions('^::clang::CXXMethodDecl::isStatic', free=False):
        if function.localname == 'isStatic':
            function.clean = False
            break
    self.functions('^::clang::CXXMethodDecl::isConst', free=False).pop().clean = False
    self.functions('^::clang::CXXMethodDecl::isVolatile', free=False).pop().clean = False
    self.functions('^::clang::CXXMethodDecl::isVirtual', free=False).pop().clean = False

    self.functions('^::clang::TagDecl::isClass', free=False).pop().clean = False
    self.functions('^::clang::TagDecl::isStruct', free=False).pop().clean = False
    self.functions('^::clang::TagDecl::isUnion', free=False).pop().clean = False
    self.functions('^::clang::TagDecl::hasNameForLinkage', free=False).pop().clean = False
    self.functions('^::clang::TagDecl::getTypedefNameForAnonDecl', free=False).pop().clean = False
    for function in self.functions('::clang::TagDecl::isCompleteDefinition', free=False):
        if function.localname == 'isCompleteDefinition':
            function.clean = False
            break

    self.functions('^::clang::CXXRecordDecl::isAbstract', free=False).pop().clean = False
    self.functions('^::clang::CXXRecordDecl::getNumBases', free=False).pop().clean = False
    self.functions('^::clang::CXXRecordDecl::getNumVBases', free=False).pop().clean = False

    self.functions('^::clang::ClassTemplateSpecializationDecl::getTemplateArgs', free=False).pop().clean = False
    self.functions('^::clang::ClassTemplateSpecializationDecl::isExplicitSpecialization', free=False).pop().clean = False
    for function in self.functions('^::clang::ClassTemplateSpecializationDecl::getSpecializedTemplate', free=False):
        if function.localname == 'getSpecializedTemplate':
            function.clean = False
            break
    self.classes('^(class |union |struct |)::clang::TemplateArgumentList').pop().clean = False
    self.functions('^::clang::TemplateArgumentList::get', free=False).pop().clean = False
    self.functions('^::clang::TemplateArgumentList::size', free=False).pop().clean = False

    self.classes('^(class |union |struct |)::clang::TemplateArgument').pop().clean = False
    self.enums('^(enum |)::clang::TemplateArgument::ArgKind').pop().clean = False
    self.functions('^::clang::TemplateArgument::getKind', free=False).pop().clean = False
    self.functions('^::clang::TemplateArgument::getAsType', free=False).pop().clean = False
    self.functions('^::clang::TemplateArgument::getAsDecl', free=False).pop().clean = False
    self.functions('^::clang::TemplateArgument::getIntegralType', free=False).pop().clean = False

    for enum in self.enums():
        if not enum.clean:
            for constant in enum.constants:
                constant.clean = False

    decl = self.classes('^(class |struct |)::clang::Decl$').pop()
    decl.is_copyable = False
    for inheritor in decl.inheritors(True):
        inheritor.is_copyable = False

    diagnostic = self.clean()
    self.mark_invalid_pointers()
    return diagnostic

def static_downcast(self):
    content = "#include <boost/python.hpp>\n"
    declcontext = self.classes('^(class |struct |)::clang::DeclContext$').pop()
    inheritors = [inheritor for inheritor in declcontext.inheritors(True)
            if inheritor.localname in [constant.localname+'Decl'
                for constant in self['enum ::clang::Decl::Kind'].constants]]
    headers = {header.globalname : header
            for header in [inheritor.header
                for inheritor in inheritors+[declcontext]]}.values()
    for header in headers:
        content += '#include '+include(header)+'\n'

    content += '\nnamespace autowig\n{\n'
    for inheritor in inheritors:
        content += '\t' + inheritor.globalname + ' * cast_as_' + lower(inheritor.localname) + '(::clang::DeclContext* decl)\n'
        content += '\t{ return static_cast< ' + inheritor.globalname + ' * >(decl); }\n\n'
    content = content[:-1] + '}\n\n'

    content += CAST
    for inheritor in inheritors:
        content += '\tboost::python::def("cast_as_' + lower(inheritor.localname) + '", ::autowig::cast_as_' + lower(inheritor.localname) +', boost::python::return_value_policy< boost::python::reference_existing_object >());\n'
    content += '}'

    return TOOLING, content

TOOLING = """#include <boost/python.hpp>
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

CAST = """void export_namespace_clang_cast()
{
    std::string clang_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".clang");
    boost::python::object clang_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(clang_name.c_str()))));
    boost::python::scope().attr("clang") = clang_module;
    boost::python::scope clang_scope = clang_module;
    std::string cast_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".cast");
    boost::python::object cast_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(cast_name.c_str()))));
    boost::python::scope().attr("cast") = cast_module;
    boost::python::scope cast_scope = cast_module;"""

