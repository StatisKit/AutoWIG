"""
"""
from clang.cindex import TranslationUnit, Type, Cursor, CursorKind, Type, TypeKind, AccessSpecifier
import itertools
import re
from numpy import cumsum

from ..tools import AST, parse_file

__mapping__ = dict()

def Header(obj):
    """
    """
    return HTML(highlight(obj._repr_header_(), CppLexer(), HtmlFormatter(full = True)))

class InterfaceType(object):

    def __init__(self, itype):
        if not isinstance(itype, Type):
            raise TypeError('`itype` parameter')
        if itype.kind in [TypeKind.TYPEDEF, TypeKind.LVALUEREFERENCE]:
            raise ValueError('`rtype` parameter')
        self.type = itype
        self.const = itype.is_const_qualified()
        self.spelling = itype.spelling

    def _repr_header_(self):
        return self.spelling

    def __str__(self):
        return self.spelling

class InterfaceTypedefType(object):

    def __init__(self, ttype):
        if not isinstance(ttype, Type):
            raise TypeError('`ttype` parameter')
        if not ttype.kind is TypeKind.TYPEDEF:
            raise ValueError('`rtype` parameter')
        self.type = TypeFactory(ttype.get_declaration()).type
        self.spelling = ttype.spelling

    def _repr_header_(self):
        return self.spelling

    def __str__(self):
        return self.spelling

class InterfaceLValueReferenceType(object):

    def __init__(self, rtype):
        if not isinstance(rtype, Type):
            raise TypeError('`rtype` parameter')
        if not rtype.kind is TypeKind.LVALUEREFERENCE:
            raise ValueError('`rtype` parameter')
        self.spelling = rtype.spelling
        self.type = TypeFactory(rtype.get_pointee())
        self.const = rtype.is_const_qualified()

    def _repr_header_(self):
        string = self.type._repr_header_()
        if self.const:
            string += " const"
        return string + " &"

    def __str__(self):
        string = str(self.type)
        if self.const:
            string = "const " + string
        return string +" &"

class InterfacePointerType(object):

    def __init__(self, ptype):
        if not isinstance(ptype, Type):
            raise TypeError('`ptype` parameter')
        if not ptype.kind is TypeKind.POINTER:
            raise ValueError('`ptype` parameter')
        self.spelling = ptype.spelling
        self.type = TypeFactory(ptype.get_pointee())
        self.const = ptype.is_const_qualified()

    def _repr_header_(self):
        string = self.type._repr_header_()+" *"
        if self.const:
            string += " const"
        return string

    def __str__(self):
        string = str(self.type)
        if self.const:
            string += " const"
        return string+" *"

def TypeFactory(type):
    if not isinstance(type, (Cursor, Type)):
        raise TypeError('`type` parameter')
    if isinstance(type, Cursor):
        if type.kind is CursorKind.TYPE_REF:
            return TypeRefHeaderInterface(type)
        elif type.kind is CursorKind.TYPEDEF_DECL:
            return TypedefHeaderInterface(type)
        elif type.kind is CursorKind.TYPE_ALIAS_DECL:
            return UsingHeaderInterface(type)
        elif type.kind is CursorKind.CLASS_DECL:
            return ClassHeaderInterface(type)
        elif type.kind is CursorKind.STRUCT_DECL:
            return StructHeaderInterface(type)
        elif type.kind is CursorKind.UNION_DECL:
            return UnionHeaderInterface(type)
        elif type.kind is CursorKind.TEMPLATE_TYPE_PARAMETER:
            return TemplateTypeHeaderInterface(type)
    elif isinstance(type, Type):
        if type.kind is TypeKind.LVALUEREFERENCE:
            return InterfaceLValueReferenceType(type)
        elif type.kind is TypeKind.POINTER:
            return InterfacePointerType(type)
        elif type.kind is TypeKind.TYPEDEF:
            return InterfaceTypedefType(type)
        else:
            return InterfaceType(type)

class HeaderInterface(object):

    def __init__(self, cursor):
        if not isinstance(cursor, Cursor):
            raise TypeError('`cursor` parameter')
        if not cursor.location.file is None:
            self.file = cursor.location.file.name
        else:
            if not cursor.kind is CursorKind.TRANSLATION_UNIT:
                raise ValueError('`cursor` parameter')
            self.file = cursor.spelling
        self.cursor = cursor
        self.annotations = [c.spelling for c in cursor.get_children() if c.kind is CursorKind.ANNOTATE_ATTR]

    @property
    def hidden(self):
        return 'hidden' in self.annotations

    def _repr_header_(self):
        return "/* non-readable header lines */"

    def __str__(sef):
        return "non-readable"

class TypeRefHeaderInterface(HeaderInterface):

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        self.spelling = cursor.spelling
        self.type = TypeFactory(curser.get_declaration())

    def _repr_header_(self):
        return self.spelling

    def __str__(self):
        return self.spelling

class TemplateTypeHeaderInterface(HeaderInterface):

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        self.spelling = cursor.type.spelling

    def _repr_header_(self):
        return self.spelling

    def __str__(self):
        return self.spelling

def templates(*interfaces):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, TemplateTypeHeaderInterface)]

class AliasHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        """
        """
        HeaderInterface.__init__(self, cursor)
        self.spelling = cursor.spelling
        self.type = TypeFactory(cursor.underlying_typedef_type)

    def __str__(self):
        return self.spelling

def aliases(*interfaces, **kwargs):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, AliasHeaderInterface)]

class UsingHeaderInterface(AliasHeaderInterface):
    """
    """

    def _repr_header_(self):
        return 'using '+self.spelling+' = '+self.type._repr_header_()+';'

class TypedefHeaderInterface(AliasHeaderInterface):
    """
    """

    def _repr_header_(self):
        return 'typedef '+self.type._repr_header_()+' '+self.spelling+';'

class EnumHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind is CursorKind.ENUM_DECL:
            raise TypeError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.values = sorted([c.spelling for c in cursor.get_children() if c.kind is CursorKind.ENUM_CONSTANT_DECL])

    def _repr_header_(self):
        return 'enum '+self.spelling+'\n{\n\t'+',\n\t'.join(self.values)+'\n};'

    def __str__(self):
        return self.spelling

    @property
    def anonymous(self):
        return str(self) == ""

def enums(*interfaces, **kwargs):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, EnumHeaderInterface)]

class VariableHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL, CursorKind.FIELD_DECL]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.type = TypeFactory(cursor.type)
        #self.static = cursor.is_static_variable()

    def _repr_header_(self):
        return self.type._repr_header_()+" "+self.spelling+';'

    def __str__(self):
        return str(self.type) + " " + self.spelling

def variables(*interfaces, **kwargs):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, VariableHeaderInterface)]

class FieldHeaderInterface(VariableHeaderInterface):
    """
    """

    def __init__(self, cursor, **kwcursor):
        VariableHeaderInterface.__init__(self, cursor)
        self.access = cursor.access_specifier
        #self.mutable = cursor.type.is_mutable_qualified()

    def _repr_header_(self):
        header = super(FieldHeaderInterface, self)._repr_header_()
        #if self.mutable: header = "mutable "+header
        return header

class FunctionHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.output = TypeFactory(cursor.result_type)
        self.inputs = [VariableHeaderInterface(c) for c in cursor.get_children() if c.kind is CursorKind.PARM_DECL]

    def _repr_header_(self):
        return self.output._repr_header_()+' '+self.spelling+'('+", ".join([i._repr_header_()[:-1] for i in self.inputs])+');'

    def __str__(self):
        return self.spelling

def functions(*interfaces):
    """
    """
    results = dict()
    for interface in interfaces:
        if isinstance(interface, FunctionHeaderInterface):
            if not interface.spelling in results:
                results[interface.spelling] = [interface]
            else:
                results[interface.spelling].append(interface)
    return results.values()

class MethodHeaderInterface(FunctionHeaderInterface):
    """
    """

    def __init__(self, cursor, **kwcursor):
        FunctionHeaderInterface.__init__(self, cursor)
        self.static = cursor.is_static_method()
        self.virtual = cursor.is_virtual_method()
        self.pure_virtual = cursor.is_pure_virtual_method()
        self.const = cursor.type.is_const_qualified()

    def _repr_header_(self):
        header = FunctionHeaderInterface._repr_header_(self)[:-1]
        if self.static: header = "static " + header
        if self.virtual: header = "virtual " + header
        if self.const: header = header + " const"
        if self.pure_virtual: header = header + " = 0"
        return header+";"

class ConstructorHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind is CursorKind.CONSTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.inputs = [VariableHeaderInterface(c) for c in cursor.get_children() if c.kind is CursorKind.PARM_DECL]

    def _repr_header_(self):
        return self.spelling+'('+", ".join([i._repr_header_()[:-1] for i in self.inputs])+');'

    def __str__(self):
        return self.spelling

def constructors(*interfaces):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, ConstructorHeaderInterface)]

class DestructorHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind is CursorKind.DESTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.virtual = cursor.is_virtual_method()

    def _repr_header_(self):
        if self.virtual: header = "virtual "
        else: header = ""
        return header + self.spelling + "();"

    def __str__(self):
        return self.spelling

class BaseClassHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind is CursorKind.CXX_BASE_SPECIFIER:
            raise ValueError('`cursor` parameter')
        self.spelling = [c for c in cursor.get_children() if c.kind in [CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF]].pop().type.spelling
        if cursor.access_specifier is AccessSpecifier.PUBLIC:
            self.access = 'public'
        elif cursor.access_specifier is AccessSpecifier.PROTECTED:
            self.access = 'protected'
        elif cursor.access_specifier is AccessSpecifier.PRIVATE:
            self.access = 'private'
        else:
            raise ValueError('`cursor` parameter')

    def __str__(self):
        return self.spelling

class AccessorHeaderInterface(HeaderInterface):

    def __init__(self, cursor):
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind is CursorKind.CXX_ACCESS_SPEC_DECL:
            raise ValueError('`cursor` parameter')
        if cursor.access_specifier is AccessSpecifier.PUBLIC:
            self.spelling = 'public'
        elif cursor.access_specifier is AccessSpecifier.PROTECTED:
            self.spelling = 'protected'
        elif cursor.access_specifier is AccessSpecifier.PRIVATE:
            self.spelling = 'private'
        else:
            raise ValueError('`cursor` parameter')

    def _repr_header_(self):
        return self.spelling+":"

    def __str__(self):
        return self.spelling

def accessors(*interfaces):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, AccessorHeaderInterface)]

class UserDefinedTypeHeaderInterface(HeaderInterface):

    def __init__(self, cursor):
        self._declarations = []
        self._bases = []
        if cursor is None:
            raise TypeError('`cursor` parameter')
        HeaderInterface.__init__(self, cursor)
        if not cursor.kind in [CursorKind.CLASS_DECL, CursorKind.CLASS_TEMPLATE, CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION, CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        for c in cursor.get_children():
            if c.kind is CursorKind.CONSTRUCTOR:
                self._declarations.append(ConstructorHeaderInterface(c))
            elif c.kind is CursorKind.DESTRUCTOR:
                self._declarations.append(DestructorHeaderInterface(c))
            elif c.kind is CursorKind.CXX_BASE_SPECIFIER:
                self._bases.append(BaseClassHeaderInterface(c))
            elif c.kind is CursorKind.CXX_METHOD:
                self._declarations.append(MethodHeaderInterface(c))
            elif c.kind is CursorKind.FIELD_DECL:
                self._declarations.append(FieldHeaderInterface(c))
            elif c.kind is CursorKind.TYPEDEF_DECL:
                self._declarations.append(TypedefHeaderInterface(c))
            elif c.kind is CursorKind.TYPE_ALIAS_DECL:
                self._declarations.append(UsingHeaderInterface(c))
            elif c.kind is CursorKind.CLASS_DECL:
                self._declarations.append(ClassHeaderInterface(c))
            elif c.kind is CursorKind.STRUCT_DECL:
                self._declarations.append(StructHeaderInterface(c))
            elif c.kind is CursorKind.UNION_DECL:
                self._declarations.append(UnionHeaderInterface(c))
            elif c.kind is CursorKind.TEMPLATE_TYPE_PARAMETER:
                self._declarations.append(TemplateTypeHeaderInterface(c))
            elif c.kind is CursorKind.CXX_ACCESS_SPEC_DECL:
                self._declarations.append(AccessorHeaderInterface(c))
            elif c.kind in [CursorKind.ANNOTATE_ATTR, CursorKind.UNEXPOSED_EXPR, CursorKind.UNEXPOSED_DECL]:
                continue
            else:
                raise ValueError('`cursor` parameter')

    def __str__(self):
        string = ", ".join(str(template) for template in templates(self[:]))
        if len(string) > 0:
            string = "< "+string+" >"
        return self.spelling+string

    def __len__(self):
        return len(self._declarations)

    def __getitem__(self, index):
        return self._declarations[index]

    @property
    def pure_virtual(self):
        if any(any(overload.pure_virtual for overload in function) for function in functions(*self[:])):
            return True
        else:
            return False

    @property
    def has_templates(self):
        return len(templates(*self[:])) > 0

    @property
    def empty(self):
        return len(self) == 0 or len(self) == len(templates(*self[:]))

    def bases(self, access='public'):
        if not isinstance(access, basestring):
            raise TypeError('`access` parameter')
        if not access in ['public', 'protected', 'private']:
            raise ValueError('`access` parameter')
        return [base for base in self._bases if base.access == access]

    def access(self, access='default'):
        if not isinstance(access, basestring):
            raise TypeError('`access` parameter')
        if not access in ['public', 'protected', 'private', 'default']:
            raise ValueError('`access` parameter')
        if access == 'default':
            acess = self.default_access
        values = cumsum([isinstance(interface, AccessorHeaderInterface) for interface in self])
        labels = [self.default_access]+[accessor.spelling for accessor in accessors(*self[:])]
        return [interface for index, interface in enumerate(self) if labels[values[index]] == access and not isinstance(interface, AccessorHeaderInterface)]

    def _repr_header_(self):
        if self.empty:
            header = ";"
        else:
            public_header = ""
            protected_header = ""
            private_header = ""
            for i in [self.typedefs, self.fields, self.user_defined_types, list(itertools.chain(self.constructors, [self.destructor])), self.methods]:
                public_lines = 0
                protected_lines = 0
                private_lines = 0
                for j in i:
                    if not j is None:
                        if j.access is AccessSpecifier.PUBLIC:
                            public_header += j._repr_header_()+"\n"
                            public_lines += 1
                        elif j.access is AccessSpecifier.PROTECTED:
                            protected_header += j._repr_header_()+"\n"
                            protected_lines += 1
                        elif j.access is AccessSpecifier.PRIVATE:
                            private_header += j._repr_header_()+"\n"
                            private_lines += 1
                if public_lines > 0: public_header += "\n"
                if protected_lines > 0: protected_header += "\n"
                if private_lines > 0: private_header += "\n"
            header = ""
            for i, j in zip(["public", "protected", "private"], [public_header, protected_header, private_header]):
                if len(j) > 0:
                    header += "\t"+i+":\n"+"\t"*2+("\n"+"\t"*2).join(j.splitlines())+"\n"
            header = "\n{\n"+header+"};"
            if len(self.bases) > 0:
                public_bases = []
                protected_bases = []
                private_bases = []
                for i in self.bases:
                    if i.access is AccessSpecifier.PUBLIC:
                        public_bases.append(i.__str__())
                    elif i.access is AccessSpecifier.PROTECTED:
                        protected_bases.append(i.__str__())
                    elif i.access is AccessSpecifier.PRIVATE:
                        private_bases.append(i.__str__())
                header = " : " +", ".join([", ".join(i) for i in [public_bases, protected_bases, private_bases] if len(i) > 0])+header
        header = self.spelling+header
        return header

def classes(*interfaces):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, UserDefinedTypeHeaderInterface) and not isinstance(interface, UnionHeaderInterface)]

class StructHeaderInterface(UserDefinedTypeHeaderInterface):
    """
    """
    default_access = 'public'

    def _repr_header_(self):
        return "struct "+UserDefinedTypeHeaderInterface._repr_header_(self)

class ClassHeaderInterface(UserDefinedTypeHeaderInterface):
    """
    """
    default_access = 'private'

    def _repr_header_(self):
        return "class "+UserDefinedTypeHeaderInterface._repr_header_(self)


class UnionHeaderInterface(UserDefinedTypeHeaderInterface):
    """
    """
    default_access = 'public'

    def __init__(self, cursor):
        UserDefinedTypeHeaderInterface.__init__(self, cursor)
        if any([m.virtual for m in self.methods]) or len(self.bases) > 0:
            raise ValueError('`cursor` parameter')

    def _repr_header_(self):
        return "union "+UserDefinedTypeHeaderInterface._repr_header_(self)

    @property
    def anonymous(self):
        return str(self) == ""

def unions(*interfaces):
    """
    """
    return [interface for interface in interfaces if isinstance(interface, UnionHeaderInterface)]

class ScopeHeaderInterface(HeaderInterface):
    """
    """

    def __init__(self, cursor, filtering=None):
        HeaderInterface.__init__(self, cursor)
        self._declarations = []
        if filtering is None:
            def filtering(children):
                return children
        for ch in filtering(cursor.get_children()):
            if ch.kind is CursorKind.VAR_DECL:
                self._declarations.append(VariableHeaderInterface(ch))
            elif ch.kind is CursorKind.FUNCTION_DECL:
                self._declarations.append(FunctionHeaderInterface(ch))
            elif ch.kind is CursorKind.STRUCT_DECL:
                self._declarations.append(StructHeaderInterface(ch))
            elif ch.kind in [CursorKind.CLASS_DECL, CursorKind.CLASS_TEMPLATE]:
                self._declarations.append(ClassHeaderInterface(ch))
            elif ch.kind is CursorKind.ENUM_DECL:
                self._declarations.append(EnumHeaderInterface(ch))
            elif ch.kind is CursorKind.NAMESPACE:
                self._declarations.append(NamespaceHeaderInterface(ch))
            elif ch.kind is CursorKind.TYPEDEF_DECL:
                self._declarations.append(TypedefHeaderInterface(ch))
            elif ch.kind is CursorKind.TYPE_ALIAS_DECL:
                self._declarations.append(UsingHeaderInterface(ch))
            elif ch.kind is CursorKind.ANNOTATE_ATTR:
                continue
            else:
                self._declarations.append(HeaderInterface(ch))

    def __str__(self):
        return self.spelling

    def __len__(self):
        return len(self._declarations)

    def __getitem__(self, index):
        return self._declarations[index]

def namespaces(*interfaces):
    """
    """
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeHeaderInterface):
            if interface.spelling in results:
                results[interface.spelling].append(interface)
            else:
                results[interface.spelling] = [interface]
    return results.values()

class NamespaceHeaderInterface(ScopeHeaderInterface):
    """
    """

    def __init__(self, cursor, filtering=None):
        ScopeHeaderInterface.__init__(self, cursor, filtering)
        if not cursor.kind is CursorKind.NAMESPACE:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling

    def _repr_header_(self):
        return "namespace "+self.spelling+"\n{\n"+"\n\n".join(["\t"+"\n\t".join(d._repr_header_().splitlines()) for d in self._declarations])+"\n}"

class GlobalscopeHeaderInterface(ScopeHeaderInterface):
    """
    """

    def __init__(self, cursor, filtering=None):
        if filtering is None:
            def filtering(children):
                return [ch for ch in children if ch.location.file.name == self.file]
        ScopeHeaderInterface.__init__(self, cursor, filtering)
        if not cursor.kind is CursorKind.TRANSLATION_UNIT:
            raise ValueError('`cursor` parameter')
        self.spelling = ""

    def _repr_header_(self):
        return "\n\n".join([d._repr_header_() for d in self._declarations])

def header_interface(filepath, flags=None):
    """
    """
    return GlobalscopeHeaderInterface(parse_file(filepath, flags).cursor)

def resolve_scopes(*interfaces, **kwargs):
    """
    """
    scope = dict.pop(kwargs, 'scope', "")
    if not scope == "::":
        scope += "::"
    results = {scope : []}
    level = dict.pop(kwargs, 'level', 1)
    if not isinstance(level, int):
        raise TypeError('`level` parameter')
    if not 0 <= level <= 2:
        raise ValueError('`level` parameter')
    for interface in interfaces:
        if level > 0 and isinstance(interface, ScopeHeaderInterface):
            if level == 1:
                for key, value in resolve_scopes(*interface[:], scope=scope+str(interface)).iteritems():
                    if key in results:
                        results[key].extend(value)
                    else:
                        results[key] = value
            else:
                results[scope].append(interface)
        elif level > 1 and isinstance(interface, UserDefinedTypeHeaderInterface):
            if level == 2:
                for key, value in resolve_scopes(*interface[:], scope=scope+str(interface)).iteritems():
                    if key in results:
                        results[key].extend(value)
                    else:
                        results[key] = value
            else:
                results[scope].append(interface)
        else:
            results[scope].append(interface)
    return results

def hide(*interfaces):
    """
    """
    for interface in interfaces:
        interface.annotations.append('hidden')
