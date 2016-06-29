from mako.template import Template

from .asg import *

DeclarationProxy.cython_export = True

class CythonDefinitionFileProxy(FileProxy):

    DESUGAREDTYPE = Template(text=r"""${dtype.unqualified_type.globalname.strip('::').replace('::', '.')} ${dtype.qualifiers}""")

    EXTERN = Template(text=r"""cdef extern from "<${obj.header.searchpath}>" namespace "${obj.parent.globalname.lstrip('::')}":""")

    FUNCTION = Template(text=r"""\
% if extern:
${EXTERN.render(obj=fct)}
% endif
    ${DESUGAREDTYPE.render(dtype=fct.return_type.desugared_type)} ${fct.localname}(${", ".join(DESUGAREDTYPE.render(dtype=prm.qualified_type.desugared_type) for prm in fct.parameters)})""")

    VARIABLE = Template(text=r"""\
% if extern:
${EXTERN.render(obj=var)}
% endif
    ${DESUGAREDTYPE.render(dtype=var.qualified_type.desugared_type)} ${var.localname}""")

    CONSTRUCTOR = Template(text=r"""${ctr.localname}(${", ".join(DESUGAREDTYPE.render(dtype=prm.qualified_type.desugared_type) for prm in ctr.parameters)})""")

    CLASS = Template(text=r"""\
% if extern:
${EXTERN.render(obj=cls)}
% endif
    cdef cppclass ${cls.localname}\
% if cls.is_derived:
(${', '.join(base.globalname.lstrip('::').replace('::', '.') for base in cls.bases(access='public'))})\
% endif
:
% for ctr in cls.constructors:
    % if ctr.cython_export:
        ${CONSTRUCTOR.render(ctr=ctr, DESUGAREDTYPE=DESUGAREDTYPE)}
    % endif
% endfor
% for mtd in cls.methods(access='public'):
    % if mtd.cython_export:
        %if mtd.is_static:
        @staticmethod
        %endif
    ${FUNCTION.render(fct=mtd, extern=False, DESUGAREDTYPE=DESUGAREDTYPE) + ' const' * mtd.is_const}
    % endif
% endfor
% for fld in cls.fields(access='public'):
    % if fld.cython_export:
    ${VARIABLE.render(var=fld, extern=False, DESUGAREDTYPE=DESUGAREDTYPE)}
    % endif
% endfor""")

    @property
    def is_empty(self):
        return len(self._declarations) == 0

    @property
    def depth(self):
        if self.is_empty:
            return 0
        else:
            depth = 0
            for declaration in self.declarations:
                if isinstance(declaration, ClassProxy):
                    depth = max(declaration.depth, depth)
                elif isinstance(declaration, VariableProxy):
                    target = declaration.qualified_type.desugared_type.unqualified_type
                    if isinstance(target, ClassTemplateSpecializationProxy) and target.is_smart_pointer:
                        target = target.templates[0].target
                    if isinstance(target, ClassProxy):
                        depth = max(target.depth+1, depth)
            return depth

    @property
    def scope(self):
        if len(self._declarations) > 0:
            return self._asg[self.declarations[0]._node].parent

    @property
    def _content(self):
        content = ""
        #self.HEADER.render(headers = self._asg.includes(*self.declarations), errors = [declaration for declaration in self.declarations if isinstance(declaration, ClassProxy) and declaration.is_error])
        #content += '\n\nvoid ' + self.prefix + '()\n{\n'
        #content += self.SCOPE.render(scopes = self.scopes,
        #        node_rename = node_rename,
        #        documenter = documenter)
        for arg in self.declarations:
            if isinstance(arg, EnumeratorProxy):
                pass
                #content += '\n' + self.ENUMERATOR.render(enumerator = arg,
                #        node_rename = node_rename,
                #        documenter = documenter)
            elif isinstance(arg, EnumerationProxy):
                pass
                #content += '\n' + self.ENUMERATION.render(enumeration = arg,
                #        node_rename = node_rename,
                #        documenter = documenter)
            elif isinstance(arg, VariableProxy):
                content += '\n' + self.VARIABLE.render(var = arg,
                        EXTERN=self.EXTERN,
                        DESUGAREDTYPE=self.DESUGAREDTYPE)
            elif isinstance(arg, FunctionProxy):
                content += '\n' + self.FUNCTION.render(fct = arg,
                        EXTERN=self.EXTERN,
                        DESUGAREDTYPE=self.DESUGAREDTYPE)
            elif isinstance(arg, ClassProxy):
                content += '\n' + self.CLASS.render(cls = arg)
            elif isinstance(arg, TypedefProxy):
                continue
            else:
                raise NotImplementedError(arg.__class__.__name__)
        content += '\n}'
        return content
