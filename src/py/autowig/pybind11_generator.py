## Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ##
##                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
## Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
##                                                                       ##
## This file is part of the AutoWIG project. More information can be     ##
## found at                                                              ##
##                                                                       ##
##     http://autowig.rtfd.io                                            ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

"""
"""

from mako.template import Template
from operator import attrgetter
from functools import partial

import multiprocessing
import os
import parse

from .asg import (AbstractSemanticGraph,
                  NodeProxy,
                  ClassTemplateSpecializationProxy,
                  EnumeratorProxy,
                  ClassTemplatePartialSpecializationProxy,
                  DeclarationProxy,
                  ClassProxy,
                  FileProxy,
                  FieldProxy,
                  FundamentalTypeProxy,
                  ClassTemplateProxy,
                  VariableProxy,
                  MethodProxy,
                  DestructorProxy,
                  NamespaceProxy,
                  TypedefProxy,
                  EnumerationProxy,
                  FunctionProxy,
                  ConstructorProxy,
                  QualifiedTypeProxy,
                  ParameterProxy)
from ._node_path import node_path
from ._node_rename import node_rename
from ._documenter import documenter
from .asg import visitor
from .plugin import ProxyManager, PluginManager
from ._node_rename import PYTHON_OPERATOR

__all__ = ['pybind11_call_policy', 'pybind11_export', 'pybind11_module', 'pybind11_decorator', 'TO', 'FROM']

def PARALLEL_WRITER(node, asg):
    return asg[node].write()

TO = {}

FROM = {}

IGNORE = {"class ::std::shared_ptr",
          "class ::std::unique_ptr",
          "class ::pybind11::handle",
          "class ::pybind11::object",
          "class ::pybind11::bool_",
          "class ::pybind11::int_",
          "class ::pybind11::float_",
          "class ::pybind11::str",
          "class ::pybind11::bytes",
          "class ::pybind11::tuple",
          "class ::pybind11::list",
          "class ::pybind11::dict",
          "class ::pybind11::slice",
          "class ::pybind11::none",
          "class ::pybind11::capsule",
          "class ::pybind11::iterable",
          "class ::pybind11::iterator",
          "class ::pybind11::function",
          "class ::pybind11::buffer",
          "class ::pybind11::array",
          "class ::pybind11::array_t"}

ENUMERATOR = Template(text="""\
    module.attr("${node_rename(enumerator)}") = (int)(${enumerator.globalname});\
""")

ENUMERATION = Template(text=r"""\
    pybind11::enum_< ${enumeration.globalname.replace("enum ", "")} > enum_${enumeration.hash}(module, "${node_rename(enumeration)}");
    % if enumeration.is_scoped:
        % for enumerator in enumeration.enumerators:
            % if enumerator.pybind11_export:
    enum_${enumeration.hash}.value("${node_rename(enumerator)}", ${enumerator.globalname});
            % endif
        % endfor
    % else:
        % for enumerator in enumeration.enumerators:
            % if enumerator.pybind11_export:
    enum_${enumeration.hash}.value("${node_rename(enumerator)}", ${enumerator.globalname[::-1].replace((enumeration.localname + '::')[::-1], '', 1)[::-1]});
            % endif
        % endfor
    enum_${enumeration.hash}.export_values();
    % endif""")

VARIABLE = Template(text="""\
    module.attr("${node_rename(variable)}") = ${variable.globalname};\
""")

FUNCTION_POINTER = Template(text=r"""\
${function.return_type.globalname} (*function_pointer_${function.hash})(${", ".join(parameter.qualified_type.globalname for parameter in function.parameters)}) = ${function.globalname};
""")

FUNCTION = Template(text=r"""\
    module.def("${node_rename(function)}", function_pointer_${function.hash}\
        % if function.pybind11_call_policy:
, ${function.pybind11_call_policy}\
        % endif
, "${documenter(function)}");""")

ERROR = Template(text=r"""\
    pybind11::register_exception< ${error.globalname} >(module, "${node_rename(error)}");
""")

ABSTRACT_CLASS = Template(text=r"""\
namespace autowig
{
    typedef ${cls.globalname.replace('struct ', '', 1).replace('class ', '', 1)} class_type;

    class Trampoline : public class_type
    {
        public:
% if any(cls.constructors(access='public')):
            using ${cls.globalname.replace('struct ', '', 1).replace('class ', '', 1)}::${cls.constructors(access='public')[0].localname};
% endif

        % for mtd in cls.methods(access="private", inherited=True, strict=True):
            %if mtd.is_virtual and mtd.pybind11_export:

        ${mtd.access}:
            typedef ${mtd.return_type.globalname} return_type_${mtd.hash};
                % for parameter in mtd.parameters:
            typedef ${parameter.qualified_type.globalname} param_${mtd.hash}_${parameter.index}_type;
                % endfor
            virtual return_type_${mtd.hash} ${mtd.localname}(${', '.join('param_' + mtd.hash + '_' + str(parameter.index) + '_type param_' + str(parameter.index) for parameter in mtd.parameters)}) \
                % if mtd.is_const:
const \
                % endif
override { PYBIND11_OVERLOAD\
                % if mtd.is_pure:
_PURE\
                % endif
                % if mtd.return_type.is_std_unique_ptr:
_UNIQUE_PTR\
                % endif
(return_type_${mtd.hash}, class_type, ${mtd.localname}, ${', '.join('param_' + str(parameter.index) for parameter in mtd.parameters)}); };
            % endif
        % endfor
    };
% if any([mtd for mtd in cls.methods(inherited=True, strict=True, access="private") if not mtd.access == "public" and mtd.is_virtual]):

    class Publicist : public class_type
    {
        public:
    % for mtd in cls.methods(inherited=True, strict=True, access="private"):
        % if not mtd.access == "public" and mtd.is_virtual and mtd.pybind11_export:
            using class_type::${mtd.localname};
        % endif
    % endfor
    };
% endif
}
""")

METHOD_DECORATOR = Template(text=r"""\
namespace autowig {
    % for method in cls.methods(access='public'):
        % if method.pybind11_export and method.return_type.desugared_type.is_reference and not method.return_type.desugared_type.is_const and method.return_type.desugared_type.unqualified_type.is_assignable:
    void method_decorator_${method.hash}\
(${cls.globalname + " const" * bool(method.is_const) + " & instance, " + \
   ", ".join(parameter.qualified_type.globalname + ' param_in_' + str(parameter.index) for parameter in method.parameters) + ", " * bool(method.nb_parameters > 0)}\
            % if method.return_type.desugared_type.is_fundamental_type:
${method.return_type.desugared_type.unqualified_type.globalname}\
            % else:
const ${method.return_type.globalname}\
            % endif
 param_out) { instance.${method.localname}\
(${", ".join('param_in_' + str(parameter.index) for parameter in method.parameters)}) = param_out; }
        % endif
    % endfor
}""")

METHOD_POINTERS = Template(text=r"""\
% for method in cls.methods(access='public'):
    % if method.pybind11_export:
${method.return_type.globalname} (\
        % if not method.is_static:
${method.parent.globalname.replace('class ', '').replace('struct ', '').replace('union ', '')}::\
        % endif
*method_pointer_${method.hash})(${", ".join(parameter.qualified_type.globalname for parameter in method.parameters)})\
        % if method.is_const:
const\
        % endif
= \
        % if not method.is_static:
&\
        % endif
${method.globalname};
    % endif
% endfor
""")

CLASS = Template(text=r"""\
    % if any(function.pybind11_export for function in cls.functions()):
    struct function_group
    {
        % for function in cls.functions():
            % if function.pybind11_export:
        static ${function.return_type.globalname} function_${function.hash}\
(${", ".join(parameter.qualified_type.globalname + " parameter_" + str(index) for index, parameter in enumerate(function.parameters))})
        { \
            % if not function.return_type.globalname == 'void':
return \
            % endif
            % if function.is_operator:
${function.localname}\
            % else:
${function.globalname}\
            % endif
(${', '.join('parameter_' + str(index) for index in range(function.nb_parameters))}); }
            % endif
        % endfor
    };
    % endif
    pybind11::class_<${cls.globalname}, \
    % if cls.is_abstract:
autowig::Trampoline, \
    % endif
autowig::\
    % if not cls.is_deletable:
NoDelete\
    % endif
HolderType< ${cls.globalname} >::Type\
    % if any(base for base in cls.bases(access='public') if base.pybind11_export):
, ${", ".join(base.globalname for base in cls.bases(access='public') if base.pybind11_export)}\
    % endif
 > class_${cls.hash}(module, "${node_rename(cls)}", "${documenter(cls)}");
        % for constructor in cls.constructors(access = 'public'):
            % if constructor.pybind11_export and not (cls.is_abstract and constructor.is_copy_constructor):
    class_${cls.hash}.def(pybind11::init< ${", ".join(parameter.qualified_type.globalname for parameter in constructor.parameters)} >());
            % endif
        % endfor
    % for method in cls.methods(access = 'public'):
        % if method.pybind11_export:
    class_${cls.hash}.def\
            % if method.is_static:
_static\
            % endif
("${node_rename(method)}", method_pointer_${method.hash}, \
                % if method.pybind11_call_policy:
${method.pybind11_call_policy}, \
                % endif
"${documenter(method)}");
                % if method.return_type.desugared_type.is_reference and not method.return_type.desugared_type.is_const and method.return_type.desugared_type.unqualified_type.is_assignable:
    class_${cls.hash}.def("${node_rename(method)}", autowig::method_decorator_${method.hash});
                % endif
        % endif
    % endfor
    % if cls.is_abstract:
        % for mtd in cls.methods(access='private', inherited=True, strict=True):
            % if mtd.is_virtual and not mtd.access == 'public' and mtd.pybind11_export:
    class_${cls.hash}.def("_\
                % if mtd.access == 'private':
_\
                % endif
${node_rename(mtd)}", static_cast< ${mtd.type(desugared=False)} >(&autowig::Publicist::${mtd.localname}), \
                % if mtd.pybind11_call_policy:
${mtd.pybind11_call_policy}, \
                % endif
"${documenter(mtd)}");
            % endif
        % endfor
    % endif
    % for function in cls.functions():
        % if function.pybind11_export:
    class_${cls.hash}.def("${node_rename(function)}", function_group::function_${function.hash}, \
                % if function.pybind11_call_policy:
${function.pybind11_call_policy}, \
                % endif
"${documenter(function)}");
        % endif
    % endfor
    % for field in cls.fields(access = 'public'):
        % if field.pybind11_export:
            % if field.qualified_type.is_const:
    class_${cls.hash}.def_readonly\
            % else:
    class_${cls.hash}.def_readwrite\
            % endif
            % if field.is_static:
_static\
            % endif
("${node_rename(field)}", &${field.globalname}, "${documenter(field)}");
        % endif
    % endfor
""")


def get_pybind11_call_policy(self):
    if hasattr(self, '_pybind11_call_policy'):
        return self._pybind11_call_policy
    else:
        return pybind11_call_policy(self)

def set_pybind11_call_policy(self, call_policy):
    self._asg._nodes[self._node]['_pybind11_call_policy'] = call_policy

def del_pybind11_call_policy(self):
    self._asg._nodes[self._node].pop('_pybind11_call_policy', None)

FunctionProxy.pybind11_call_policy = property(get_pybind11_call_policy, set_pybind11_call_policy, del_pybind11_call_policy)
del get_pybind11_call_policy, set_pybind11_call_policy, del_pybind11_call_policy

pybind11_call_policy = PluginManager('autowig.pybind11_call_policy', brief="AutoWIG PyBind11 call policy plugin_managers",
        details="")

def pybind11_default_call_policy(node):
    if isinstance(node, MethodProxy):
        return_type = node.return_type.desugared_type
        if return_type.is_pointer:
            return 'pybind11::return_value_policy::reference_internal'
        elif return_type.is_reference:
            if return_type.is_const or isinstance(return_type.unqualified_type, (FundamentalTypeProxy, EnumerationProxy)):
                return 'pybind11::return_value_policy::copy'
            else:
                return 'pybind11::return_value_policy::reference_internal'
    elif isinstance(node, FunctionProxy):
        return_type = node.return_type.desugared_type
        if return_type.is_pointer:
            return 'pybind11::return_value_policy::reference'
        elif return_type.is_reference:
            if return_type.is_const or isinstance(return_type.unqualified_type, (FundamentalTypeProxy, EnumerationProxy)):
                return 'pybind11::return_value_policy::copy'
            else:
                return 'pybind11::return_value_policy::reference'

def pybind11_visitor(node):
    if getattr(node, 'pybind11_export', False):
        return True
    else:
        return isinstance(node, FundamentalTypeProxy)

def pybind11_closure_visitor(node):
    if isinstance(node, FundamentalTypeProxy):
        return True
    else:
        pybind11_export = getattr(node, 'pybind11_export', False)
        return isinstance(pybind11_export, bool) and pybind11_export

def get_pybind11_export(self):
    desugared_type = self.desugared_type
    if desugared_type.is_pointer_chain or desugared_type.is_rvalue_reference:
        return False
    elif desugared_type.is_fundamental_type:
        return not desugared_type.is_pointer
    else:
        if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
            if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                return False
        return desugared_type.unqualified_type.pybind11_export

def set_pybind11_export(self, pybind11_export):
    if isinstance(pybind11_export, NodeProxy):
        pybind11_export = pybind11_export._node
    self.desugared_type.unqualified_type.pybind11_export = pybind11_export

def del_pybind11_export(self):
    del self.desugared_type.unqualified_type.pybind11_export

QualifiedTypeProxy.pybind11_export = property(get_pybind11_export, set_pybind11_export, del_pybind11_export)
del get_pybind11_export

def get_pybind11_export(self):
    desugared_type = self.qualified_type.desugared_type
    if desugared_type.is_pointer_chain or desugared_type.is_rvalue_reference:
        return False
    elif desugared_type.is_fundamental_type:
        return not desugared_type.is_pointer
    else:
        if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
            if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                return False
        return desugared_type.unqualified_type.pybind11_export

ParameterProxy.pybind11_export = property(get_pybind11_export, set_pybind11_export, del_pybind11_export)
del get_pybind11_export, set_pybind11_export, del_pybind11_export

def get_pybind11_export(self):
    if hasattr(self, '_pybind11_export'):
        pybind11_export = self._pybind11_export
        if isinstance(pybind11_export, bool):
            return pybind11_export
        else:
            return self._asg[pybind11_export]
    elif self.globalname == '::':
        return True
    else:
        return self._valid_pybind11_export and self._default_pybind11_export

def set_pybind11_export(self, pybind11_export):
    if not self._valid_pybind11_export and pybind11_export:
        raise ValueError('\'pybind11_export\' cannot be set to another value than \'False\'')
    if isinstance(pybind11_export, str):
        pybind11_export = self._asg[pybind11_export]
    elif not isinstance(pybind11_export, (bool, PyBind11ExportFileProxy)):
        raise TypeError('\'pybind11_export\' parameter must be boolean, a \'' + PyBind11ExportFileProxy.__class__.__name__ + '\' instance or identifer')
    del self.pybind11_export
    if isinstance(pybind11_export, PyBind11ExportFileProxy):
        if '__declaration' in self._asg._nodes[pybind11_export._node]:
            del pybind11_export.declaration.pybind11_export
        self._asg._nodes[pybind11_export._node]['_declaration'] = self._node
        pybind11_export = pybind11_export._node
    self._asg._nodes[self._node]['_pybind11_export'] = pybind11_export

def del_pybind11_export(self):
    if hasattr(self, '_pybind11_export'):
        pybind11_export = self.pybind11_export
        if isinstance(pybind11_export, PyBind11ExportFileProxy):
            self._asg._nodes[pybind11_export._node].pop('_declaration')
        self._asg._nodes[self._node].pop('_pybind11_export', pybind11_export)

DeclarationProxy.pybind11_export = property(get_pybind11_export, set_pybind11_export, del_pybind11_export)
DeclarationProxy._default_pybind11_export = False

def _valid_pybind11_export(self):
    return getattr(self, 'access', False) in ['none', 'public']

NodeProxy._valid_pybind11_export = property(_valid_pybind11_export)
del _valid_pybind11_export

def _default_pybind11_export(self):
    return bool(self.parent.pybind11_export)

EnumeratorProxy._default_pybind11_export = property(_default_pybind11_export)

def _default_pybind11_export(self):
    return not self.localname.startswith('_') and len(self.enumerators) > 0 and bool(self.parent.pybind11_export)

EnumerationProxy._default_pybind11_export = property(_default_pybind11_export)

def _default_pybind11_export(self):
    return not self.localname.startswith('_') and bool(self.parent.pybind11_export)

NamespaceProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _default_pybind11_export(self):
    return not self.localname.startswith('_') and self.is_complete and bool(self.parent.pybind11_export)

ClassProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _default_pybind11_export(self):
    return not self.localname.startswith('_') and self.parent.pybind11_export

ClassTemplateProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _default_pybind11_export(self):
    return (self.specialize is None or bool(self.specialize.pybind11_export)) and bool(self.parent.pybind11_export)

ClassTemplateSpecializationProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _default_pybind11_export(self):
    if self.parent.pybind11_export:
        desugared_type = self.qualified_type.desugared_type
        if desugared_type.is_pointer or desugared_type.is_reference:
            return False
        else:
            if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
                if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                    return False
            return desugared_type.is_fundamental_type or bool(desugared_type.unqualified_type.pybind11_export)
    else:
        return False

VariableProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _valid_pybind11_export(self):
    if isinstance(self.parent, ClassTemplateProxy):
        return False
    else:
        return getattr(self, 'access', False) in ['none', 'public'] and not self.is_bit_field

FieldProxy._valid_pybind11_export = property(_valid_pybind11_export)

def _default_pybind11_export(self):
    if self.parent.pybind11_export:
        qualified_type = self.qualified_type
        return not qualified_type.is_reference and not qualified_type.is_pointer and (bool(qualified_type.unqualified_type.pybind11_export) or qualified_type.is_fundamental_type)
    else:
        return False

TypedefProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _default_pybind11_export(self):
    return bool(self.parent.pybind11_export)

FunctionProxy._default_pybind11_export = property(_default_pybind11_export)

def _valid_pybind11_export(self):
    if self.pybind11_call_policy == 'pybind11::return_value_policy::reference_internal':
        if not isinstance(self.return_type.desugared_type.unqualified_type, ClassProxy):
            return False
    if self.return_type.pybind11_export and all(parameter.pybind11_export for parameter in self.parameters):
        return not self.localname.startswith('operator') or isinstance(self.parent, ClassProxy)
    else:
        return False

FunctionProxy._valid_pybind11_export = property(_valid_pybind11_export)
del _valid_pybind11_export

ConstructorProxy._default_pybind11_export = property(_default_pybind11_export)

def _valid_pybind11_export(self):
    return self.access == 'public' and all(parameter.pybind11_export for parameter in self.parameters)

ConstructorProxy._valid_pybind11_export = property(_valid_pybind11_export)
del _default_pybind11_export, _valid_pybind11_export

def _default_pybind11_export(self):
    if self.is_virtual:
        try:
            return self.overrides is None
        except:
            return self.is_pure
    else:
        return bool(self.parent.pybind11_export)

MethodProxy._default_pybind11_export = property(_default_pybind11_export)
del _default_pybind11_export

def _valid_pybind11_export(self):
    if isinstance(self.parent, ClassTemplateProxy):
        return False
    else:
        if self.return_type.desugared_type.is_reference and self.return_type.desugared_type.is_pointer and not self.return_type.desugared_type.is_const:
            return False
        if any(parameter.qualified_type.desugared_type.is_reference and parameter.qualified_type.desugared_type.is_pointer and not parameter.qualified_type.is_const for parameter in self.parameters):
            return False
        if self.pybind11_call_policy in ['pybind11::return_value_policy::reference_internal',
                                         'pybind11::return_value_policy::reference']:
            if not isinstance(self.return_type.desugared_type.unqualified_type, ClassProxy):
                return False
        if (self.access == 'public'or self.parent.is_abstract) and self.return_type.pybind11_export and all(bool(parameter.pybind11_export) for parameter in self.parameters):
            return not self.localname.startswith('operator') or self.localname.strip('operator').strip() in PYTHON_OPERATOR
        else:
            return False

MethodProxy._valid_pybind11_export = property(_valid_pybind11_export)
del _valid_pybind11_export

class PyBind11ExportFileProxy(FileProxy):

    language = 'c++'

    @property
    def _clean_default(self):
        return '_declaration' not in self._asg._nodes[self._node]

    def __init__(self, asg, node):
        super(PyBind11ExportFileProxy, self).__init__(asg, node)

    @property
    def module(self):
        if hasattr(self, '_module'):
            return self._asg[self._module]

    @module.setter
    def module(self, module):
        del self.module
        if isinstance(module, PyBind11ModuleFileProxy):
            module = module._node
        self._asg._nodes[self._node]['_module'] = module
        self._asg._nodes[module]['_exports'].add(self._node)

    @module.deleter
    def module(self):
        module = self.module
        if module:
            self._asg._nodes[module._node]['_exports'].remove(self._node)
        self._asg._nodes[self._node].pop('_module', None)

    @property
    def header(self):
        module = self.module
        if module:
            return module.header

    @property
    def is_empty(self):
        return '_declaration' not in self._asg._nodes[self._node]

    @property
    def depth(self):
        if self.is_empty:
            return 0
        else:
            depth = 0
            declaration = self.declaration
            if isinstance(declaration, ClassProxy):
                depth = declaration.depth
            elif isinstance(declaration, VariableProxy):
                target = declaration.qualified_type.desugared_type.unqualified_type
                if isinstance(target, ClassProxy):
                    depth = target.depth + 1
            return depth

    @property
    def scope(self):
        if not self.is_empty:
            return self.declaration.parent

    @property
    def scopes(self):
        if not self.is_empty:
            return self.declaration.ancestors[1:]
           
    @property
    def declaration(self):
        if hasattr(self, '_declaration'):
            return self._asg[self._declaration]

    def get_content(self):
        content = '#include "' + self.header.localname + '"\n'
        declaration = self.declaration
        if isinstance(declaration, ClassProxy) and not declaration.is_error:
            if declaration.is_abstract:
                content += '\n' + ABSTRACT_CLASS.render(cls = declaration,
                        node_rename = node_rename,
                        documenter = documenter)
            content += '\n' + METHOD_POINTERS.render(cls = declaration,
                    node_rename = node_rename,
                    documenter = documenter)
            content += '\n' + METHOD_DECORATOR.render(cls = declaration,
                    node_rename = node_rename,
                    documenter = documenter)
        elif isinstance(declaration, FunctionProxy):
            content += '\n' + FUNCTION_POINTER.render(function = declaration,
                    node_rename = node_rename,
                    documenter = documenter)
        content += '\n\nvoid ' + self.prefix + '(pybind11::module& module)\n{\n' 
        if isinstance(declaration, EnumeratorProxy):
            content += '\n' + ENUMERATOR.render(enumerator = declaration,
                    node_rename = node_rename,
                    documenter = documenter)
        elif isinstance(declaration, EnumerationProxy):
            if declaration.globalname not in IGNORE:
                content += '\n' + ENUMERATION.render(enumeration = declaration,
                                        node_rename = node_rename,
                                        documenter = documenter)
        elif isinstance(declaration, VariableProxy):
            content += '\n' + VARIABLE.render(variable = declaration,
                    node_rename = node_rename,
                    documenter = documenter)
        elif isinstance(declaration, FunctionProxy):
            content += '\n' + FUNCTION.render(function = declaration,
                    node_rename = node_rename,
                    documenter = documenter)
        elif isinstance(declaration, ClassTemplateSpecializationProxy):
            if declaration.globalname not in IGNORE and declaration.specialize.globalname not in IGNORE:
                if declaration.is_error:
                    content += '\n\n' + ERROR.render(error = declaration,
                                                     node_rename = node_rename,
                                                     documenter = documenter)
                else:
                    content += '\n' + CLASS.render(cls = declaration,
                            node_rename = node_rename,
                            documenter = documenter)
            if declaration.specialize.globalname in TO:
                content += '\n' + TO[declaration.specialize.globalname].render(cls = declaration)
            elif declaration.globalname in TO:
                content += '\n' + TO[declaration.globalname].render(cls = declaration)
            if declaration.specialize.globalname in FROM:
                content += '\n' + FROM[declaration.specialize.globalname].render(cls = declaration)
            elif declaration.globalname in FROM:
                content += '\n' + FROM[declaration.globalname].render(cls = declaration)
        elif isinstance(declaration, ClassProxy):
            if declaration.globalname not in IGNORE:
                if declaration.is_error:
                    content += '\n\n' + ERROR.render(error = declaration,
                                                     node_rename = node_rename,
                                                     documenter = documenter)
                else:
                    content += '\n' + CLASS.render(cls = declaration,
                            node_rename = node_rename,
                            documenter = documenter)
            if declaration.globalname in TO:
                content += '\n' + TO[declaration.globalname].render(cls = declaration)
            if declaration.globalname in FROM:
                content += '\n' + FROM[declaration.globalname].render(cls = declaration)
        elif isinstance(declaration, TypedefProxy):
            pass
        else:
            raise NotImplementedError(declaration.__class__.__name__)
        content += '\n}'
        return content

    def edit(self, row):
        return ""

PyBind11ExportFileProxy._content = property(PyBind11ExportFileProxy.get_content)

def pybind11_exports(self, *args, **kwargs):
    return [export for export in self.files(*args, **kwargs) if isinstance(export, PyBind11ExportFileProxy)]

AbstractSemanticGraph.pybind11_exports = pybind11_exports
del pybind11_exports

pybind11_export = ProxyManager('autowig.pybind11_export', brief="",
        details="")

class PyBind11HeaderFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return self.module._clean_default

    CONTENT = Template(text=r"""\
#pragma once

#include <pybind11/pybind11.h>
% if include_stl:
#include <pybind11/stl.h>
% endif

#include <memory>\
% for header in headers:

    % if header.language == 'c':
extern "C" {
    % endif
#include <${header.searchpath}>\
    % if header.language == 'c':

}\
    % endif
% endfor


#define PYBIND11_OVERLOAD_UNIQUE_PTR_INT(ret_type, cname, name, ...) { ${"\\"}
        pybind11::gil_scoped_acquire gil; ${"\\"}
        pybind11::function overload = pybind11::get_overload(static_cast<const cname *>(this), name); ${"\\"}
        if (overload) { ${"\\"}
            auto o = overload(__VA_ARGS__); ${"\\"}
            if (pybind11::detail::cast_is_temporary_value_reference<ret_type::pointer>::value) { ${"\\"}
                static pybind11::detail::overload_caster_t<ret_type::pointer> caster; ${"\\"}
                return std::unique_ptr< ret_type::element_type >(pybind11::detail::cast_ref<ret_type::pointer>(std::move(o), caster)); ${"\\"}
            } ${"\\"}
            else return std::unique_ptr< ret_type::element_type >(pybind11::detail::cast_safe<ret_type::pointer>(std::move(o))); ${"\\"}
        } ${"\\"}
    }

#define PYBIND11_OVERLOAD_UNIQUE_PTR_NAME(ret_type, cname, name, fn, ...) ${"\\"}
    PYBIND11_OVERLOAD_UNIQUE_PTR_INT(ret_type, cname, name, __VA_ARGS__) ${"\\"}
    return cname::fn(__VA_ARGS__)

#define PYBIND11_OVERLOAD_PURE_UNIQUE_PTR_NAME(ret_type, cname, name, fn, ...) ${"\\"}
    PYBIND11_OVERLOAD_UNIQUE_PTR_INT(ret_type, cname, name, __VA_ARGS__) ${"\\"}
    pybind11::pybind11_fail("Tried to call pure virtual function \"" #cname "::" name "\"");

#define PYBIND11_OVERLOAD_UNIQUE_PTR(ret_type, cname, fn, ...) ${"\\"}
    PYBIND11_OVERLOAD_UNIQUE_PTR_NAME(ret_type, cname, #fn, fn, __VA_ARGS__)

#define PYBIND11_OVERLOAD_PURE_UNIQUE_PTR(ret_type, cname, fn, ...) ${"\\"}
    PYBIND11_OVERLOAD_PURE_UNIQUE_PTR_NAME(ret_type, cname, #fn, fn, __VA_ARGS__)

namespace autowig
{
    template<class T> struct HolderType {
        typedef std::unique_ptr< T > Type;
    };

    template<class T> struct NoDeleteHolderType {
        typedef std::unique_ptr< T, pybind11::nodelete > Type;
    };
}""")

    @property
    def module(self):
        return self._asg[self.globalname.rstrip(self.suffix) + self._module]

    @property
    def content(self):
        return self.CONTENT.render(headers = [header for header in self._asg.files(header=True) if not header.is_external_dependency and header.is_self_contained],
                                   include_stl = self.include_stl)

    @property
    def include_stl(self):
        if not hasattr(self, "_include_stl"):
            return False
        else:
            return self._include_stl
    
    @include_stl.setter
    def include_stl(self, include):
        self._include_stl = include
    
    @include_stl.deleter
    def include_stl(self):
        del self._include_stl

class PyBind11ModuleFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return len(self._exports) == 0

    CONTENT = Template(text=r"""\
#include "${module.header.localname}"

% for export in module.exports:
    % if not export.is_empty:
void ${export.prefix}(pybind11::module& module);
    % endif
% endfor

PYBIND11_MODULE(_${module.prefix}, module_${module._asg['::'].hash})
{
<% modules = set() %>\
% for export in sorted(module.exports, key = lambda export: len(export.scopes)):
    % if not export.is_empty:
        % for scope in export.scope.ancestors + [export.scope]:
            % if not scope.globalname == '::' and not scope.hash in modules:

    pybind11::module module_${scope.hash} = module_${scope.parent.hash}.def_submodule("${node_rename(scope, scope=True).split('.')[-1]}", "");\
            %  endif
<% modules.add(scope.hash) %>\
        % endfor
    % endif
% endfor

% for export in module.exports:
    % if not export.is_empty:
    ${export.prefix}(module_${export.scope.hash});
    %endif
% endfor
}""")

    def __init__(self, asg, node):
        super(PyBind11ModuleFileProxy, self).__init__(asg, node)
        if not hasattr(self, '_exports'):
            self._asg._nodes[self._node]['_exports'] = set()

    @property
    def docstring_user_defined(self):
        if not hasattr(self, '_docstring_user_defined'):
            return True
        else:
            return self._docstring_user_defined

    @docstring_user_defined.setter
    def docstring_user_defined(self, docstring_user_defined):
        self._asg._nodes[self._node]['_docstring_user_defined'] = docstring_user_defined

    @property
    def docstring_py_signatures(self):
        if not hasattr(self, '_docstring_py_signatures'):
            return False
        else:
            return self._docstring_py_signatures

    @docstring_py_signatures.setter
    def docstring_py_signatures(self, docstring_py_signatures):
        self._asg._nodes[self._node]['_docstring_py_signatures'] = docstring_py_signatures

    @property
    def docstring_cpp_signatures(self):
        if not hasattr(self, '_docstring_cpp_signatures'):
            return False
        else:
            return self._docstring_cpp_signatures

    @docstring_cpp_signatures.setter
    def docstring_cpp_signatures(self, docstring_cpp_signatures):
        self._asg._nodes[self._node]['_docstring_cpp_signatures'] = docstring_cpp_signatures

    @property
    def header(self):
        return self._asg[self.globalname[:-len(self.suffix)] + '.' + 'h']

    @property
    def exports(self):
        if not hasattr(self, '_exports'):
            return []
        else:
            return [export for export in sorted(sorted([self._asg[export] for export in self._exports], key = attrgetter('globalname')), key = attrgetter('depth'))]

    #@property
    def get_dependencies(self):
        modules = set([self.globalname])
        temp = [export.declaration for export in self.exports]
        black = set()
        while len(temp) > 0:
            declaration = temp.pop()
            black.add(declaration._node)
            if isinstance(declaration, FunctionProxy):
                export = declaration.return_type.desugared_type.unqualified_type.pybind11_export
                if export and export is not True:
                    module = export.module
                    if module is not None:
                        modules.add(module.globalname)
                for prm in declaration.parameters:
                    export = prm.qualified_type.desugared_type.unqualified_type.pybind11_export
                    if export and export is not True:
                        module = export.module
                        if module is not None:
                            modules.add(module.globalname)
            elif isinstance(declaration, (VariableProxy, TypedefProxy)):
                export = declaration.qualified_type.desugared_type.unqualified_type.pybind11_export
                if export and export is not True:
                    module = export.module
                    if module is not None:
                        modules.add(module.globalname)
            elif isinstance(declaration, ClassProxy):
                export = declaration.pybind11_export
                if export and export is not True:
                    module = export.module
                    if module is not None:
                        modules.add(module.globalname)
                temp.extend([bse for bse in declaration.bases() if bse.access == 'public' and not bse._node in black])
                temp.extend([dcl for dcl in declaration.declarations() if dcl.access == 'public' and not dcl._node in black])
            elif isinstance(declaration, ClassTemplateProxy):
                export = declaration.pybind11_export
                if export and export is not True:
                    module = export.module
                    if module is None:
                        modules.add(module.globalname)
        modules.remove(self.globalname)
        return [self._asg[module] for module in modules]
      
    @property
    def depth(self):
        dependencies = self.dependencies
        if len(dependencies) == 0:
            return 0
        else:
            return max(dependency.depth for dependency in dependencies) + 1

    def get_content(self):
        return self.CONTENT.render(module = self,
                                   node_rename = node_rename)

    @property
    def decorator(self):
        if '_decorator' in self._asg._nodes[self._node]:
            return self._asg[self._decorator]

    @decorator.setter
    def decorator(self, decorator):
        if isinstance(decorator, str):
            decorator = self._asg[decorator]
        if not isinstance(decorator, PyBind11DecoratorFileProxy):
            raise TypeError("'decorator' parameter")
        if self.decorator and not self.decorator.module.globalname == decorator.globalname:
            del self.decorator.module
        self._asg._nodes[self._node]['_decorator'] = decorator._node
        self._asg._nodes[decorator._node]['_module'] = self._node

    @decorator.deleter
    def decorator(self):
        if self.decorator:
            del self.decorator.module
        self._asg._nodes[self._node].pop('_decorator', None)

    def write(self, header=True, exports=True, decorator=True, processes=1):
        super(PyBind11ModuleFileProxy, self).write()
        if processes > 1:
            args = []
            if header:
                args.append(self.header._node)
            if exports:
                args.extend([export._node for export in self.exports if not export.is_empty])
            if decorator:
                decorator = self.decorator
            if decorator:
                args.append(decorator._node)
            pool = multiprocessing.Pool(processes)
            pool.map(partial(PARALLEL_WRITER, asg=self._asg), args)
        else:
            super(PyBind11ModuleFileProxy, self).write()
            if header:
                self.header.write()
            if exports:
                for export in self.exports:
                    if not export.is_empty:
                        export.write()
            if decorator:
                decorator = self.decorator
            if decorator:
                decorator.write()

    def remove(self, header=True, exports=True, decorator=True):
        super(PyBind11ModuleFileProxy, self).remove()
        if header:
            self.header.remove()
        if exports:
            for export in self.exports:
                export.remove()
        if decorator:
            self.decorator.remove()

PyBind11ModuleFileProxy.dependencies = property(PyBind11ModuleFileProxy.get_dependencies)

PyBind11ModuleFileProxy._content = property(PyBind11ModuleFileProxy.get_content)

def pybind11_modules(self, **kwargs):
    return [module for module in self.files(**kwargs) if isinstance(module, PyBind11ModuleFileProxy)]

AbstractSemanticGraph.pybind11_modules = pybind11_modules
del pybind11_modules

pybind11_module = ProxyManager('autowig.pybind11_module', brief="",
        details="")

class PyBind11DecoratorFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return not hasattr(self, '_module')

    @property
    def module(self):
        if hasattr(self, '_module'):
            return self._asg[self._module]

    @module.setter
    def module(self, module):
        if isinstance(module, str):
            module = self._asg[module]
        if not isinstance(module, PyBind11ModuleFileProxy):
            raise TypeError('\'module\' parameter')
        if self.module and not self.module.decorator.globalname == module.globalname:
            del self.module.decorator
        self._asg._nodes[self._node]['_module'] = module._node
        self._asg._nodes[module._node]['_decorator'] = self._node

    @module.deleter
    def module(self):
        if self.module:
            del self.module.decorator
        self._asg._nodes[self._node].pop('_module', None)

    @property
    def package(self):
        modules = []
        parent = self.parent
        while parent is not None and parent.globalname + '__init__.py' in self._asg:
            modules.append(parent.localname.strip(os.sep))
            parent = parent.parent
        return '.'.join(reversed(modules))


class PyBind11DecoratorDefaultFileProxy(PyBind11DecoratorFileProxy):

    IMPORTS = Template(text=r"""\
__all__ = []

% if any(dependency for dependency in dependencies):
# Import dependency decorator modules
    % for dependency in dependencies:
        % if dependency:
import ${dependency.package}.${dependency.prefix}
        % endif
    % endfor
% endif

# Import Boost.Python module
from . import _${module.prefix}
""")

    SCOPES = Template(text=r"""\
% if len(scopes) > 0:
# Resolve scopes
    % for scope in scopes:
_${module.prefix}.${".".join(node_rename(ancestor) for ancestor in scope.ancestors[1:])}.${node_rename(scope)} = \
_${module.prefix}.${".".join(node_rename(ancestor, scope=True) for ancestor in scope.ancestors[1:])}.${node_rename(scope)}
    % endfor
% endif
""")

    ABSTRACTS = Template(text=r"""\
% if len(abstracts) > 0:
# Resolve scopes
    % for abstract in abstracts:
_${module.prefix}.${".".join(node_rename(ancestor) for ancestor in abstract.ancestors[1:])}.${node_rename(abstract)}.__abstract__ = True
    % endfor
% endif
% if len(non_abstracts) > 0:
# Resolve scopes
    % for non_abstract in non_abstracts:
_${module.prefix}.${".".join(node_rename(ancestor) for ancestor in non_abstract.ancestors[1:])}.${node_rename(non_abstract)}.__abstract__ = False
    % endfor
% endif
""")

    TEMPLATES = Template(text=r"""\
% if templates:
# Group template specializations
    % for tpl, spcs in templates:
_${module.prefix}.\
        % if len(tpl.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tpl.ancestors[1:])}.${node_rename(tpl)} = \
(${", ".join(['_' + module.prefix + "." + ".".join(node_rename(ancestor) for ancestor in spc.ancestors[1:]) + "." + node_rename(spc) for spc in spcs])})
        % else:
${node_rename(tpl)} = (${", ".join(['_' + module.prefix + "." + node_rename(spc) for spc in spcs])})
        % endif
    % endfor
% endif""")

    TYPEDEFS = Template(text=r"""\
% if typedefs:
# Define aliases
    % for tdf in typedefs:
_${module.prefix}.\
        % if len(tdf.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.ancestors[1:])}.\
        % endif
<% target = tdf.qualified_type.desugared_type.unqualified_type.pybind11_export.module.decorator %>\
${node_rename(tdf)} = \
        % if target.globalname == module.decorator.globalname:
_${module.prefix}.\
        % else:
${target.package}._${target.module.prefix}.\
        % endif
        % if len(tdf.qualified_type.desugared_type.unqualified_type.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.qualified_type.desugared_type.unqualified_type.ancestors[1:])}.\
        % endif
${node_rename(tdf.qualified_type.desugared_type.unqualified_type)}
        % if tdf.is_local:
            % if target.globalname == module.decorator.globalname:
_${module.prefix}.\
            % else:
${target.package}._${target.module.prefix}.\
            % endif
            % if len(tdf.qualified_type.desugared_type.unqualified_type.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.qualified_type.desugared_type.unqualified_type.ancestors[1:])}.\
            % endif
${node_rename(tdf.qualified_type.desugared_type.unqualified_type)}.__alias__ = "${node_rename(tdf)}"
        % endif
    % endfor
% endif""")

    def get_content(self):

        def ignore(decl):
            if not decl.globalname in IGNORE:
                if isinstance(decl, NamespaceProxy):
                    return False
                elif isinstance(decl, ClassTemplateSpecializationProxy):
                    return ignore(decl.specialize) or ignore(decl.parent)
                elif isinstance(decl, TypedefProxy):
                    return ignore(decl.qualified_type.unqualified_type) or ignore(decl.parent)
                else:
                    return ignore(decl.parent)
            else:
                return True

        dependencies = [module for module in self.module.get_dependencies()]
        content = [self.IMPORTS.render(decorator = self, module = self.module, dependencies = [module.decorator for module in sorted(dependencies, key = lambda dependency: dependency.depth)])]
        scopes = []
        for export in self.module.exports:
            declaration = export.declaration
            if isinstance(declaration.parent, ClassProxy) and not ignore(declaration):
                scopes.append(declaration)
        content.append(self.SCOPES.render(scopes = sorted(scopes, key = lambda scope: len(scope.ancestors)), decorator = self, module = self.module,
                node_rename = node_rename))
        abstracts = []
        non_abstracts = []
        for export in self.module.exports:
            declaration = export.declaration
            if isinstance(declaration, ClassProxy) and not ignore(declaration):
                if declaration.is_abstract:
                    abstracts.append(declaration)
                else:
                    non_abstracts.append(declaration)
        content.append(self.ABSTRACTS.render(non_abstracts=non_abstracts, abstracts = abstracts, decorator = self, module = self.module,
                node_rename = node_rename))
        templates = dict()
        for export in self.module.exports:
            declaration = export.declaration
            if isinstance(declaration, ClassTemplateSpecializationProxy) and not ignore(declaration):
                spc = declaration.specialize.globalname
                if spc in templates:
                    templates[spc].append(declaration)
                else:
                    templates[spc] = [declaration]
        content.append(self.TEMPLATES.render(decorator = self, module = self.module, templates = [(self._asg[tpl], spcs) for tpl, spcs in templates.items()],
                node_rename = node_rename))
        typedefs = []
        for export in self.module.exports:
            for scope in export.scope.ancestors + [export.scope]:
                if isinstance(scope, NamespaceProxy) and not ignore(scope):
                    typedefs.extend([tdf for tdf in scope.typedefs() if tdf.pybind11_export and tdf.qualified_type.desugared_type.unqualified_type.pybind11_export and tdf.qualified_type.desugared_type.unqualified_type.pybind11_export is not True])
            declaration = export.declaration
            if isinstance(declaration, ClassProxy) and not ignore(declaration):
                typedefs.extend([tdf for tdf in declaration.typedefs() if tdf.pybind11_export and tdf.qualified_type.desugared_type.unqualified_type.pybind11_export and tdf.qualified_type.desugared_type.unqualified_type.pybind11_export is not True])
        typedefs = {tdf._node for tdf in typedefs}
        typedefs = [self._asg[tdf] for tdf in typedefs]
        content.append(self.TYPEDEFS.render(decorator = self, module = self.module, typedefs = typedefs, node_rename=node_rename))
        return "\n".join(content)


PyBind11DecoratorDefaultFileProxy._content = property(PyBind11DecoratorDefaultFileProxy.get_content)

pybind11_decorator = ProxyManager('autowig.pybind11_decorator', brief="",
        details="")

def pybind11_generator(asg, nodes, module='./module.cpp', decorator=None, **kwargs):
    """
    """

    if module in asg:
        module = asg[module]
    else:
        module = asg.add_file(module, proxy=pybind11_module())
        asg.add_file(module.globalname[:-len(module.suffix)] + '.' + 'h',
                     _module = module.suffix,
                     proxy= PyBind11HeaderFileProxy)

    directory = module.parent
    suffix = module.suffix
    prefix = kwargs.pop('prefix', 'wrapper_')

    if kwargs.pop('closure', True):
        plugin = visitor.plugin
        visitor.plugin = 'pybind11_closure'
        nodes += asg.dependencies(*nodes)
        visitor.plugin = plugin

    exports = set()
    for node in nodes:
        if node.pybind11_export is True and not node.globalname in IGNORE:
            if (isinstance(node, EnumeratorProxy) and isinstance(node.parent, (EnumerationProxy, ClassProxy))) or isinstance(node, TypedefProxy) or isinstance(node, (FieldProxy, MethodProxy, ConstructorProxy, DestructorProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy)) or (isinstance(node, FunctionProxy) and isinstance(node.parent, ClassProxy)):
                continue
            elif not isinstance(node, NamespaceProxy) and not any(isinstance(ancestor, ClassTemplateProxy) for ancestor in reversed(node.ancestors)):
                export = directory.globalname + node_path(node, prefix=prefix, suffix=suffix).strip('./')
                if export in asg:
                    export = asg[export]
                else:
                    export = asg.add_file(export, proxy=pybind11_export())
                node.pybind11_export = export
                exports.add(export._node)

    exports = [asg[export] for export in exports]
    for export in exports:
        export.module = module

    if decorator:
        if decorator in asg:
            decorator = asg[decorator]
        else:
            decorator = asg.add_file(decorator, proxy=pybind11_decorator())
        decorator.module = module
        parent = os.path.join(decorator.parent.globalname, '__init__.py')
        while os.path.exists(parent):
            parent = os.path.join(asg.add_file(parent).parent.parent.globalname, '__init__.py')

    if 'helder' in kwargs:
        module.header.helder = kwargs.pop('helder')

    return module

def pybind11_pattern_generator(asg, pattern=None, *args, **kwargs):
    """
    """
    return pybind11_generator(asg, asg.declarations(pattern=pattern), *args, **kwargs)


def pybind11_internal_generator(asg, pattern=None, *args, **kwargs):
    """
    """
    return pybind11_generator(asg,
                              [node for node in asg.declarations(pattern=pattern) if not getattr(node.header, 'is_external_dependency', True)],
                              *args, **kwargs)