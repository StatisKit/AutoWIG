from abc import ABCMeta
import os
from mako.template import Template
import re
import itertools

from .asg import AbstractSemanticGraph, DirectoryProxy, CxxFileProxy, CxxNamespaceProxy, CxxEnumProxy, CxxVariableProxy, CxxFunctionProxy, CxxClassProxy, CxxClassTemplateProxy

class BoostPythonExportFileProxy(CxxFileProxy):
    """
    """

    _template = Template(text=r"""\
/***************************************************************************/
/*   This file was automatically generated using VPlants.AutoWIG package   */
/*                                                                         */
/* Any modification of this file will be lost if VPlants.AutoWIG is re-run */
/***************************************************************************/

% if len(obj.classes) > 0:
#include <boost/shared_ptr.hpp>
% endif
#include <boost/python.hpp>
% for include in obj.includes:
#include ${include}
% endfor

/****************************** Thin  wrapper ******************************/

% for function in obj.functions:
    % if function.overloaded:
${function.result_type.globalname} (*${function.hashname})(${", ".join(parameter.type.globalname for parameter in function.parameters)}) = ${function.globalname};
    % endif
% endfor
% for clss in obj.classes:
    % for method in clss.methods():
        % if method.overloaded and method.access == 'public':
${method.result_type.globalname} (*${method.hashname})(${", ".join(parameter.type.globalname for parameter in method.parameters)}) = \
            % if not method.static:
&
            % endif
${method.globalname};
        % endif
    % endfor
% endfor

/****************************** Deep  wrapper ******************************/

void ${obj.localname.replace('.cxx', '')}()
{
% for enum in obj.enums:
    % if enum.anonymous:
        % for value in enum.values:
    boost::python::scope().attr("${value.localname}") = ${value.globalname};
        % endfor
    % else:
    boost::python::enum_< ${enum.globalname} >("${enum.localname}")\
         % for value in enum.values:

        .value("${value.localname}", ${value.globalname})\
        % endfor

        ;
    % endif
% endfor
% for function in obj.functions:
    boost::python::def("${function.localname}", \
    % if function.overloaded:
${function.hashname}\
    % else:
${function.globalname}\
    % endif
);
% endfor
% for clss in obj.classes:
    boost::python::class_< ${clss.globalname}, \
    % if any(base.access == 'public' for base in obj.bases(clss)):
boost::python::bases< ${", ".join(base.globalname for base in obj.bases(clss) if base.access == 'public')} >, \
    % endif
${obj.pointer_type(clss)}\
    % if clss.pure_virtual:
, boost::noncopyable\
    % endif
 >("${clss.localname}", boost::python::no_init)
    % if not clss.pure_virtual:
        % for constructor in clss.constructors:
            % if constructor.access == 'public':
        .def(boost::python::init< ${", ".join(parameter.type.globalname for parameter in constructor.parameters)} >())
            % endif
        % endfor
    % endif
    % for method in clss.methods():
        % if method.access == 'public':
        .def("${obj.methodname(method)}", \
            % if method.overloaded:
${function.hashname}\
            % else:
                % if not method.static:
&\
                % endif
${method.globalname}\
            % endif
)
        % endif
    % endfor
    % for method in obj.supplementary_methods(clss):
        .def("${obj.methodname(method)}", \
            % if not method.static:
&\
            % endif
${method.globalname})
    % endfor
        ;
    % for base in obj.bases(clss):
        % if base.access == 'public':
        boost::python::implicitly_convertible< obj.pointer_type(clss), obj.pointer_type(base) >();
        % endif
    % endfor
% endfor
}""")

    def write(self):
        filehandler = open(self.globalname, 'w')
        try:
            filehandler.write(str(self))
        except:
            filehandler.close()
            raise
        else:
            filehandler.close()

    @staticmethod
    def pointer_type(node):
        return "boost::shared_ptr< " + node.globalname + " >"

    @staticmethod
    def bases(node):
        return node.bases(False)
        #templatebases = [base for base in bases if isinstance(base, CxxClassTemplateProxy) and base.access == 'public']
        #specializationbases = [base for base in bases if isinstance(base, CxxClassSpecializationProxy) and base.access == 'public']
        #bases = [base for base in bases if not isinstance(base, (CxxClassTemplateProxy, CxxClassSpecializationProxy)) and base.access == 'public']
        #while len(templatebases)+len(specializationbases) > 0:
        #    _bases = itertools.chain(*[template.bases() for template in templatebases])
        #    templatebases = [base for base in _bases if isinstance(base, CxxClassTemplateProxy) and base.access == 'public']
        #    specializationbases += [base for base in _bases if isinstance(base, CxxClassSpecializationProxy) and base.access == 'public']
        #    bases += [base for base in _bases if not isinstance(base, (CxxClassTemplateProxy, CxxClassSpecializationProxy)) and base.access == 'public']
        #    _bases = itertools.chain(*[specialization.specialize.bases() for specialization in specializationbases])
        #    templatebases += [base for base in _bases if isinstance(base, CxxClassTemplateProxy) and base.access == 'public']
        #    specializationbases = [base for base in _bases if isinstance(base, CxxClassSpecializationProxy) and base.access == 'public']
        #    bases += [base for base in _bases if not isinstance(base, (CxxClassTemplateProxy, CxxClassSpecializationProxy)) and base.access == 'public']
        #return bases

    @staticmethod
    def supplementary_methods(node):
        #bases = [base for base in node.bases(False) if isinstance(base, (CxxClassTemplateProxy, CxxClassSpecializationProxy)) and base.access == 'public']
        #methods = []
        #while len(bases) > 0:
        #    methods += list(itertools.chain(*[base.methods() for base in bases if isinstance(base, CxxClassTemplateProxy)]))
        #    bases = [base.specialize for base in bases if isinstance(base, CxxClassSpecializationProxy)]+[base for base in itertools.chain(*[base.bases() for base in bases if isinstance(base, CxxClassTemplateProxy)]) if isinstance(base, (CxxClassTemplateProxy, CxxClassSpecializationProxy))]
        return []

    @staticmethod
    def path(node):
        filename = os.sep.join(node.scope.globalname.split('::')) + 'export_'
        if isinstance(node, CxxEnumProxy):
            filename += 'enum_'
        elif isinstance(node, CxxVariableProxy):
            filename += 'variable_'
        elif isinstance(node, CxxFunctionProxy):
            filename += 'function_'
        elif isinstance(node, CxxClassProxy):
            filename += 'class_'
        else:
            raise TypeError('`node` parameter')
        return ''.join('_' + c.lower() if c.isupper() else c for c in filename + node.localname).lstrip('_').replace('__', '_')  + '.cxx'

    @property
    def includes(self):
        return set(["\"" + export.header.globalname + "\"" for export in self.exports if hasattr(export, 'header')])

    @property
    def exports(self):
        return [self._asg[node] for node in self._asg._exportedges[self._node]]

    @property
    def enums(self):
        return [enum for enum in self.exports if isinstance(enum, CxxEnumProxy)]

    @property
    def functions(self):
        return [function for function in self.exports if isinstance(function, CxxFunctionProxy)]

    @property
    def classes(self):
        return [clss for clss in self.exports if isinstance(clss, CxxClassProxy)]

    @staticmethod
    def methodname(method):
        funcname = method.localname
        pattern = re.compile('operator(.*)')
        if pattern.match(funcname):
            operator = pattern.split(funcname)[1].replace(' ', '')
            if operator == '+':
                return '__add__'
            elif operator == '-':
                return '__sub__'
            elif operator == '*':
                return '__mul__'
            elif operator == '/':
                return '__div__'
            elif operator == '%':
                return '__mod__'
            elif operator == '==':
                return '__eq__'
            elif operator == '!=':
                return '__eq__'
            elif operator == '>':
                return '__gt__'
            elif operator == '<':
                return '__lt__'
            elif operator == '>=':
                return '__ge__'
            elif operator == '<=':
                return '__le__'
            elif operator == '!':
                return '__not__'
            elif operator == '&&':
                return '__and__'
            elif operator == '||':
                return '__or__'
            elif operator == '~':
                return '__invert__'
            elif operator == '&':
                return '__and__'
            elif operator == '|':
                return '__or__'
            elif operator == '^':
                return '__xor__'
            elif operator == '<<':
                return '__lshift__'
            elif operator == '>>':
                return '__rshift__'
            elif operator == '+=':
                return '__iadd__'
            elif operator == '-=':
                return '__isub__'
            elif operator == '*=':
                return '__imul__'
            elif operator == '/=':
                return '__idiv__'
            elif operator == '%=':
                return '__imod__'
            elif operator == '&=':
                return  '__iand__'
            elif operator == '|=':
                return '__ior__'
            elif operator == '^=':
                return '__ixor__'
            elif operator == '<<=':
                return '__ilshift__'
            elif operator == '>>=':
                return '__irshift__'
            elif operator == '[]':
                if method.const:
                    return '__getitem__'
                else:
                    return '__setitem__'
            elif operator == '()':
                return '__call__'
            else:
                return NotImplemented
        else:
            return funcname

class BoostPythonModuleFileProxy(CxxFileProxy):

    _template = Template("""\
/***************************************************************************/
/*   This file was automatically generated using VPlants.AutoWIG package   */
/*                                                                         */
/* Any modification of this file will be lost if VPlants.AutoWIG is re-run */
/***************************************************************************/

% for export in obj.parent.glob('*export_*.cxx', True):
void ${export.localname.replace('.cxx', '')}();
% endfor

BOOST_PYTHON_MODULE(_${obj.localname.replace('.cxx', '')})
{
% for export in obj.parent.glob('*export_*.cxx'):
    ${export.localname.replace('.cxx', '')}();
% endfor
}

void init_bindings()
{
    Py_Initialize();
    init_${obj.localname.replace('.cxx', '')}();
}""")

    @staticmethod
    def path(node):
        return node.globalname + 'module.cxx'

    def write(self):
        filehandler = open(self.globalname, 'w')
        try:
            filehandler.write(str(self))
        except:
            filehandler.close()
            raise
        else:
            filehandler.close()

class BoostPythonTraversal(object):
    """
    """

    def __init__(self, node="::", directory='.', export_proxy=BoostPythonExportFileProxy, module_proxy=BoostPythonModuleFileProxy):
        self.node = node
        self.directory = directory
        if not self.directory[-1] == os.sep:
            self.directory += os.sep
        self.export_proxy = export_proxy
        self.module_proxy = module_proxy

    def __call__(self, asg):
        """
        """
        if not isinstance(asg, AbstractSemanticGraph):
            raise TypeError('`asg` parameter')
        if self.node in asg:
            if not hasattr(asg, '_exportedges'):
                asg._exportedges = dict()
            if not self.directory in asg._nodes:
                filename = self.directory
                asg._nodes[filename] = dict(proxy = DirectoryProxy)
                asg._diredges[filename] = []
                dirname = filename[:filename.rfind(os.sep, 0, -1)+1]
                while not dirname == '' and not dirname in asg._nodes:
                    asg._nodes[dirname] = dict(proxy = DirectoryProxy)
                    asg._diredges[dirname] = [filename]
                    filename = dirname
                    dirname = filename[:filename.rfind(os.sep, 0, -1)+1]
                if not dirname == '':
                    asg._diredges[dirname].append(filename)
            visited = set()
            unvisited = [asg[self.node]]
            while len(unvisited) != 0:
                node = unvisited.pop()
                if not node.ignore:
                    if isinstance(node, CxxNamespaceProxy):
                        declarations = [declaration for declaration in node.declarations(nested=False) if not declaration.ignore and not declaration.hashname in visited]
                        unvisited.extend(declarations)
                        visited.update([declaration.hashname for declaration in declarations])
                    elif not isinstance(node, CxxClassTemplateProxy):
                        try:
                            exportnode = self.directory + self.export_proxy.path(node)
                            if not exportnode in asg._nodes:
                                asg._add_file(exportnode, file_proxy = self.export_proxy)
                            if not exportnode in asg._exportedges:
                                asg._exportedges[exportnode] = []
                            asg._exportedges[exportnode].append(node._node)
                            if isinstance(node, CxxClassProxy):
                                enums = [enum for enum in node.enums() if not enum.ignore and not enum.hashname in visited and enum.access == 'public']
                                unvisited.extend(enums)
                                visited.update([enum.hashname for enum in enums])
                                classes = [clss for clss in node.classes() if not clss.ignore and not clss.hashname in visited and clss.access == 'public']
                                unvisited.extend(classes)
                                visited.update([clss.hashname for clss in classes])
                        except:
                            raise
                    else:
                        pass
            for dir in [asg[self.directory]]+asg[self.directory].walkdirs():
                modulenode = self.module_proxy.path(dir)
                asg._add_file(modulenode, file_proxy=self.module_proxy)
