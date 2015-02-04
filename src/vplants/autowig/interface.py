"""
"""
from clang.cindex import TranslationUnit, Type, Cursor, CursorKind, Type, TypeKind, AccessSpecifier
import itertools
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.display import HTML
import re

def Interface(obj):
    """
    """
    return HTML(highlight(obj._repr_interface_(), CppLexer(), HtmlFormatter(full = True)))

class InterfaceType(object):

    def __init__(self, itype):
        if not isinstance(itype, Type):
            raise TypeError('`itype` parameter')
        if itype.kind in [TypeKind.TYPEDEF, TypeKind.LVALUEREFERENCE]:
            raise ValueError('`rtype` parameter')
        self.type = itype
        self.const = itype.is_const_qualified()
        self.spelling = itype.spelling

    def _repr_interface_(self):
        return self.spelling

class InterfaceTypedefType(object):

    def __init__(self, ttype):
        if not isinstance(ttype, Type):
            raise TypeError('`ttype` parameter')
        if not ttype.kind is TypeKind.TYPEDEF:
            raise ValueError('`rtype` parameter')
        self.type = TypeFactory(ttype.get_declaration()).type
        self.spelling = ttype.spelling

    def _repr_interface_(self):
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

    def _repr_interface_(self):
        string = self.type._repr_interface_()
        if self.const:
            string += " const"
        return string + " &"

class InterfacePointerType(object):

    def __init__(self, ptype):
        if not isinstance(ptype, Type):
            raise TypeError('`ptype` parameter')
        if not ptype.kind is TypeKind.POINTER:
            raise ValueError('`ptype` parameter')
        self.spelling = ptype.spelling
        self.type = TypeFactory(ptype.get_pointee())
        self.const = ptype.is_const_qualified()

    def _repr_interface_(self):
        string = self.type._repr_interface_()+" *"
        if self.const:
            string += " const"
        return string

def TypeFactory(type):
    if not isinstance(type, (Cursor, Type)):
        raise TypeError('`type` parameter')
    if isinstance(type, Cursor):
        if type.kind is CursorKind.TYPE_REF:
            return TypeRefInterfaceCursor(type)
        elif type.kind is CursorKind.TYPEDEF_DECL:
            return TypedefInterfaceCursor(type)
        elif type.kind is CursorKind.TYPE_ALIAS_DECL:
            return UsingInterfaceCursor(type)
        elif type.kind is CursorKind.CLASS_DECL:
            return ClassInterfaceCursor(type)
        elif type.kind is CursorKind.STRUCT_DECL:
            return StructInterfaceCursor(type)
        elif type.kind is CursorKind.UNION_DECL:
            return UnionInterfaceCursor(type)
        elif type.kind is CursorKind.TEMPLATE_TYPE_PARAMETER:
            return TemplateTypeInterfaceCursor(type)
    elif isinstance(type, Type):
        if type.kind is TypeKind.LVALUEREFERENCE:
            return InterfaceLValueReferenceType(type)
        elif type.kind is TypeKind.POINTER:
            return InterfacePointerType(type)
        elif type.kind is TypeKind.TYPEDEF:
            return InterfaceTypedefType(type)
        else:
            return InterfaceType(type)

class InterfaceCursor(object):

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

    def _repr_interface_(self):
        return "/* interface */"

class TypeRefInterfaceCursor(InterfaceCursor):

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        self.spelling = cursor.spelling
        self.type = TypeFactory(curser.get_declaration())

    def _repr_interface_(self):
        return self.spelling

class TemplateTypeInterfaceCursor(InterfaceCursor):

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        self.spelling = cursor.type.spelling

    def _repr_interface_(self):
        return self.spelling

class AliasInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        """
        """
        InterfaceCursor.__init__(self, cursor)
        self.spelling = cursor.spelling
        self.type = TypeFactory(cursor.underlying_typedef_type)

class UsingInterfaceCursor(AliasInterfaceCursor):
    """
    """

    def _repr_interface_(self):
        return 'using '+self.spelling+' = '+self.type._repr_interface_()+';'

class TypedefInterfaceCursor(AliasInterfaceCursor):
    """
    """

    def _repr_interface_(self):
        return 'typedef '+self.type._repr_interface_()+' '+self.spelling+';'

class EnumInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind is CursorKind.ENUM_DECL:
            raise TypeError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.values = sorted([c.spelling for c in cursor.get_children() if c.kind is CursorKind.ENUM_CONSTANT_DECL])

    def _repr_interface_(self):
        return 'enum '+self.spelling+'\n{\n\t'+',\n\t'.join(self.values)+'\n};'

class VariableInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL, CursorKind.FIELD_DECL]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.type = TypeFactory(cursor.type)
        #self.static = cursor.is_static_variable()

    def _repr_interface_(self):
        return self.type._repr_interface_()+" "+self.spelling+';'

class FieldInterfaceCursor(VariableInterfaceCursor):
    """
    """

    def __init__(self, cursor, **kwcursor):
        VariableInterfaceCursor.__init__(self, cursor)
        self.access = cursor.access_specifier
        #self.mutable = cursor.type.is_mutable_qualified()

    def _repr_interface_(self):
        header = super(FieldInterfaceCursor, self)._repr_interface_()
        #if self.mutable: header = "mutable "+header
        return header

class ConstructorInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind is CursorKind.CONSTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.access = cursor.access_specifier
        self.inputs = [VariableInterfaceCursor(c) for c in cursor.get_children() if c.kind is CursorKind.PARM_DECL]

    def _repr_interface_(self):
        return self.spelling+'('+", ".join([i._repr_interface_()[:-1] for i in self.inputs])+');'

class DestructorInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind is CursorKind.DESTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.access = cursor.access_specifier
        self.virtual = cursor.is_virtual_method()

    def _repr_interface_(self):
        if self.virtual: header = "virtual "
        else: header = ""
        return header + self.spelling + "();"

class FunctionInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.output = TypeFactory(cursor.result_type)
        self.inputs = [VariableInterfaceCursor(c) for c in cursor.get_children() if c.kind is CursorKind.PARM_DECL]

    def _repr_interface_(self):
        return self.output._repr_interface_()+' '+self.spelling+'('+", ".join([i._repr_interface_()[:-1] for i in self.inputs])+');'

class MethodInterfaceCursor(FunctionInterfaceCursor):
    """
    """

    def __init__(self, cursor, **kwcursor):
        FunctionInterfaceCursor.__init__(self, cursor)
        self.access = cursor.access_specifier
        self.static = cursor.is_static_method()
        self.virtual = cursor.is_virtual_method()
        self.pure_virtual = cursor.is_pure_virtual_method()
        self.const = cursor.type.is_const_qualified()

    def _repr_interface_(self):
        header = FunctionInterfaceCursor._repr_interface_(self)[:-1]
        if self.static: header = "static " + header
        if self.virtual: header = "virtual " + header
        if self.const: header = header + " const"
        if self.pure_virtual: header = header + " = 0"
        return header+";"

class BaseClassInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor):
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind is CursorKind.CXX_BASE_SPECIFIER:
            raise ValueError('`cursor` parameter')
        self.access = cursor.access_specifier
        self.spelling = [c for c in cursor.get_children() if c.kind in [CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF]].pop().type.spelling

    def __str__(self):
        if self.access is AccessSpecifier.PUBLIC:
            string = "public"
        elif self.access is AccessSpecifier.PROTECTED:
            string = "protected"
        elif self.access is AccessSpecifier.PRIVATE:
            string = "private"
        return string + " " + str(self.spelling)

class UserDefinedTypeInterfaceCursor(InterfaceCursor):

    def __init__(self, cursor):
        self.bases = []
        self.typedefs = []
        self.constructors = []
        self.destructor = None
        self.methods = []
        self.fields = []
        self.user_defined_types = []
        if cursor is None:
            raise TypeError('`cursor` parameter')
        InterfaceCursor.__init__(self, cursor)
        if not cursor.kind in [CursorKind.CLASS_DECL, CursorKind.CLASS_TEMPLATE, CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION, CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        for c in cursor.get_children():
            if c.kind is CursorKind.CONSTRUCTOR:
                self.constructors.append(ConstructorInterfaceCursor(c))
            elif c.kind is CursorKind.DESTRUCTOR:
                self.destructor = DestructorInterfaceCursor(c)
            elif c.kind is CursorKind.CXX_BASE_SPECIFIER:
                self.bases.append(BaseClassInterfaceCursor(c))
            elif c.kind is CursorKind.CXX_METHOD:
                self.methods.append(MethodInterfaceCursor(c))
            elif c.kind is CursorKind.FIELD_DECL:
                self.fields.append(FieldInterfaceCursor(c))
            elif c.kind is CursorKind.TYPEDEF_DECL:
                self.typedefs.append(TypedefInterfaceCursor(c))
                self.typedefs[-1].access = c.access_specifier
            elif c.kind is CursorKind.TYPE_ALIAS_DECL:
                self.typedefs.append(UsingInterfaceCursor(c))
                self.typdefs[-1].access = c.acces_specifier
            elif c.kind is CursorKind.CLASS_DECL:
                self.user_defined_types.append(ClassInterfaceCursor(c))
                self.user_defined_types[-1].access = c.access_specifier
            elif c.kind is CursorKind.STRUCT_DECL:
                self.user_defined_types.append(StructInterfaceCursor(c))
                self.user_defined_types[-1].access = c.access_specifier
            elif c.kind is CursorKind.UNION_DECL:
                self.user_defined_types.append(UnionInterfaceCursor(c))
                self.user_defined_types[-1].access = c.access_specifier
            elif c.kind is CursorKind.TEMPLATE_TYPE_PARAMETER:
                self.templates.append(TemplateTypeInterfaceCursor(c))
            elif c.kind in [CursorKind.ANNOTATE_ATTR, CursorKind.CXX_ACCESS_SPEC_DECL, CursorKind.UNEXPOSED_EXPR, CursorKind.UNEXPOSED_DECL]:
                continue
            else:
                def node_children(node):
                    """
                    """
                    return (c for c in node.get_children() if c.location.file.name == self.spelling)

                def print_node(node):
                    """
                    """
                    text = node.spelling or node.displayname
                    kind = str(node.kind)[str(node.kind).index('.')+1:]
                    return '{} {}'.format(kind, text)

                import asciitree
                print asciitree.draw_tree(c, node_children, print_node)
                raise ValueError('`cursor` parameter')

    @property
    def pure_virtual(self):
        if any([m.pure_virtual for m in self.methods]):
            return True
        else:
            return False

    @property
    def empty(self):
        return len(self.bases) == 0 and len(self.typedefs) == 0 and len(self.constructors) == 0 and self.destructor is None and len(self.methods) == 0 and len(self.fields) == 0

    def _repr_interface_(self):
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
                            public_header += j._repr_interface_()+"\n"
                            public_lines += 1
                        elif j.access is AccessSpecifier.PROTECTED:
                            protected_header += j._repr_interface_()+"\n"
                            protected_lines += 1
                        elif j.access is AccessSpecifier.PRIVATE:
                            private_header += j._repr_interface_()+"\n"
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

class StructInterfaceCursor(UserDefinedTypeInterfaceCursor):
    """
    """

    def _repr_interface_(self):
        return "struct "+UserDefinedTypeInterfaceCursor._repr_interface_(self)

class ClassInterfaceCursor(UserDefinedTypeInterfaceCursor):
    """
    """

    def _repr_interface_(self):
        return "class "+UserDefinedTypeInterfaceCursor._repr_interface_(self)

class UnionInterfaceCursor(UserDefinedTypeInterfaceCursor):
    """
    """

    def __init__(self, cursor):
        UserDefinedTypeInterfaceCursor.__init__(self, cursor)
        if any([m.virtual for m in self.methods]) or len(self.bases) > 0:
            raise ValueError('`cursor` parameter')

    def _repr_interface_(self):
        return "union "+UserDefinedTypeInterfaceCursor._repr_interface_(self)

class TemplateClassInterfaceCursor(UserDefinedTypeInterfaceCursor):
    """
    """

    def __init__(self, cursor):
        self.templates = []
        UserDefinedTypeInterfaceCursor.__init__(self, cursor)

    def _repr_interface_(self):
        return "template < " + ", ".join(["typename "+i.spelling for i in self.templates])+ " > class "+UserDefinedTypeInterfaceCursor._repr_interface_(self)

class ScopeInterfaceCursor(InterfaceCursor):
    """
    """

    def __init__(self, cursor, filtering=None):
        InterfaceCursor.__init__(self, cursor)
        self.declarations = []
        if filtering is None:
            def filtering(children):
                return children
        for ch in filtering(cursor.get_children()):
            if ch.kind is CursorKind.VAR_DECL:
                self.declarations.append(VariableInterfaceCursor(ch))
            elif ch.kind is CursorKind.FUNCTION_DECL:
                self.declarations.append(FunctionInterfaceCursor(ch))
            elif ch.kind is CursorKind.STRUCT_DECL:
                self.declarations.append(StructInterfaceCursor(ch))
            elif ch.kind is CursorKind.CLASS_DECL:
                self.declarations.append(ClassInterfaceCursor(ch))
            elif ch.kind is CursorKind.CLASS_TEMPLATE:
                self.declarations.append(TemplateClassInterfaceCursor(ch))
            elif ch.kind is CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                self.declarations.append(InterfaceCursor(ch))
                #self.declarations.append(TemplateClassInterfaceCursor(ch))
            elif ch.kind is CursorKind.ENUM_DECL:
                self.declarations.append(EnumInterfaceCursor(ch))
            elif ch.kind is CursorKind.NAMESPACE:
                self.declarations.append(NamespaceInterfaceCursor(ch))
            elif ch.kind is CursorKind.TYPEDEF_DECL:
                self.declarations.append(TypedefInterfaceCursor(ch))
            elif ch.kind is CursorKind.TYPE_ALIAS_DECL:
                self.declarations.append(UsingInterfaceCursor(ch))
            elif ch.kind is CursorKind.ANNOTATE_ATTR:
                continue
            else:
                self.declarations.append(InterfaceCursor(ch))

class NamespaceInterfaceCursor(ScopeInterfaceCursor):
    """
    """

    def __init__(self, cursor, filtering=None):
        ScopeInterfaceCursor.__init__(self, cursor, filtering)
        if not cursor.kind is CursorKind.NAMESPACE:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling

    def _repr_interface_(self):
        return "namespace "+self.spelling+"\n{\n"+"\n\n".join(["\t"+"\n\t".join(d._repr_interface_().splitlines()) for d in self.declarations])+"\n}"

class GlobalscopeInterfaceCursor(ScopeInterfaceCursor):
    """
    """

    def __init__(self, cursor, filtering=None):
        if filtering is None:
            def filtering(children):
                return [ch for ch in children if ch.location.file.name == self.file]
        ScopeInterfaceCursor.__init__(self, cursor, filtering)
        if not cursor.kind is CursorKind.TRANSLATION_UNIT:
            raise ValueError('`cursor` parameter')
        self.spelling = ""

    def _repr_interface_(self):
        return "\n\n".join([d._repr_interface_() for d in self.declarations])

def interface_translation_unit(translation_unit, filtering=None):
    """
    """
    if not isinstance(translation_unit, TranslationUnit):
        raise TypeError('`translation_unit` parameter')
    return GlobalscopeInterfaceCursor(translation_unit.cursor, filtering)
