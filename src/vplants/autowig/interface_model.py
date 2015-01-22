"""
"""
from parse import parse
from clang.cindex import CursorKind, AccessSpecifier
import itertools

class TypeModel(object):

    def __init__(self, cursor):
        self.name = cursor.spelling

    def __repr__(self):
        return self.name

class TypedefModel(TypeModel):
    """
    """
    def __init__(self, cursor):
        self.name = cursor.spelling
        self.alias = [c for c in cursor.get_children() if c.kind is CursorKind.TYPE_REF][0].type.spelling

    def _repr_interface_(self):
        return 'typedef '+self.alias+' '+self.name+';'

class VariableModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind in [CursorKind.VAR_DECL, CursorKind.PARM_DECL, CursorKind.FIELD_DECL]:
            raise TypeError('`cursor` parameter')
        self.name = cursor.spelling
        self.type = TypeModel(cursor.type)
        self.const = cursor.type.is_const_qualified()
        #self.static = cursor.is_static_variable()


    def _repr_interface_(self):
        header = repr(self.type)+" "+self.name+";"
        if self.const: header = "const "+header
        return header

class FunctionModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD]:
            raise TypeError('`cursor` parameter')
        self.name = cursor.spelling
        self.output = TypeModel(cursor.result_type)
        self.inputs = [VariableModel(c) for c in cursor.get_children()]

    def _repr_interface_(self):
        return str(self.output)+' '+self.name+'('+", ".join([i._repr_interface_()[:-1] for i in self.inputs])+');'

class EnumModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind is CursorKind.ENUM_DECL:
            raise TypeError('`cursor` parameter')
        self.name = cursor.spelling
        self.values = sorted([c.spelling for c in cursor.get_children()])

    def _repr_interface_(self):
        return 'enum '+self.name+'\n{\n\t'+',\n\t'.join(self.values)+'\n};'

class ConstructorModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind is CursorKind.CONSTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.name = cursor.spelling
        self.access = cursor.access_specifier
        self.inputs = [VariableModel(c) for c in cursor.get_children()]

    def _repr_interface_(self):
        return self.name+'('+", ".join([i._repr_interface_()[:-1] for i in self.inputs])+');'

class DestructorModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind is CursorKind.DESTRUCTOR:
            raise ValueError('`cursor` parameter')
        self.name = cursor.spelling
        self.access = cursor.access_specifier
        self.virtual = cursor.is_virtual_method()

    def _repr_interface_(self):
        if self.virtual: header = "virtual "
        else: header = ""
        return header + self.name + "();"

class FieldModel(VariableModel):
    """
    """

    def __init__(self, cursor):
        super(FieldModel, self).__init__(cursor)
        self.access = cursor.access_specifier
        #self.mutable = cursor.type.is_mutable_qualified()


    def _repr_interface_(self):
        header = super(FieldModel, self)._repr_interface_()
        #if self.mutable: header = "mutable "+header
        return header

class MethodModel(FunctionModel):
    """
    """

    def __init__(self, cursor):
        super(MethodModel, self).__init__(cursor)
        self.access = cursor.access_specifier
        self.static = cursor.is_static_method()
        self.virtual = cursor.is_virtual_method()
        self.pure_virtual = cursor.is_pure_virtual_method()
        self.const = cursor.type.is_const_qualified()

    def _repr_interface_(self):
        header = super(MethodModel, self)._repr_interface_()[:-1]
        if self.static: header = "static " + header
        if self.virtual: header = "virtual " + header
        if self.const: header = header + " const"
        if self.pure_virtual: header = header + " = 0"
        return header+";"

class BaseClassModel(object):
    """
    """

    def __init__(self, cursor):
        #super(BaseClassModel, self).__init__(cursor)
        if not cursor.kind is CursorKind.CXX_BASE_SPECIFIER:
            raise ValueError('`cursor` parameter')
        self.access = cursor.access_specifier
        self.name = [c for c in cursor.get_children() if c.kind is CursorKind.TYPE_REF][0].type.spelling

    def __str__(self):
        if self.access is AccessSpecifier.PUBLIC:
            string = "public"
        elif self.access is AccessSpecifier.PROTECTED:
            string = "protected"
        elif self.access is AccessSpecifier.PRIVATE:
            string = "private"
        return string + " " + str(self.name)

class ClassModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind in [CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL]:
            raise TypeError('`cursor` parameter')
        self.name = cursor.spelling
        self.bases = []
        self.typedefs = []
        self.constructors = []
        self.destructor = None
        self.methods = []
        self.fields = []
        for c in cursor.get_children():
            if c.kind is CursorKind.CONSTRUCTOR:
                self.constructors.append(ConstructorModel(c))
            elif c.kind is CursorKind.DESTRUCTOR:
                self.destructor = DestructorModel(c)
            elif c.kind is CursorKind.CXX_BASE_SPECIFIER:
                self.bases.append(BaseClassModel(c))
            elif c.kind is CursorKind.CXX_METHOD:
                self.methods.append(MethodModel(c))
            elif c.kind is CursorKind.FIELD_DECL:
                self.fields.append(FieldModel(c))
            elif c.kind is CursorKind.TYPEDEF_DECL:
                self.typedefs.append(TypedefModel(c))
            elif c.kind is CursorKind.CXX_ACCESS_SPEC_DECL:
                continue
            else:
                raise ValueError('`cursor` parameter')

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
        header = "class "+self.name+header
        return header

class NamespaceModel(object):
    """
    """

    def __init__(self, cursor):
        if not cursor.kind is CursorKind.NAMESPACE:
            raise TypeError('`cursor` parameter')
        self.name = cursor.spelling
        self.declarations = []
        for c in cursor.get_children():
            if c.kind is CursorKind.VAR_DECL:
                self.declarations.append(VariableModel(c))
            elif c.kind is CursorKind.FUNCTION_DECL:
                self.declarations.append(FunctionModel(c))
            elif c.kind in [CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL]:
                self.declarations.append(ClassModel(c))
            elif c.kind is CursorKind.ENUM_DECL:
                self.declarations.append(EnumModel(c))
            elif c.kind is CursorKind.NAMESPACE:
                self.declarations.append(NamespaceModel(c))
            elif c.kind is CursorKind.TYPEDEF_DECL:
                self.declarations.append(TypedefModel(c))
            else:
                raise ValueError('`cursor` parameter')

    def _repr_interface_(self):
        return "namespace "+self.name+"\n{\n"+"\n\n".join(["\t"+"\n\t".join(d._repr_interface_().splitlines()) for d in self.declarations])+"\n}"

def model(filepath, **kwargs):
    """
    """
    translation_unit = parse(filepath, **dict.pop(kwargs, 'parse', {}))
    for c in translation.cursor.get_children():
        if c.location.file.name == filepath:
            if c.kind is CursorKind.VAR_DECL:
                yield VariableModel(c))
            elif c.kind is CursorKind.FUNCTION_DECL:
                yield FunctionModel(c)
            elif c.kind in [CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL]:
                yield ClassModel(c)
            elif c.kind is CursorKind.ENUM_DECL:
                yield EnumModel(c)
            elif c.kind is CursorKind.NAMESPACE:
                yield NamespaceModel(c)
            elif c.kind is CursorKind.TYPEDEF_DECL:
                yield TypedefModel(c)
            else:
                raise ValueError('`cursor` parameter')
