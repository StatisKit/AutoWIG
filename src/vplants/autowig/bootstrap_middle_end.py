import re

from .asg import AbstractSemanticGraph
from .tools import lower

def _bootstrap_middle_end(self, include=None):
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
    self._nodes[node.node]['is_abstract'] = False
    self._nodes[node.node]['_is_copyable'] = True
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

AbstractSemanticGraph._bootstrap_middle_end = _bootstrap_middle_end
del _bootstrap_middle_end
