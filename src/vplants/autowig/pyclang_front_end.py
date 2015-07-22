import time
import warnings
import uuid
from pyclanglite import pyclanglite
from path import path

from .ast import *
from .asg import *
from .tools import remove_regex, split_scopes, remove_templates
from .custom_warnings import NotWrittenFileWarning, ErrorWarning, NoneTypeWarning,  UndeclaredParentWarning, MultipleDeclaredParentWarning, MultipleDefinitionWarning, NoDefinitionWarning, SideEffectWarning, ProtectedFileWarning, InfoWarning, TemplateParentWarning, TemplateParentWarning, AnonymousWarning, AnonymousFunctionWarning, AnonymousFieldWarning, AnonymousClassWarning, NotImplementedWarning, NotImplementedTypeWarning, NotImplementedDeclWarning, NotImplementedParentWarning, NotImplementedOperatorWarning, NotImplementedTemplateWarning

class PyClangDiagnostic(object):

    name = 'pyclang'

    def __init__(self):
        self.parsing = 0.0
        self.translating = 0.0
        self.bootstrapping = 0.0

    @property
    def total(self):
        return self.parsing + self.translating + self.bootstrapping

    def __str__(self):
        string = "Processing: " + str(self.total)
        string += "\n" + " * Parsing: " + str(self.parsing)
        string += "\n" + " * Translating: " + str(self.translating)
        return string

def _pyclang_front_end(self, content, flags, silent=False):
    diagnostic = PyClangDiagnostic()
    prev = time.time()
    tu = pyclanglite.clang.tooling.build_ast_from_code_with_args(content, flags)
    curr = time.time()
    diagnostic.parsing = curr - prev
    prev = time.time()
    with warnings.catch_warnings() as cw:
        if silent:
            warnings.simplefilter('ignore')
        else:
            warnings.simplefilter('always')
        self._pyclang_read_translation_unit(tu)
    curr = time.time()
    diagnostic.parsing = curr - prev
    return diagnostic

AbstractSyntaxTree._pyclang_front_end = _pyclang_front_end
del _pyclang_front_end

def _pyclang_front_end(self, content, flags, bootstrap=False, silent=False):
    diagnostic = PyClangDiagnostic()
    prev = time.time()
    tu = pyclanglite.clang.tooling.build_ast_from_code_with_args(content, flags)
    curr = time.time()
    diagnostic.parsing = curr - prev
    prev = time.time()
    with warnings.catch_warnings() as cw:
        if silent:
            warnings.simplefilter('ignore')
        else:
            warnings.simplefilter('always')
        self._pyclang_read_translation_unit(tu)
    curr = time.time()
    diagnostic.translating = curr - prev
    if bootstrap:
        prev = time.time()
        nodes = 0
        while not nodes == len(self):
            nodes = len(self)
            classes = []
            for cls in self.classes(templated=True, specialized=False):
                if any(not spc.is_complete for spc in cls.specializations(partial=False)):
                    classes.append(cls)
            content = ""
            for header in self.headers(*classes):
                content += "#include \"" + header.globalname + "\"\n"
            content += "\n"
            content += "int main(void)\n{\n"
            for cls in classes:
                for spc in cls.specializations(partial=False):
                    if not spc.is_complete:
                        content += "\tsizeof(" + spc.globalname + ");\n"
            content += "\treturn 0;\n}"
            tu = pyclanglite.clang.tooling.build_ast_from_code_with_args(content, flags)
            with warnings.catch_warnings() as cw:
                if silent:
                    warnings.simplefilter('ignore')
                else:
                    warnings.simplefilter('always')
                self._pyclang_read_translation_unit(tu)
        curr = time.time()
        diagnostic.bootstrapping = curr - prev
    return diagnostic

AbstractSemanticGraph._pyclang_front_end = _pyclang_front_end
del _pyclang_front_end

def _pyclang_read_translation_unit(self, tu):
        """
        """
        self._read = set()
        for child in tu.get_children():
            self._pyclang_read_decl(child)
        del self._read

AbstractSemanticGraph._pyclang_read_translation_unit = _pyclang_read_translation_unit
del _pyclang_read_translation_unit

def _pyclang_read_qualified_type(self, qtype):
    specifiers = ' const' * qtype.is_const_qualified() + ' volatile' *  qtype.is_volatile_qualified()
    ttype = qtype.get_type_ptr_or_null()
    while True:
        if ttype is None:
            raise warnings.warn(qtype.get_as_string(), NoneTypeWarning)
        elif ttype.get_type_class() is pyclanglite.clang._type.TypeClass.Typedef:
            qtype = ttype.get_canonical_type_internal()
            specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + specifiers
            ttype = qtype.get_type_ptr_or_null()
        elif any([ttype.is_structure_or_class_type(), ttype.is_enumeral_type(), ttype.is_union_type()]):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    tag = ttype.get_as_tag_decl()
                    tag = self._pyclang_read_tag(tag, False)
                    return tag[0], specifiers
            except Warning as warning:
                warnings.warn(str(warning), warning.__class__)
                break
        elif ttype.is_pointer_type():
            qtype = ttype.get_pointee_type()
            specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + ' *' + specifiers
            ttype = qtype.get_type_ptr_or_null()
        elif ttype.is_rvalue_reference_type():
            qtype = ttype.get_pointee_type()
            specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + ' &&' + specifiers
            ttype = qtype.get_type_ptr_or_null()
        elif ttype.is_lvalue_reference_type():
            qtype = ttype.get_pointee_type()
            specifiers = ' const' * qtype.is_const_qualified() + ' volatile' * qtype.is_volatile_qualified() + ' &' + specifiers
            ttype = qtype.get_type_ptr_or_null()
        elif ttype.is_builtin_type():
            return self._pyclang_read_builtin_type(ttype), specifiers
        else:
            warnings.warn('\'' + str(ttype.get_type_class()) + '\'', NotImplementedTypeWarning)
            break

AbstractSemanticGraph._pyclang_read_qualified_type = _pyclang_read_qualified_type
del _pyclang_read_qualified_type

def _pyclang_read_builtin_type(self, btype):
    if btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Bool):
        return BoolTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Char_U):
        return UnsignedCharTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Char_S):
        return CharTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Char32):
        return Char32TypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Char16):
        return Char16TypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Double):
        return SignedDoubleTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Float):
        return SignedFloatTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Int):
        return SignedIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.LongLong):
        return SignedLongLongIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Long):
        return SignedLongIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.LongDouble):
        return SignedLongDoubleTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.NullPtr):
        return NullPtrTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Short):
        return SignedShortIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.SChar):
        return SignedCharTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.ULongLong):
        return UnsignedLongLongIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.UChar):
        return UnsignedCharTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.ULong):
        return UnsignedLongIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.UInt):
        return UnsignedIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.UShort):
        return UnsignedShortIntegerTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.Void):
        return VoidTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.WChar_S):
        return WCharTypeProxy.node
    elif btype.is_specific_builtin_type(pyclanglite.clang._builtin_type.Kind.WChar_U):
        return WCharTypeProxy.node
    else:
        warnings.warn('\'' + str(btype.get_class_type()) + '\'', NotImplementedTypeWarning)

AbstractSemanticGraph._pyclang_read_builtin_type = _pyclang_read_builtin_type
del _pyclang_read_builtin_type

def _pyclang_read_enum(self, decl, out=True):
    filename = str(path(str(decl.get_filename())).abspath())
    self.add_file(filename, _language=self._language)
    if decl.get_name() == '':
        children = []
        decls = []
        for child in decl.get_children():
            children.extend(self._pyclang_read_enum_constant(child))
            decls.append(child)
        for childspelling, child in zip(children, decls):
            self._nodes[childspelling]['_header'] = filename
            self._nodes[childspelling]['decl'] = child
        return children
    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                parent = self._pyclang_read_syntaxic_parent(decl)
        except Warning as warning:
            warnings.warn(str(warning) + ' for enum \'' + decl.get_name() + '\'', warning.__class__)
            return []
        else:
            if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
                scope = '::'
                spelling = scope + decl.get_name()
            else:
                scope = self._pyclang_read_decl(parent, out=False)
                if len(scope) == 0:
                    warnings.warn(spelling, UndeclaredParentWarning)
                    return []
                elif len(scope) == 1:
                    scope = scope[0]
                else:
                    warnings.warn(spelling, MultipleDeclaredParentWarning)
                    return []
                spelling = scope + '::' + decl.get_name()
                if spelling.startswith('class '):
                    spelling = spelling[6:]
                elif spelling.startswith('union '):
                    spelling = spelling[6:]
                elif spelling.startswith('struct '):
                    spelling = spelling[7:]
            if not spelling.startswith('enum '):
                spelling = 'enum ' + spelling
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=EnumProxy)
                self._syntax_edges[spelling] = []
                self._syntax_edges[scope].append(spelling)
            if out and not spelling in self._read and not self[spelling].is_complete:
                self._read.add(spelling)
                self._syntax_edges[scope].remove(spelling)
                self._syntax_edges[scope].append(spelling)
                for child in decl.get_children():
                    self._pyclang_read_enum_constant(child)
                if self[spelling].is_complete:
                    self._nodes[spelling]['_header'] = filename
                    self._nodes[spelling]['decl'] = decl
                self._read.remove(spelling)
            return [spelling]

AbstractSemanticGraph._pyclang_read_enum = _pyclang_read_enum
del _pyclang_read_enum

def _pyclang_read_enum_constant(self, decl):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            parent = self._pyclang_read_context_parent(decl)
    except Warning as warning:
        warnings.warn(str(warning) + ' for enum constant \'' + decl.get_name() + '\'', warning.__class__)
        return []
    else:
        if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
            scope = '::'
            spelling = scope + decl.get_name()
        else:
            scope = self._pyclang_read_decl(parent, out=False)
            if len(scope) == 0:
                warnings.warn(spelling, UndeclaredParentWarning)
                return []
            elif len(scope) == 1:
                scope = scope[0]
            else:
                warnings.warn(spelling, MultipleDeclaredParentWarning)
                return []
            spelling = scope + '::' + decl.get_name()
            if spelling.startswith('enum '):
                spelling = spelling[5:]
        if not spelling in self._nodes:
            self._nodes[spelling] = dict(proxy=EnumConstantProxy)
            self._syntax_edges[scope].append(spelling)
        return [spelling]

AbstractSemanticGraph._pyclang_read_enum_constant = _pyclang_read_enum_constant
del _pyclang_read_enum_constant

def _pyclang_read_typedef(self, typedef):
    return []

AbstractSemanticGraph._pyclang_read_typedef = _pyclang_read_typedef
del _pyclang_read_typedef

def _pyclang_read_variable(self, decl):
    if isinstance(decl, (pyclanglite.clang.VarTemplateDecl, pyclanglite.clang.VarTemplateSpecializationDecl)) or decl.get_type().get_type_ptr_or_null().get_type_class() is pyclanglite.clang._type.TypeClass.TemplateTypeParm:
        return []
    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                parent = self._pyclang_read_context_parent(decl)
                if isinstance(parent, (pyclanglite.clang.TagDecl, pyclanglite.clang.ClassTemplateDecl)):
                    warnings.warn('' + decl.get_name() + '\'', UserWarning)
        except Warning as warning:
            warnings.warn(str(warning) + ' for variable \'' + decl.get_name() + '\'', warning.__class__)
            return []
        else:
            if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
                scope = '::'
                spelling = scope + decl.get_name()
            else:
                scope = self._pyclang_read_decl(parent, out=False)
                if len(scope) == 0:
                    warnings.warn(decl.get_name(), UndeclaredParentWarning)
                    return []
                elif len(scope) == 1:
                    scope = scope[0]
                else:
                    warnings.warn(spelling, MultipleDeclaredParentWarning)
                    return []
                spelling = scope + '::' + decl.get_name()
            try:
                with warnings.catch_warnings() as warning:
                    warnings.simplefilter("error")
                    target, specifiers = self._pyclang_read_qualified_type(decl.get_type())
                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            except Warning as warning:
                warnings.warn(str(warning) + ' for variable \'' + spelling + '\'', warning.__class__)
                return []
            else:
                if not spelling in self._nodes:
                    self._nodes[spelling] = dict(proxy=VariableProxy)
                    self._syntax_edges[scope].append(spelling)
                filename = str(path(str(decl.get_filename())).abspath())
                self.add_file(filename, _language=self._language)
                self._nodes[spelling]['_header'] = filename
                self._nodes[spelling]['decl'] = decl
                return [spelling]

AbstractSemanticGraph._pyclang_read_variable = _pyclang_read_variable
del _pyclang_read_variable

def _pyclang_read_function(self, decl):
    if isinstance(decl, pyclanglite.clang.FunctionTemplateDecl) or decl.is_implicit() or decl.is_deleted():
        return []
    if decl.get_name() == '':
        warnings.warn('', AnonymousFunctionWarning)
        return []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            if isinstance(decl, pyclanglite.clang.CXXMethodDecl):
                parent = self._pyclang_read_lexical_parent(decl)
                if isinstance(parent, pyclanglite.clang.NamespaceDecl):
                    return []
            parent = self._pyclang_read_syntaxic_parent(decl)
    except Warning as warning:
        warnings.warn(str(warning) + ' for function \'' + decl.get_name() + '\'', warning.__class__)
        return []
    else:
        if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
            scope = '::'
            spelling = scope + decl.get_name()
        else:
            scope = self._pyclang_read_decl(parent, out=False)
            if len(scope) == 0:
                warnings.warn(spelling, UndeclaredParentWarning)
                return []
            elif len(scope) == 1:
                scope = scope[0]
            else:
                warnings.warn(spelling, MultipleDeclaredParentWarning)
                return []
            spelling =  scope + '::' + decl.get_name()
        if spelling.startswith('class '):
            spelling = spelling[6:]
        elif spelling.startswith('union '):
            spelling = spelling[6:]
        elif spelling.startswith('struct '):
            spelling = spelling[7:]
        if not isinstance(decl, pyclanglite.clang.CXXDestructorDecl):
            spelling += '::' + str(uuid.uuid5(uuid.NAMESPACE_X500, decl.get_mangling()))
        if not spelling in self._nodes:
            if isinstance(decl, pyclanglite.clang.CXXMethodDecl):
                if isinstance(decl, pyclanglite.clang.CXXConversionDecl):
                    warnings.warn(pyclanglite.clang.CXXConversionDecl.__class__.__name__.split('.')[-1] + ' for function \'' + spelling + '\'',
                            NotImplementedDeclWarning)
                    return []
                elif isinstance(self[scope], NamespaceProxy):
                    return []
                else:
                    if not isinstance(decl, pyclanglite.clang.CXXDestructorDecl):
                        self._syntax_edges[spelling] = []
                        try:
                            with warnings.catch_warnings() as warning:
                                warnings.simplefilter("error")
                                setted = set()
                                for index, child in enumerate(decl.get_children()):
                                    childspelling = spelling + child.spelling()
                                    if childspelling.endswith('::'):
                                        childspelling += 'parm_' + str(index)
                                    if childspelling in setted:
                                        warnings.warn('')
                                    else:
                                        setted.add(childspelling)
                                    target, specifiers = self._pyclang_read_qualified_type(child.get_type())
                                    self._type_edges[childspelling] = dict(target=target,
                                            specifiers=specifiers)
                                    self._nodes[childspelling] = dict(proxy=VariableProxy)
                                    self._syntax_edges[spelling].append(childspelling)
                        except Warning as warning:
                            message = str(warning) + ' for parameter \'' + childspelling + '\''
                            self._syntax_edges.pop(spelling)
                            for index, child in enumerate(decl.get_children()):
                                childspelling = spelling + child.spelling()
                                if childspelling.endswith('::'):
                                    childspelling += 'parm_' + str(index)
                                self._nodes.pop(childspelling, None)
                                self._type_edges.pop(childspelling, None)
                            warnings.warn(message,
                                    warning.__class__)
                            return []
                        else:
                            if not isinstance(decl, pyclanglite.clang.CXXConstructorDecl):
                                try:
                                    with warnings.catch_warnings() as warning:
                                        warnings.simplefilter("error")
                                        target, specifiers = self._pyclang_read_qualified_type(decl.get_return_type())
                                except Warning as warning:
                                    self._syntax_edges.pop(spelling)
                                    for index, child in enumerate(decl.get_children()):
                                        childspelling = spelling + child.spelling()
                                        if childspelling.endswith('::'):
                                            childspelling += 'parm_' + str(index)
                                        self._nodes.pop(childspelling, None)
                                        self._type_edges.pop(childspelling, None)
                                    warnings.warn(str(warning) + ' for function \'' + spelling + '\' return type',
                                            warning.__class__)
                                    return []
                                else:
                                    self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                                    self._nodes[spelling] = dict(proxy=MethodProxy,
                                            is_static=decl.is_static(),
                                            is_const=decl.is_const(),
                                            is_volatile=decl.is_volatile(),
                                            is_virtual=decl.is_virtual(),
                                            decl=decl)
                            else:
                                self._nodes[spelling] = dict(proxy=ConstructorProxy,
                                        is_virtual=decl.is_virtual(),
                                        decl=decl)
                            self._syntax_edges[scope].append(spelling)
                            return [spelling]
                    else:
                        if not spelling in self._nodes:
                            self._nodes[spelling] = dict(proxy=DestructorProxy,
                                    virtual=decl.is_virtual(),
                                    decl=decl)
                            self._syntax_edges[scope].append(spelling)
                        return [spelling]
            else:
                self._syntax_edges[spelling] = []
                try:
                    with warnings.catch_warnings() as warning:
                        warnings.simplefilter("error")
                        setted = set()
                        for index, child in enumerate(decl.get_children()):
                            childspelling = spelling + child.spelling()
                            if childspelling.endswith('::'):
                                childspelling += 'parm_' + str(index)
                            if childspelling in setted:
                                warnings.warn('')
                            else:
                                setted.add(childspelling)
                            target, specifiers = self._pyclang_read_qualified_type(child.get_type())
                            self._type_edges[childspelling] = dict(target=target,
                                    specifiers=specifiers)
                            self._nodes[childspelling] = dict(proxy=VariableProxy)
                            self._syntax_edges[spelling].append(childspelling)
                except Warning as warning:
                    message = str(warning) + ' for parameter \'' + childspelling + '\''
                    self._syntax_edges.pop(spelling)
                    for index, child in enumerate(decl.get_children()):
                        childspelling = spelling + child.spelling()
                        if childspelling.endswith('::'):
                            childspelling += 'parm_' + str(index)
                        self._nodes.pop(childspelling, None)
                        self._type_edges.pop(childspelling, None)
                    warnings.warn(message,
                            warning.__class__)
                    return []
                else:
                    try:
                        with warnings.catch_warnings() as warning:
                            warnings.simplefilter("error")
                            target, specifiers = self._pyclang_read_qualified_type(decl.get_return_type())
                    except Warning as warning:
                        message = str(warning) + ' for function \'' + spelling + '\''
                        self._syntax_edges.pop(spelling)
                        for index, child in enumerate(decl.get_children()):
                            childspelling = spelling + child.spelling()
                            if childspelling.endswith('::'):
                                childspelling += 'parm_' + str(index)
                            self._nodes.pop(childspelling, None)
                            self._type_edges.pop(childspelling, None)
                        self._type_edges.pop(spelling, None)
                        warnings.warn(message,
                                warning.__class__)
                        return []
                    else:
                        self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
                        self._nodes[spelling] = dict(proxy=FunctionProxy,
                                decl=decl)
                        self._syntax_edges[scope].append(spelling)
                        filename = str(path(str(decl.get_filename())).abspath())
                        self.add_file(filename, _language=self._language)
                        self._nodes[spelling]['_header'] = filename
                        return [spelling]

AbstractSemanticGraph._pyclang_read_function = _pyclang_read_function
del _pyclang_read_function

def _pyclang_read_field(self, decl):
    if decl.get_name() == '':
        warnings.warn('', AnonymousFieldWarning)
        return []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            parent = self._pyclang_read_context_parent(decl)
    except Warning as warning:
        warnings.warn(str(warning) + ' for field \'' + decl.get_name() + '\'', warning.__class__)
        return []
    else:
        if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
            scope = '::'
            spelling = scope + decl.get_name()
        else:
            scope = self._pyclang_read_decl(parent, out=False)
            if len(scope) == 0:
                warnings.warn(spelling, UndeclaredParentWarning)
                return []
            elif len(scope) == 1:
                scope = scope[0]
            else:
                warnings.warn(spelling, MultipleDeclaredParentWarning)
                return []
            spelling = scope + '::' + decl.get_name()
            if spelling.startswith('class '):
                spelling = spelling[6:]
            elif spelling.startswith('union '):
                spelling = spelling[6:]
            elif spelling.startswith('struct '):
                spelling = spelling[7:]
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = self._pyclang_read_qualified_type(decl.get_type())
        except Warning as warning:
            warnings.warn(str(warning) + ' for field \'' + spelling + '\'', warning.__class__)
            return []
        else:
            self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
            self._nodes[spelling] = dict(proxy=FieldProxy,
                    is_mutable=decl.is_mutable(),
                    is_static=False, # TODO
                    decl=decl)
            self._syntax_edges[scope].append(spelling)
            return [spelling]

AbstractSemanticGraph._pyclang_read_field = _pyclang_read_field
del _pyclang_read_field

def _pyclang_read_class_template(self, decl, out=True):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            parent = self._pyclang_read_context_parent(decl)
    except Warning as warning:
        warnings.warn(str(warning) + ' for class \'' + decl.get_name() + '\'', warning.__class__)
        return []
    else:
        if isinstance(parent, (pyclanglite.clang.ClassTemplateDecl, pyclanglite.clang.ClassTemplatePartialSpecializationDecl)):
            warnings.warn("", UserWarning)
            return []
        elif isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
            scope = '::'
            spelling = 'class ' + scope + decl.get_name()
        else:
            scope = self._pyclang_read_decl(parent, out=False)
            if len(scope) == 0:
                warnings.warn(spelling, UndeclaredParentWarning)
                return []
            elif len(scope) == 1:
                scope = scope[0]
            else:
                warnings.warn(spelling, MultipleDeclaredParentWarning)
                return []
            spelling = scope + '::' + decl.get_name()
            if spelling.startswith('union '):
                spelling = 'class ' + spelling[6:]
            elif spelling.startswith('struct '):
                spelling = 'class ' + spelling[7:]
            elif not spelling.startswith('class '):
                spelling = 'class ' + spelling
        if not spelling in self._nodes:
            self._nodes[spelling] = dict(proxy=ClassTemplateProxy,
                    decl=decl)
            self._syntax_edges[scope].append(spelling)
            self._specialization_edges[spelling] = set()
            filename = str(path(str(decl.get_filename())).abspath())
            self.add_file(filename, _language=self._language)
            self._nodes[spelling]['_header'] = filename
        if out:
            for child in decl.get_children():
                self._specialization_edges[spelling].update(set(self._pyclang_read_tag(child)))
        return [spelling]

AbstractSemanticGraph._pyclang_read_class_template = _pyclang_read_class_template
del _pyclang_read_class_template

def _pyclang_read_tag(self, decl, out=True):
    if isinstance(decl, pyclanglite.clang.EnumDecl):
        return self._pyclang_read_enum(decl)
    elif isinstance(decl, pyclanglite.clang.ClassTemplatePartialSpecializationDecl):
        # TODO
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                parent = self._pyclang_read_context_parent(decl)
        except Warning as warning:
            warnings.warn(str(warning) + ' for class \'' + decl.get_typedef_name_for_anon_decl().get_name() + '\'', warning.__class__)
            return []
        else:
            if isinstance(parent, (pyclanglite.clang.ClassTemplateDecl, pyclanglite.clang.ClassTemplatePartialSpecializationDecl)):
                warnings.warn("", UserWarning)
                return []
            elif isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
                scope = '::'
                spelling = scope + decl.get_name()
            else:
                scope = self._pyclang_read_decl(parent, out=False)
                if len(scope) == 0:
                    warnings.warn(spelling, UndeclaredParentWarning)
                    return []
                elif len(scope) == 1:
                    scope = scope[0]
                else:
                    warnings.warn(spelling, MultipleDeclaredParentWarning)
                    return []
                spelling = scope + '::' + decl.get_name()
                if spelling.startswith('class '):
                    spelling = spelling[6:]
                elif spelling.startswith('union '):
                    spelling = spelling[6:]
                elif spelling.startswith('struct '):
                    spelling = spelling[7:]
            if decl.is_class():
                spelling = 'class ' + spelling
            elif decl.is_struct():
                spelling = 'struct ' + spelling
            elif decl.is_union():
                spelling = 'union ' + spelling
            else:
                warnings.warn(spelling, NotImplementedDeclWarning)
                return []
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=ClassTemplatePartialSpecializationProxy,
                        decl=decl)
                specialize = self._pyclang_read_class_template(decl.get_specialized_template(), out=False)[0]
                self._specialization_edges[specialize].add(spelling)
                self._syntax_edges[scope].append(spelling)
                filename = str(path(str(decl.get_filename())).abspath())
                self.add_file(filename, _language=self._language)
                self._nodes[spelling]['_header'] = filename
            return [spelling]
    if not decl.has_name_for_linkage():
        warnings.warn('', AnonymousClassWarning)
        return []
    if not decl.get_typedef_name_for_anon_decl() is None:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                parent = self._pyclang_read_syntaxic_parent(decl)
        except Warning as warning:
            warnings.warn(str(warning) + ' for class \'' + decl.get_typedef_name_for_anon_decl().get_name() + '\'', warning.__class__)
            return []
        else:
            if isinstance(parent, (pyclanglite.clang.ClassTemplateDecl, pyclanglite.clang.ClassTemplatePartialSpecializationDecl)):
                warnings.warn("", UserWarning)
                # TODO
                return []
            elif isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
                scope = '::'
                spelling = scope + decl.get_typedef_name_for_anon_decl().get_name()
            else:
                scope = self._pyclang_read_decl(parent, out=False)
                if len(scope) == 0:
                    warnings.warn(spelling, UndeclaredParentWarning)
                    return []
                elif len(scope) == 1:
                    scope = scope[0]
                else:
                    warnings.warn(spelling, MultipleDeclaredParentWarning)
                    return []
                spelling = scope + '::' + decl.get_typedef_name_for_anon_decl().get_name()
                if spelling.startswith('class '):
                    spelling = spelling[6:]
                elif spelling.startswith('union '):
                    spelling = spelling[6:]
                elif spelling.startswith('struct '):
                    spelling = spelling[7:]
    elif decl.get_name() == '':
        warnings.warn('in scope \'' + scope + '\'', AnonymousClassWarning)
        return []
    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                parent = self._pyclang_read_syntaxic_parent(decl)
        except Warning as warning:
            warnings.warn(str(warning) + ' for class \'' + decl.get_typedef_name_for_anon_decl().get_name() + '\'', warning.__class__)
            return []
        else:
            if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
                scope = '::'
                spelling = scope + decl.get_name()
            else:
                scope = self._pyclang_read_decl(parent, out=False)
                if len(scope) == 0:
                    warnings.warn(spelling, UndeclaredParentWarning)
                    return []
                elif len(scope) == 1:
                    scope = scope[0]
                else:
                    warnings.warn(spelling, MultipleDeclaredParentWarning)
                    return []
                spelling = scope + '::' + decl.get_name()
                if spelling.startswith('class '):
                    spelling = spelling[6:]
                elif spelling.startswith('union '):
                    spelling = spelling[6:]
                elif spelling.startswith('struct '):
                    spelling = spelling[7:]
            if decl.is_class():
                spelling = 'class ' + spelling
            elif decl.is_struct():
                spelling = 'struct ' + spelling
            elif decl.is_union():
                spelling = 'union ' + spelling
            else:
                warnings.warn(spelling, NotImplementedDeclWarning)
                return []
    if not spelling in self._nodes:
        if decl.is_class():
            default_access = 'private'
        else:
            default_access = 'public'
        if isinstance(decl, pyclanglite.clang.ClassTemplateSpecializationDecl):
            self._nodes[spelling] = dict(proxy=ClassTemplateSpecializationProxy,
                _scope = scope,
                default_access=default_access,
                is_abstract=False,
                _is_copyable=True,
                is_complete=False,
                decl=decl)
            specialize = self._pyclang_read_class_template(decl.get_specialized_template(), out=False)[0]
            self._specialization_edges[specialize].add(spelling)
            self._syntax_edges[spelling] = []
            self._base_edges[spelling] = []
            self._syntax_edges[scope].append(spelling)
            self._template_edges[spelling] = []
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    templates = decl.get_template_args()
                    for template in [templates.get(index) for index in range(templates.size())]:
                        if template.get_kind() is pyclanglite.clang._template_argument.ArgKind.Type:
                            target, specifiers = self._pyclang_read_qualified_type(template.get_as_type())
                            self._template_edges[spelling].append(dict(target = target, specifiers = specifiers))
                        elif template.get_kind() is pyclanglite.clang._template_argument.ArgKind.Declaration:
                            target, specifiers = self._pyclang_read_qualified_type(template.get_as_decl().get_type())
                            self._template_edges[spelling].append(dict(target = target, specifiers = specifiers))
                        elif template.get_kind() is pyclanglite.clang._template_argument.ArgKind.Integral:
                            target, specifiers = self._pyclang_read_qualified_type(template.get_integral_type())
                            self._template_edges[spelling].append(dict(target = target, specifiers = specifiers))
                        else:
                            warnings.warn(str(template.get_kind()), NotImplementedTemplateWarning)
            except Warning as warning:
                self._nodes.pop(spelling)
                self._specialization_edges[specialize].remove(spelling)
                self._syntax_edges.pop(spelling)
                self._base_edges.pop(spelling)
                self._syntax_edges[scope].remove(spelling)
                self._template_edges.pop(spelling)
                warnings.warn(str(warning) + 'nested', warning.__class__)
                return []
        else:
            self._nodes[spelling] = dict(proxy=ClassProxy,
                _scope = scope,
                default_access=default_access,
                is_abstract=False,
                _is_copyable=True,
                is_complete=False,
                decl=decl)
            self._syntax_edges[spelling] = []
            self._base_edges[spelling] = []
            self._syntax_edges[scope].append(spelling)
    if out and not spelling in self._read and not self[spelling].is_complete and decl.is_complete_definition():
        self._read.add(spelling)
        self._syntax_edges[scope].remove(spelling)
        self._syntax_edges[scope].append(spelling)
        if isinstance(decl, pyclanglite.clang.CXXRecordDecl):
            self._nodes[spelling]['is_abstract'] = decl.is_abstract()
            self._nodes[spelling]['_is_copyable'] = decl.is_copyable()
        else:
            self._nodes[spelling]['is_abstract'] = False
            self._nodes[spelling]['_is_copyable'] = True
        self._nodes[spelling]['is_complete'] = True
        self._base_edges[spelling] = []
        for base in decl.get_bases():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    basespelling, specifiers = self._pyclang_read_qualified_type(base.get_type())
                    self._base_edges[spelling].append(dict(base=self[basespelling].node,
                        access=str(base.get_access_specifier()).strip('AS_'),
                        is_virtual=False))
            except Warning as warning:
                pass
                #warnings.warn(str(warning), warning.__class__)
        for base in decl.get_virtual_bases():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    basespelling, specifiers = self._pyclang_read_qualified_type(base.get_type())
                    self._base_edges[spelling].append(dict(base=self[basespelling].node,
                        access=str(base.get_access_specifier()).strip('AS_'),
                        is_virtual=True))
            except Warning as warning:
                pass
                #warnings.warn(str(warning), warning.__class__)
        for child in decl.get_children():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    access = str(child.get_access_unsafe()).strip('AS_')
                    for childspelling in self._pyclang_read_decl(child):
                        self._nodes[childspelling]["access"] = access
                        dict.pop(self._nodes[childspelling], "_header", None)
            except Warning as warning:
                pass
                #warnings.warn(str(warning), warning.__class__)
        self._nodes[spelling]['is_complete'] = len(self._syntax_edges[spelling])+len(self._base_edges[spelling]) > 0
        if self[spelling].is_complete:
            filename = str(path(str(decl.get_filename())).abspath())
            self.add_file(filename, _language=self._language)
            self._nodes[spelling]['_header'] = filename
            self._nodes[spelling]['decl'] = decl
        self._read.remove(spelling)
    #if isinstance(decl, pyclanglite.clang.ClassTemplateSpecializationDecl) and not decl.is_explicit_specialization():
    #    tpl = decl.get_specialized_template()
    #    if not tpl is None:
    #        filename = str(path(str(tpl.get_filename())).abspath())
    #        self.add_file(filename, _language=self._language)
    #        self._nodes[spelling]['_header'] = filename
    #        self._nodes[spelling]['decl'] = decl
    return [spelling]

AbstractSemanticGraph._pyclang_read_tag = _pyclang_read_tag
del _pyclang_read_tag

def _pyclang_read_typedef(self, decl):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            parent = self._pyclang_read_context_parent(decl)
            if isinstance(parent, (pyclanglite.clang.TagDecl, pyclanglite.clang.ClassTemplateDecl)):
                warnings.warn('' + decl.get_name() + '\'', UserWarning)
    except Warning as warning:
        warnings.warn(str(warning) + ' for variable \'' + decl.get_name() + '\'', warning.__class__)
        return []
    else:
        if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
            scope = '::'
            spelling = scope + decl.get_name()
        else:
            scope = self._pyclang_read_decl(parent, out=False)
            if len(scope) == 0:
                warnings.warn(decl.get_name(), UndeclaredParentWarning)
                return []
            elif len(scope) == 1:
                scope = scope[0]
            else:
                warnings.warn(spelling, MultipleDeclaredParentWarning)
                return []
            spelling = scope + '::' + decl.get_name()
        try:
            with warnings.catch_warnings() as warning:
                warnings.simplefilter("error")
                target, specifiers = self._pyclang_read_qualified_type(decl.get_underlying_type())
                self._type_edges[spelling] = dict(target=target, specifiers=specifiers)
        except Warning as warning:
            warnings.warn(str(warning) + ' for variable \'' + spelling + '\'', warning.__class__)
            return []
        else:
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=TypedefProxy)
                self._syntax_edges[scope].append(spelling)
            filename = str(path(str(decl.get_filename())).abspath())
            self.add_file(filename, _language=self._language)
            self._nodes[spelling]['_header'] = filename
            self._nodes[spelling]['decl'] = decl
            return [spelling]

AbstractSemanticGraph._pyclang_read_typedef = _pyclang_read_typedef
del _pyclang_read_typedef

def _pyclang_read_namespace(self, decl, out=True):
    if decl.get_name() == '':
        children = []
        for child in decl.get_children():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    children.extend(self._pyclang_read_decl(child))
            except:
                pass
        return children
    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                parent = self._pyclang_read_syntaxic_parent(decl)
        except Warning as warning:
            warnings.warn(str(warning) + ' for namespace \'' + decl.get_name() + '\'', warning.__class__)
            return []
        else:
            if isinstance(parent, pyclanglite.clang.TranslationUnitDecl):
                scope = '::'
                spelling = scope + decl.get_name()
            else:
                scope = self._pyclang_read_decl(parent, out=False)
                if len(scope) == 0:
                    warnings.warn(spelling, UndeclaredParentWarning)
                    return []
                elif len(scope) == 1:
                    scope = scope[0]
                else:
                    warnings.warn(spelling, MultipleDeclaredParentWarning)
                    return []
                spelling = scope + '::' + decl.get_name()
            if not spelling in self._nodes:
                self._nodes[spelling] = dict(proxy=NamespaceProxy)
                self._syntax_edges[spelling] = []
            if not spelling in self._syntax_edges[scope]:
                self._syntax_edges[scope].append(spelling)
            if out and not spelling in self._read:
                self._read.add(spelling)
                for child in decl.get_children():
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter('error')
                            self._pyclang_read_decl(child)
                    except:
                        pass
                self._read.remove(spelling)
            return [spelling]

AbstractSemanticGraph._pyclang_read_namespace = _pyclang_read_namespace
del _pyclang_read_namespace

def _pyclang_read_decl(self, decl, **kwargs):
    """
    """
    if isinstance(decl, pyclanglite.clang.LinkageSpecDecl):
        language = self._language
        if decl.get_language() is pyclanglite.clang._linkage_spec_decl.LanguageIDs.lang_c:
            self._language = 'c'
        else:
            self._language = 'c++'
        children = []
        for child in decl.get_children():
            children = self._pyclang_read_decl(child, **kwargs)
        self._language = language
        return children
    elif isinstance(decl, pyclanglite.clang.VarDecl):
        return self._pyclang_read_variable(decl, **kwargs)
    elif isinstance(decl, pyclanglite.clang.FunctionDecl):
        return self._pyclang_read_function(decl, **kwargs)
    elif isinstance(decl, pyclanglite.clang.FieldDecl):
        return self._pyclang_read_field(decl, **kwargs)
    elif isinstance(decl, pyclanglite.clang.TagDecl):
        return self._pyclang_read_tag(decl, **kwargs)
    elif isinstance(decl, pyclanglite.clang.ClassTemplateDecl):
        return self._pyclang_read_class_template(decl, **kwargs)
    elif isinstance(decl, pyclanglite.clang.NamespaceDecl):
        return self._pyclang_read_namespace(decl, **kwargs)
    elif isinstance(decl, pyclanglite.clang.TypedefDecl):
        return self._pyclang_read_typedef(decl, **kwargs)
    elif isinstance(decl, (pyclanglite.clang.AccessSpecDecl,
        pyclanglite.clang.BlockDecl, pyclanglite.clang.CapturedDecl,
        pyclanglite.clang.ClassScopeFunctionSpecializationDecl,
        pyclanglite.clang.EmptyDecl, pyclanglite.clang.FileScopeAsmDecl,
        pyclanglite.clang.FriendDecl, pyclanglite.clang.FriendTemplateDecl,
        pyclanglite.clang.StaticAssertDecl, pyclanglite.clang.LabelDecl,
        pyclanglite.clang.NamespaceAliasDecl, pyclanglite.clang.TemplateDecl,
        pyclanglite.clang.TemplateTypeParmDecl, pyclanglite.clang.UsingDecl,
        pyclanglite.clang.UsingDirectiveDecl, pyclanglite.clang.UsingShadowDecl,
        pyclanglite.clang.IndirectFieldDecl, pyclanglite.clang.UnresolvedUsingValueDecl, pyclanglite.clang.TypedefNameDecl)):
        return []
    else:
        warnings.warn(decl.__class__.__name__, NotImplementedDeclWarning) #.split('.')[-1]
        return []

AbstractSemanticGraph._pyclang_read_decl = _pyclang_read_decl
del _pyclang_read_decl

def _pyclang_read_lexical_parent(self, decl):
    return self._pyclang_read_parent(decl.get_lexical_parent())

AbstractSemanticGraph._pyclang_read_lexical_parent = _pyclang_read_lexical_parent
del _pyclang_read_lexical_parent

def _pyclang_read_syntaxic_parent(self, decl):
    return self._pyclang_read_parent(decl.get_parent())

AbstractSemanticGraph._pyclang_read_syntaxic_parent = _pyclang_read_syntaxic_parent
del _pyclang_read_syntaxic_parent

def _pyclang_read_context_parent(self, decl):
    return self._pyclang_read_parent(decl.get_decl_context())

AbstractSemanticGraph._pyclang_read_context_parent = _pyclang_read_context_parent
del _pyclang_read_context_parent

def _pyclang_read_parent(self, parent):
    kind = parent.get_decl_kind()
    if kind is pyclanglite.clang._decl.Kind.Namespace:
        parent = pyclanglite.clang.cast.cast_as_namespace_decl(parent)
        if parent.get_name() == '':
            parent = self._pyclang_read_parent(parent.get_parent())
        return parent
    elif kind in [pyclanglite.clang._decl.Kind.CXXRecord, pyclanglite.clang._decl.Kind.Record, pyclanglite.clang._decl.Kind.firstCXXRecord, pyclanglite.clang._decl.Kind.firstClassTemplateSpecialization, pyclanglite.clang._decl.Kind.firstRecord]:
        parent = pyclanglite.clang.cast.cast_as_record_decl(parent)
        #if parent.get_name() == '':
        #    parent = self._pyclang_read_parent(parent.get_parent())
        return parent
    elif kind in [pyclanglite.clang._decl.Kind.Enum]:
        parent = pyclanglite.clang.cast.cast_as_enum_decl(parent)
        if parent.get_name() == '':
            parent = self._pyclang_read_parent(parent.get_parent())
        return parent
    elif kind is pyclanglite.clang._decl.Kind.LinkageSpec:
        return self._pyclang_read_parent(self._pyclang_read_parent(parent.get_parent()))
    elif kind in [pyclanglite.clang._decl.Kind.TranslationUnit, pyclanglite.clang._decl.Kind.lastDecl]:
        return pyclanglite.clang.cast.cast_as_translation_unit_decl(parent)
    elif kind in [pyclanglite.clang._decl.Kind.ClassTemplatePartialSpecialization, pyclanglite.clang._decl.Kind.firstTemplate, pyclanglite.clang._decl.Kind.firstVarTemplateSpecialization, pyclanglite.clang._decl.Kind.lastTag, pyclanglite.clang._decl.Kind.lastRedeclarableTemplate, pyclanglite.clang._decl.Kind.lastTemplate]:
        warnings.warn('', TemplateParentWarning)
    else:
        warnings.warn(kind, NotImplementedParentWarning)

AbstractSemanticGraph._pyclang_read_parent = _pyclang_read_parent
del _pyclang_read_parent

def _pyclang_read_translation_unit(self, tu):
    self._nodes = dict()
    self._children = dict()
    self._nodes[0] = tu
    self._children[0] = []
    self._node = 1
    for child in tu.get_children():
        self._children[0].append(self._pyclang_read_decl(child))
    del self._node

AbstractSyntaxTree._pyclang_read_translation_unit = _pyclang_read_translation_unit
del _pyclang_read_translation_unit

def _pyclang_read_decl(self, decl):
    self._node += 1
    node = self._node
    self._nodes[node] = decl
    self._children[node] = []
    if hasattr(decl, 'get_children'):
        for child in decl.get_children():
            self._children[node].append(self._pyclang_read_decl(child))
    return node

AbstractSyntaxTree._pyclang_read_decl = _pyclang_read_decl
del _pyclang_read_decl
