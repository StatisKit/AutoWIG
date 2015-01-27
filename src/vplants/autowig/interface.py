"""
"""
from clang.cindex import TranslationUnit, Type, Cursor, CursorKind, AccessSpecifier
import itertools
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.display import HTML

def Interface(obj):
    """
    """
    return HTML(highlight(obj._repr_interface_(), CppLexer(), HtmlFormatter(full = True)))

class InterfaceModel(object):

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

    def _repr_interface_(self):
        return ""

class TypeModel(object):

    def __init__(self, cursor):
        if isinstance(cursor, Cursor):
            self.cursor = cursor
        elif not isinstance(cursor, Type):
            raise TypeError('`cursor` parameter')
        self.spelling = cursor.spelling

    def __repr__(self):
        return self.spelling

class TypedefInterfaceModel(InterfaceModel):
    """
    """
    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        self.spelling = cursor.spelling
        self.declaration = ""
        for c in cursor.get_children():
            if c.kind is CursorKind.NAMESPACE_REF:
                self.declaration += c.spelling+"::"
        self.declaration = list(cursor.get_children()).pop().type.spelling

    def _repr_interface_(self):
        return 'typedef '+self.declaration+' '+self.spelling+';'

class EnumInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind is CursorKind.ENUM_DECL:
            raise TypeError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.values = sorted([c.spelling for c in cursor.get_children()])

    def _repr_interface_(self):
        return 'enum '+self.spelling+'\n{\n\t'+',\n\t'.join(self.values)+'\n};'

class VariableInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL, CursorKind.FIELD_DECL]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.type = TypeModel(cursor.type)
        self.const = cursor.type.is_const_qualified()
        #self.static = cursor.is_static_variable()

    def _repr_interface_(self):
        header = repr(self.type)+" "+self.spelling
        if self.const: header = "const "+header
        return header+";"

class FieldInterfaceModel(VariableInterfaceModel):
    """
    """

    def __init__(self, cursor, **kwcursor):
        VariableInterfaceModel.__init__(self, cursor)
        self.access = cursor.access_specifier
        #self.mutable = cursor.type.is_mutable_qualified()

    def _repr_interface_(self):
        header = super(FieldInterfaceModel, self)._repr_interface_()
        #if self.mutable: header = "mutable "+header
        return header

class ConstructorInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind is CursorKind.CONSTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.access = cursor.access_specifier
        self.inputs = [VariableInterfaceModel(c) for c in cursor.get_children()]

    def _repr_interface_(self):
        return self.spelling+'('+", ".join([i._repr_interface_()[:-1] for i in self.inputs])+');'

class DestructorInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind is CursorKind.DESTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.access = cursor.access_specifier
        self.virtual = cursor.is_virtual_method()

    def _repr_interface_(self):
        if self.virtual: header = "virtual "
        else: header = ""
        return header + self.spelling + "();"

class FunctionInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        self.output = TypeModel(cursor.result_type)
        self.inputs = [VariableInterfaceModel(c) for c in cursor.get_children() if c.kind is CursorKind.PARM_DECL]

    def _repr_interface_(self):
        return str(self.output)+' '+self.spelling+'('+", ".join([i._repr_interface_()[:-1] for i in self.inputs])+');'

class MethodInterfaceModel(FunctionInterfaceModel):
    """
    """

    def __init__(self, cursor, **kwcursor):
        FunctionInterfaceModel.__init__(self, cursor)
        self.access = cursor.access_specifier
        self.static = cursor.is_static_method()
        self.virtual = cursor.is_virtual_method()
        self.pure_virtual = cursor.is_pure_virtual_method()
        self.const = cursor.type.is_const_qualified()

    def _repr_interface_(self):
        header = FunctionInterfaceModel._repr_interface_(self)[:-1]
        if self.static: header = "static " + header
        if self.virtual: header = "virtual " + header
        if self.const: header = header + " const"
        if self.pure_virtual: header = header + " = 0"
        return header+";"

class BaseClassInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor):
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind is CursorKind.CXX_BASE_SPECIFIER:
            raise ValueError('`cursor` parameter')
        self.access = cursor.access_specifier
        self.spelling = [c for c in cursor.get_children() if c.kind is CursorKind.TYPE_REF][0].type.spelling

    def __str__(self):
        if self.access is AccessSpecifier.PUBLIC:
            string = "public"
        elif self.access is AccessSpecifier.PROTECTED:
            string = "protected"
        elif self.access is AccessSpecifier.PRIVATE:
            string = "private"
        return string + " " + str(self.spelling)

class UserDefinedTypeInterfaceModel(InterfaceModel):

    def __init__(self, cursor):
        self.bases = []
        self.typedefs = []
        self.constructors = []
        self.destructor = None
        self.methods = []
        self.fields = []
        self.classes = []
        if cursor is None:
            raise TypeError('`cursor` parameter')
        InterfaceModel.__init__(self, cursor)
        if not cursor.kind in [CursorKind.CLASS_DECL, CursorKind.CLASS_TEMPLATE, CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION, CursorKind.STRUCT_DECL]:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling
        for c in cursor.get_children():
            if c.kind is CursorKind.CONSTRUCTOR:
                self.constructors.append(ConstructorInterfaceModel(c))
            elif c.kind is CursorKind.DESTRUCTOR:
                self.destructor = DestructorInterfaceModel(c)
            elif c.kind is CursorKind.CXX_BASE_SPECIFIER:
                self.bases.append(BaseClassInterfaceModel(c))
            elif c.kind is CursorKind.CXX_METHOD:
                self.methods.append(MethodInterfaceModel(c))
            elif c.kind is CursorKind.FIELD_DECL:
                self.fields.append(FieldInterfaceModel(c))
            elif c.kind is CursorKind.TYPEDEF_DECL:
                self.typedefs.append(TypedefInterfaceModel(c))
            elif c.kind in [CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL]:
                self.classes.append(ClassInterfaceModel(c))
            elif c.kind is CursorKind.TEMPLATE_TYPE_PARAMETER:
                self.templates.append(TypeModel(c))
            elif c.kind is CursorKind.CXX_ACCESS_SPEC_DECL:
                continue
            else:
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
            for i in [self.typedefs, self.fields, list(itertools.chain(self.constructors, [self.destructor])), self.methods]:
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

class StructInterfaceModel(UserDefinedTypeInterfaceModel):
    """
    """

    def _repr_interface_(self):
        return "struct "+UserDefinedTypeInterfaceModel._repr_interface_(self)

class ClassInterfaceModel(UserDefinedTypeInterfaceModel):
    """
    """

    def _repr_interface_(self):
        return "class "+UserDefinedTypeModel._repr_interface_(self)

class TemplateClassInterfaceModel(UserDefinedTypeInterfaceModel):
    """
    """

    def __init__(self, cursor):
        self.templates = []
        UserDefinedTypeInterfaceModel.__init__(self, cursor)

    def _repr_interface_(self):
        return "template < " + ", ".join(["typename "+i.spelling for i in self.templates])+ " > class "+UserDefinedTypeInterfaceModel._repr_interface_(self)

class ScopeInterfaceModel(InterfaceModel):
    """
    """

    def __init__(self, cursor, filtering=None):
        InterfaceModel.__init__(self, cursor)
        self.declarations = []
        if filtering is None:
            def filtering(children):
                return children
        for ch in filtering(cursor.get_children()):
            if ch.kind is CursorKind.VAR_DECL:
                self.declarations.append(VariableInterfaceModel(ch))
            elif ch.kind is CursorKind.FUNCTION_DECL:
                self.declarations.append(FunctionInterfaceModel(ch))
            elif ch.kind is CursorKind.STRUCT_DECL:
                self.declarations.append(StructInterfaceModel(ch))
            elif ch.kind is CursorKind.CLASS_DECL:
                self.declarations.append(ClassInterfaceModel(ch))
            elif ch.kind is CursorKind.CLASS_TEMPLATE:
                self.declarations.append(TemplateClassInterfaceModel(ch))
            elif ch.kind is CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                self.declarations.append(InterfaceModel(ch))
                #self.declarations.append(TemplateClassInterfaceModel(ch))
            elif ch.kind is CursorKind.ENUM_DECL:
                self.declarations.append(EnumInterfaceModel(ch))
            elif ch.kind is CursorKind.NAMESPACE:
                self.declarations.append(NamespaceInterfaceModel(ch))
            elif ch.kind is CursorKind.TYPEDEF_DECL:
                self.declarations.append(TypedefInterfaceModel(ch))
            else:
                self.declarations.append(InterfaceModel(ch))

class NamespaceInterfaceModel(ScopeInterfaceModel):
    """
    """

    def __init__(self, cursor, filtering=None):
        ScopeInterfaceModel.__init__(self, cursor, filtering)
        if not cursor.kind is CursorKind.NAMESPACE:
            raise ValueError('`cursor` parameter')
        self.spelling = cursor.spelling

    def _repr_interface_(self):
        return "namespace "+self.spelling+"\n{\n"+"\n\n".join(["\t"+"\n\t".join(d._repr_interface_().splitlines()) for d in self.declarations])+"\n}"

class GlobalscopeInterfaceModel(ScopeInterfaceModel):
    """
    """

    def __init__(self, cursor, filtering):
        if filtering is None:
            def filtering(children):
                return [ch for ch in children if ch.location.file.name == self.file]
        ScopeInterfaceModel.__init__(self, cursor, filtering)
        if not cursor.kind is CursorKind.TRANSLATION_UNIT:
            raise ValueError('`cursor` parameter')
        self.spelling = ""

    def _repr_interface_(self):
        return "\n\n".join([d._repr_interface_() for d in self.declarations])

def read_interface(translation_unit, filtering=None):
    """
    """
    if not isinstance(translation_unit, TranslationUnit):
        raise TypeError('`translation_unit` parameter')
    return GlobalscopeInterfaceModel(translation_unit.cursor, filtering)
