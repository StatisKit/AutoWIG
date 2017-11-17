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
## file except in compliance with the License.You should have received a ##
## copy of the Apache License, Version 2.0 along with this file; see the ##
## file LICENSE. If not, you may obtain a copy of the License at         ##
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

__all__ = ['boost_python_call_policy', 'boost_python_export', 'boost_python_module', 'boost_python_decorator']

def get_boost_python_call_policy(self):
    if hasattr(self, '_boost_python_call_policy'):
        return self._boost_python_call_policy
    else:
        return boost_python_call_policy(self)

def set_boost_python_call_policy(self, call_policy):
    self._asg._nodes[self._node]['_boost_python_call_policy'] = call_policy

def del_boost_python_call_policy(self):
    self._asg._nodes[self._node].pop('_boost_python_call_policy', None)

FunctionProxy.boost_python_call_policy = property(get_boost_python_call_policy, set_boost_python_call_policy, del_boost_python_call_policy)
del get_boost_python_call_policy, set_boost_python_call_policy, del_boost_python_call_policy

boost_python_call_policy = PluginManager('autowig.boost_python_call_policy', brief="AutoWIG Boost.Python call policy plugin_managers",
        details="")

def boost_python_default_call_policy(node):
    if isinstance(node, MethodProxy):
        return_type = node.return_type.desugared_type
        if return_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif return_type.is_reference:
            if return_type.is_const or isinstance(return_type.unqualified_type, (FundamentalTypeProxy, EnumerationProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_internal_reference<>()'
    elif isinstance(node, FunctionProxy):
        return_type = node.return_type.desugared_type
        if return_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif return_type.is_reference:
            if return_type.is_const or isinstance(return_type.unqualified_type, (FundamentalTypeProxy, EnumerationProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'

def boost_python_visitor(node):
    if getattr(node, 'boost_python_export', False):
        return True
    else:
        return isinstance(node, FundamentalTypeProxy)

def boost_python_closure_visitor(node):
    if isinstance(node, FundamentalTypeProxy):
        return True
    else:
        boost_python_export = getattr(node, 'boost_python_export', False)
        return isinstance(boost_python_export, bool) and boost_python_export

def get_boost_python_export(self):
    desugared_type = self.desugared_type
    if desugared_type.is_pointer_chain or desugared_type.is_rvalue_reference:
        return False
    elif desugared_type.is_fundamental_type:
        return not desugared_type.is_pointer
    else:
        if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
            if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                return False
        return desugared_type.unqualified_type.boost_python_export

def set_boost_python_export(self, boost_python_export):
    if isinstance(boost_python_export, NodeProxy):
        boost_python_export = boost_python_export._node
    self.desugared_type.unqualified_type.boost_python_export = boost_python_export

def del_boost_python_export(self):
    del self.desugared_type.unqualified_type.boost_python_export

QualifiedTypeProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
del get_boost_python_export

def get_boost_python_export(self):
    desugared_type = self.qualified_type.desugared_type
    if desugared_type.is_pointer_chain or desugared_type.is_rvalue_reference:
        return False
    elif desugared_type.is_fundamental_type:
        return not desugared_type.is_pointer
    else:
        if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
            if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                return False
        return desugared_type.unqualified_type.boost_python_export

ParameterProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
del get_boost_python_export, set_boost_python_export, del_boost_python_export

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self._boost_python_export
        if isinstance(boost_python_export, bool):
            return boost_python_export
        else:
            return self._asg[boost_python_export]
    elif self.globalname == '::':
        return True
    else:
        return self._valid_boost_python_export and self._default_boost_python_export

def set_boost_python_export(self, boost_python_export):
    if not self._valid_boost_python_export and boost_python_export:
        raise ValueError('\'boost_python_export\' cannot be set to another value than \'False\'')
    if isinstance(boost_python_export, basestring):
        boost_python_export = self._asg[boost_python_export]
    if isinstance(boost_python_export, BoostPythonExportFileProxy):
        scope = boost_python_export.scope
        if scope and not scope == self.parent:
            raise ValueError()
    elif not isinstance(boost_python_export, bool):
        raise TypeError('\'boost_python_export\' parameter must be boolean, a \'' + BoostPythonExportFileProxy.__class__.__name__ + '\' instance or identifer')
    del self.boost_python_export
    if isinstance(boost_python_export, BoostPythonExportFileProxy):
        scope = boost_python_export.scope
        boost_python_export._declarations.add(self._node)
        boost_python_export = boost_python_export._node
    self._asg._nodes[self._node]['_boost_python_export'] = boost_python_export

def del_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self.boost_python_export
        if isinstance(boost_python_export, BoostPythonExportFileProxy):
            self._asg._nodes[boost_python_export._node]['_declarations'].remove(self._node)
        self._asg._nodes[self._node].pop('_boost_python_export', boost_python_export)

DeclarationProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
DeclarationProxy._default_boost_python_export = False

def _valid_boost_python_export(self):
    return getattr(self, 'access', False) in ['none', 'public']

NodeProxy._valid_boost_python_export = property(_valid_boost_python_export)
del _valid_boost_python_export

def _default_boost_python_export(self):
    return bool(self.parent.boost_python_export)

EnumeratorProxy._default_boost_python_export = property(_default_boost_python_export)

def _default_boost_python_export(self):
    return not self.localname.startswith('_') and len(self.enumerators) > 0 and bool(self.parent.boost_python_export)

EnumerationProxy._default_boost_python_export = property(_default_boost_python_export)

def _default_boost_python_export(self):
    return not self.localname.startswith('_') and bool(self.parent.boost_python_export)

NamespaceProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return not self.localname.startswith('_') and self.is_complete and bool(self.parent.boost_python_export)

ClassProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return not self.localname.startswith('_') and self.parent.boost_python_export

ClassTemplateProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return (self.specialize is None or bool(self.specialize.boost_python_export)) and bool(self.parent.boost_python_export)

ClassTemplateSpecializationProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    if self.parent.boost_python_export:
        desugared_type = self.qualified_type.desugared_type
        if desugared_type.is_pointer or desugared_type.is_reference:
            return False
        else:
            if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
                if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                    return False
            return desugared_type.is_fundamental_type or bool(desugared_type.unqualified_type.boost_python_export)
    else:
        return False

VariableProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _valid_boost_python_export(self):
    return getattr(self, 'access', False) in ['none', 'public'] and not self.is_bit_field

FieldProxy._valid_boost_python_export = property(_valid_boost_python_export)

def _default_boost_python_export(self):
    if self.parent.boost_python_export:
        qualified_type = self.qualified_type
        return not qualified_type.is_reference and not qualified_type.is_pointer and (bool(qualified_type.unqualified_type.boost_python_export) or qualified_type.is_fundamental_type)
    else:
        return False

TypedefProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return bool(self.parent.boost_python_export)

FunctionProxy._default_boost_python_export = property(_default_boost_python_export)

def _valid_boost_python_export(self):
    if self.boost_python_call_policy == 'boost::python::return_value_policy< boost::python::reference_existing_object >()':
        if not isinstance(self.return_type.desugared_type.unqualified_type, ClassProxy):
            return False
    if self.return_type.boost_python_export and all(parameter.boost_python_export for parameter in self.parameters):
        return not self.localname.startswith('operator') or isinstance(self.parent, ClassProxy)
    else:
        return False

FunctionProxy._valid_boost_python_export = property(_valid_boost_python_export)
del _valid_boost_python_export

ConstructorProxy._default_boost_python_export = property(_default_boost_python_export)

def _valid_boost_python_export(self):
    return self.access == 'public' and all(parameter.boost_python_export for parameter in self.parameters)

ConstructorProxy._valid_boost_python_export = property(_valid_boost_python_export)
del _default_boost_python_export, _valid_boost_python_export

def _default_boost_python_export(self):
    if self.is_virtual:
        try:
            return self.overrides is None
        except:
            return self.is_pure
    else:
        return bool(self.parent.boost_python_export)

MethodProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _valid_boost_python_export(self):
    if self.boost_python_call_policy in ['boost::python::return_internal_reference<>()',
                                          'boost::python::return_value_policy< boost::python::reference_existing_object >()']:
        if not isinstance(self.return_type.desugared_type.unqualified_type, ClassProxy):
            return False
    if self.access == 'public' and self.return_type.boost_python_export and all(bool(parameter.boost_python_export) for parameter in self.parameters):
        return not self.localname.startswith('operator') or self.localname.strip('operator').strip() in PYTHON_OPERATOR
    else:
        return False

MethodProxy._valid_boost_python_export = property(_valid_boost_python_export)
del _valid_boost_python_export

class BoostPythonExportFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return len(self._declarations) == 0

    def __init__(self, asg, node):
        super(BoostPythonExportFileProxy, self).__init__(asg, node)
        if not hasattr(self, '_declarations'):
            self._asg._nodes[self._node]['_declarations'] = set()

    @property
    def declarations(self):
        declarations = [self._asg[declaration] for declaration in self._declarations]
        return [declaration for declaration in declarations if not isinstance(declaration, ClassProxy)] + \
               sorted([declaration for declaration in declarations if isinstance(declaration, ClassProxy)],
                       key = lambda cls: cls.depth)

    @property
    def depth(self):
        if not hasattr(self, '_depth'):
            return 0
        else:
            return self._depth

    @depth.setter
    def depth(self, depth):
        self._asg._nodes[self._node]['_depth'] = depth

    @depth.deleter
    def del_depth(self):
        self._asg._nodes[self._node].pop('_depth')

    @property
    def module(self):
        if hasattr(self, '_module'):
            return self._asg[self._module]

    @module.setter
    def module(self, module):
        del self.module
        if isinstance(module, BoostPythonModuleFileProxy):
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

    def edit(self, line):
        pass

class BoostPythonExportDefaultFileProxy(BoostPythonExportFileProxy):

    language = 'c++'

    SCOPE = Template(text=r"""\
% for scope in scopes:

    std::string name_${scope.hash} = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${node_rename(scope, scope=True)}");
    boost::python::object module_${scope.hash}(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(name_${scope.hash}.c_str()))));
    boost::python::scope().attr("${node_rename(scope, scope=True)}") = module_${scope.hash};
    boost::python::scope scope_${scope.hash} = module_${scope.hash};\
% endfor""")

    ENUMERATOR = Template(text="""\
    boost::python::scope().attr("${node_rename(enumerator)}") = (int)(${enumerator.globalname});\
""")

    ENUMERATION = Template(text=r"""\
    boost::python::enum_< ${enumeration.globalname} > enum_${enumeration.hash}("${node_rename(enumeration)}");
    % if enumeration.is_scoped:
        % for enumerator in enumeration.enumerators:
            % if enumerator.boost_python_export:
    enum_${enumeration.hash}.value("${node_rename(enumerator)}", ${enumerator.globalname});
            % endif
        % endfor
    % else:
        % for enumerator in enumeration.enumerators:
            % if enumerator.boost_python_export:
    enum_${enumeration.hash}.value("${node_rename(enumerator)}", ${enumerator.globalname[::-1].replace((enumeration.localname + '::')[::-1], '', 1)[::-1]});
            % endif
        % endfor
    % endif""")

    VARIABLE = Template(text="""\
    boost::python::scope().attr("${node_rename(variable)}") = ${variable.globalname};\
""")

    FUNCTION = Template(text=r"""\
    % if function.is_overloaded:
    ${function.return_type.globalname} (*function_pointer_${function.hash})\
(${", ".join(parameter.qualified_type.globalname for parameter in function.parameters)}) = ${function.globalname};
    % endif
    boost::python::def("${node_rename(function)}", \
    % if function.is_overloaded:
function_pointer_${function.hash}\
    % else:
${function.globalname}\
    % endif
    % if function.boost_python_call_policy:
, ${function.boost_python_call_policy}\
    % endif
, "${documenter(function)}");""")

    ERROR = Template(text=r"""\
namespace autowig
{
    PyObject* error_${error.hash} = NULL;

    void translate_${error.hash}(${error.globalname} const & error) { PyErr_SetString(error_${error.hash}, error.what()); };
}""")

    DECORATOR = Template(text=r"""\
% if not cls.is_error:

namespace autowig
{
    % if cls.is_abstract:
    class Wrap_${cls.hash} : public ${cls.globalname.replace('struct ', '', 1).replace('class ', '', 1)}, public boost::python::wrapper< ${cls.globalname} >
    {
        % for access in ['public', 'protected', 'private']:
        ${access}:
            <% prototypes = set() %>
            % for mtd in cls.methods(access=access, inherited=True):
                % if mtd.access == access:
                    %if mtd.prototype not in prototypes and mtd.is_virtual and mtd.is_pure:
            virtual ${mtd.return_type.globalname} ${mtd.localname}(${', '.join(parameter.qualified_type.globalname + ' param_' + str(parameter.index) for parameter in mtd.parameters)}) \
                        % if mtd.is_const:
const
                        % else:

                        % endif
                        % if mtd.return_type.desugared_type.globalname.startswith('class ::std::unique_ptr'):
            {
                 ${mtd.return_type.globalname.replace("class ", "", 1)}::element_type* result = this->get_override("${mtd.localname}")(${", ".join('param_' + str(parameter.index) for parameter in mtd.parameters)});
                 return ${mtd.return_type.globalname.replace('class ', '', 1)}(result);
            }
                        % elif mtd.return_type.is_reference:
            {
                 ${mtd.return_type.unqualified_type.globalname.replace("class ", "", 1).replace("struct ", "", 1)}* result = this->get_override("${mtd.localname}")(${", ".join('param_' + str(parameter.index) for parameter in mtd.parameters)});
                 return *result;
            }                 
                        % else:
            { \
                            % if not mtd.return_type.desugared_type.globalname.strip() == 'void':
return \
                            % endif
this->get_override("${mtd.localname}")(${", ".join('param_' + str(parameter.index) for parameter in mtd.parameters)}); }
                        % endif
                        
                    % endif
<% prototypes.add(mtd.prototype) %>\
                % endif
            % endfor

        % endfor
    };
    % endif

    % for method in cls.methods(access='public'):
        % if method.boost_python_export and method.return_type.desugared_type.is_reference and not method.return_type.desugared_type.is_const and method.return_type.desugared_type.unqualified_type.is_assignable:
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
}

#if defined(_MSC_VER)
    #if (_MSC_VER == 1900)
namespace boost
{
    % if cls.is_abstract:
    template <> autowig::Wrap_${cls.hash} const volatile * get_pointer<autowig::Wrap_${cls.hash} const volatile >(autowig::Wrap_${cls.hash} const volatile *c) { return c; }
    % endif
    template <> ${cls.globalname} const volatile * get_pointer<${cls.globalname} const volatile >(${cls.globalname} const volatile *c) { return c; }
}
    #endif
#endif

%endif""")

    CLASS = Template(text=r"""\
<%
def wrapper_name(cls):
    if cls.is_abstract:
        return 'autowig::' + 'Wrap_' + cls.hash
    else:
        return cls.globalname
%>\
% if not cls.is_error:
    % for method in cls.methods(access='public'):
        % if method.boost_python_export and method.is_overloaded:
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
    % if any(function.boost_python_export for function in cls.functions()):
    struct function_group
    {
        % for function in cls.functions():
            % if function.boost_python_export:
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
    boost::python::class_< ${wrapper_name(cls)}, autowig::Held< ${wrapper_name(cls)} >::Type\
    % if any(base for base in cls.bases(access='public') if base.boost_python_export):
, boost::python::bases< ${", ".join(base.globalname for base in cls.bases(access='public') if base.boost_python_export)} >\
    % endif
    % if not cls.is_copyable or cls.is_abstract:
, boost::noncopyable\
    % endif
 > class_${cls.hash}("${node_rename(cls)}", "${documenter(cls)}", boost::python::no_init);
    % if not cls.is_abstract and cls.is_instantiable:
        % for constructor in cls.constructors(access = 'public'):
            % if constructor.boost_python_export:
    class_${cls.hash}.def(\
boost::python::init< ${", ".join(parameter.qualified_type.globalname for parameter in constructor.parameters)} >("${documenter(constructor)}"));
            % endif
        % endfor
    % endif
    % for method in cls.methods(access = 'public'):
        % if method.boost_python_export:
    class_${cls.hash}.def("${node_rename(method)}", \
                % if method.is_virtual and method.is_pure:
boost::python::pure_virtual(\
                % endif
                % if method.is_overloaded:
method_pointer_${method.hash}\
                % else:
&${method.globalname}
                % endif
                % if method.is_virtual and method.is_pure:
)\
                % endif
, \
                % if method.boost_python_call_policy:
${method.boost_python_call_policy}, \
                % endif
"${documenter(method)}");
                % if method.return_type.desugared_type.is_reference and not method.return_type.desugared_type.is_const and method.return_type.desugared_type.unqualified_type.is_assignable:
    class_${cls.hash}.def("${node_rename(method)}", autowig::method_decorator_${method.hash});
                % endif
        % endif
    % endfor
    % for methodname in {node_rename(method) for method in cls.methods() if method.access == 'public' and method.is_static and method.boost_python_export}:
    class_${cls.hash}.staticmethod("${methodname}");
    % endfor
    % for function in cls.functions():
        % if function.boost_python_export:
    class_${cls.hash}.def("${node_rename(function)}", function_group::function_${function.hash}, \
                % if function.boost_python_call_policy:
${function.boost_python_call_policy}, \
                % endif
"${documenter(function)}");
        % endif
    % endfor
    % for field in cls.fields(access = 'public'):
        % if field.boost_python_export:
            % if field.qualified_type.is_const:
    class_${cls.hash}.def_readonly\
            % else:
    class_${cls.hash}.def_readwrite\
            % endif
("${node_rename(field)}", \
            % if not field.is_static:
&\
            % endif
${field.globalname}, "${documenter(field)}");
        % endif
    % endfor
    %if any(base for base in cls.bases(access='public') if base.boost_python_export):

    if(autowig::Held< ${cls.globalname} >::is_class)
    {
        % if cls.is_abstract:
        boost::python::implicitly_convertible< autowig::Held< ${wrapper_name(cls)} >::Type, autowig::Held< ${cls.globalname} >::Type >();
        boost::python::register_ptr_to_python< autowig::Held< ${cls.globalname} >::Type >();
        % endif
        % for bse in cls.bases(access='public'):
            % if bse.boost_python_export:
        boost::python::implicitly_convertible< autowig::Held< ${cls.globalname} >::Type, autowig::Held< ${bse.globalname} >::Type >();
            % endif
        % endfor
    }
    % elif cls.is_abstract:
    if(autowig::Held< ${cls.globalname} >::is_class)
    {
        % if cls.is_abstract:
        boost::python::implicitly_convertible< autowig::Held< ${wrapper_name(cls)} >::Type, autowig::Held< ${cls.globalname} >::Type >();
        boost::python::register_ptr_to_python< autowig::Held< ${cls.globalname} >::Type >();
        % endif
    }    
    % endif
% else:
    std::string name_${cls.hash} = boost::python::extract< std::string >(boost::python::scope().attr("__name__"));
    name_${cls.hash} = name_${cls.hash} + "." + "${node_rename(cls)}";
    autowig::error_${cls.hash} = PyErr_NewException(strdup(name_${cls.hash}.c_str()), PyExc_RuntimeError, NULL);
    boost::python::scope().attr("${node_rename(cls)}") = boost::python::object(boost::python::handle<>(boost::python::borrowed(autowig::error_${cls.hash})));
    boost::python::register_exception_translator< ${cls.globalname} >(&autowig::translate_${cls.hash});
% endif""")


    TO = {
            "class ::std::unique_ptr" : Template(r"""\
    struct unique_ptr_${cls.hash}_to_python
    {
        static PyObject* convert(${cls.globalname} const & unique_ptr_${cls.hash})
        {
            //return boost::python::incref(boost::python::object(const_cast< ${cls.globalname} & >(unique_ptr_${cls.hash}).release()).ptr());
            std::shared_ptr< ${cls.templates[0].globalname} > shared_ptr_${cls.hash}(std::move(const_cast< ${cls.globalname} & >(unique_ptr_${cls.hash})));
            return boost::python::incref(boost::python::object(shared_ptr_${cls.hash}).ptr());
        }
    };

    boost::python::to_python_converter< ${cls.globalname}, unique_ptr_${cls.hash}_to_python >();""") }

    FROM = {
            "class ::std::vector" : Template(r"""\
    struct vector_${cls.hash}_from_python
    {
        vector_${cls.hash}_from_python()
        {
            boost::python::converter::registry::push_back(
                &convertible,
                &construct,
                boost::python::type_id< ${cls.globalname} >());
        }

        static void* convertible(PyObject* obj_ptr)
        { return obj_ptr; }

        static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
        {
            boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
            void* storage = ((boost::python::converter::rvalue_from_python_storage< ${cls.globalname} >*)data)->storage.bytes;
            new (storage) ${cls.globalname}();
            data->convertible = storage;
            ${cls.globalname}& result = *((${cls.globalname}*)storage);
            unsigned int i = 0;
            for(;; i++)
            {
                boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
                if(PyErr_Occurred())
                { boost::python::throw_error_already_set(); }
                if(!py_elem_hdl.get())
                { break; }
                boost::python::object py_elem_obj(py_elem_hdl);
                result.push_back(boost::python::extract< ${cls.templates[0].globalname} >(py_elem_obj));
            }
        }
    };

    vector_${cls.hash}_from_python();"""),

            "class ::std::set" : Template(r"""\
    struct set_${cls.hash}_from_python
    {
        set_${cls.hash}_from_python()
        {
            boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id< ${cls.globalname} >());
        }

        static void* convertible(PyObject* obj_ptr)
        { return obj_ptr; }

        static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
        {
            boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
            void* storage = ((boost::python::converter::rvalue_from_python_storage< ${cls.globalname} >*)data)->storage.bytes;
            new (storage) ${cls.globalname}();
            data->convertible = storage;
            ${cls.globalname}& result = *((${cls.globalname}*)storage);
            unsigned int i = 0;
            for(;; i++)
            {
                boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
                if(PyErr_Occurred())
                { boost::python::throw_error_already_set(); }
                if(!py_elem_hdl.get())
                { break; }
                boost::python::object py_elem_obj(py_elem_hdl);
                result.insert((${cls.templates[0].globalname})(boost::python::extract< ${cls.templates[0].globalname} >(py_elem_obj)));
            }
        }

    };

    set_${cls.hash}_from_python();""")}

    IGNORE =   {"class ::std::shared_ptr",
                "class ::std::unique_ptr",
                "class ::boost::python::numeric::array",
                "struct ::boost::python::api::attribute_policies",
                "struct ::boost::python::converter::detail::arg_to_python_base",
                "class ::boost::python::detail::call_proxy",
                "struct ::boost::python::objects::py_function",
                "::boost::python::converter::detail::unwind_type_id_helper::result_type",
                "class ::boost::python::override",
                "::boost::python::api::const_attribute_policies::key_type",
                "::boost::python::detail::yes_convertible",
                "struct ::boost::python::type_info",
                "::boost::python::type_handle",
                "struct ::boost::python::detail::decref_guard",
                "struct ::boost::python::detail::keyword",
                "struct ::boost::python::api::slice_policies",
                "::boost::python::str::base",
                "struct ::boost::python::objects::function",
                "struct ::boost::python::detail::exception_handler",
                "class ::boost::python::detail::args_proxy",
                "struct ::boost::python::pickle_suite",
                "struct ::boost::python::objects::py_function_impl_base",
                "struct ::boost::python::detail::long_base",
                "struct ::boost::python::api::object_base",
                "::boost::python::objects::class_id",
                "struct ::boost::python::converter::shared_ptr_deleter",
                "struct ::boost::python::api::const_slice_policies",
                "struct ::boost::python::converter::arg_lvalue_from_python_base",
                "struct ::boost::python::converter::rvalue_from_python_chain",
                "struct ::boost::python::detail::py_func_sig_info",
                "struct ::boost::python::detail::pickle_suite_registration",
                "struct ::boost::python::objects::class_base",
                "::boost::python::type_info::base_id_t",
                "struct ::boost::python::api::const_item_policies",
                "class ::boost::python::scope",
                "::boost::python::slice::base",
                "struct ::boost::python::detail::dict_base",
                "::boost::python::default_call_policies::argument_package",
                "struct ::boost::python::converter::registration",
                "::boost::python::detail::void_result_to_python",
                "class ::boost::python::docstring_options",
                "class ::boost::python::str",
                "class ::boost::python::detail::method_result",
                "class ::boost::python::api::slice_nil",
                "::boost::python::api::const_objattribute_policies::key_type",
                "::boost::python::objects::default_iterator_call_policies",
                "struct ::boost::python::instance_holder",
                "class ::boost::python::tuple",
                "enum ::boost::python::detail::operator_id",
                "struct ::boost::python::detail::overloads_base",
                "struct ::boost::python::error_already_set",
                "struct ::boost::python::api::const_attribute_policies",
                "struct ::boost::python::detail::list_base",
                "::boost::python::ssize_t",
                "class ::boost::python::dict",
                "class ::boost::python::api::object",
                "struct ::boost::python::converter::rvalue_from_python_stage1_data",
                "class ::boost::python::detail::slice_base",
                "struct ::boost::python::api::objattribute_policies",
                "struct ::boost::python::objects::enum_base",
                "struct ::boost::python::numeric::aux::array_object_manager_traits",
                "::boost::python::long_::base",
                "class ::boost::python::detail::kwds_proxy",
                "struct ::boost::python::converter::lvalue_from_python_chain",
                "struct ::boost::python::detail::builtin_to_python",
                "::boost::python::detail::no_convertible",
                "class ::boost::python::list",
                "::boost::python::numeric::array::base",
                "struct ::boost::python::api::const_objattribute_policies",
                "struct ::boost::python::detail::signature_element",
                "class ::boost::python::long_",
                "struct ::boost::python::objects::stl_input_iterator_impl",
                "::boost::python::api::const_item_policies::key_type",
                "class ::boost::python::slice",
                "::boost::python::tuple::base",
                "struct ::boost::python::numeric::aux::array_base",
                "enum ::boost::python::no_init_t",
                "struct ::boost::python::default_call_policies",
                "::boost::python::dict::base",
                "struct ::boost::python::detail::write_type_id",
                "enum ::boost::python::tag_t",
                "::boost::python::list::base",
                "struct ::boost::python::converter::detail::unwind_type_id_helper",
                "class ::boost::python::detail::wrapper_base",
                "struct ::boost::python::api::item_policies",
                "struct ::boost::python::detail::str_base",
                "struct ::boost::python::detail::void_return",
                "struct ::boost::python::detail::tuple_base"}

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
                    if isinstance(target, ClassProxy):
                        depth = max(target.depth+1, depth)
            return depth

    @property
    def scope(self):
        if len(self._declarations) > 0:
            declaration = self.declarations[0]
            if isinstance(declaration, (ClassProxy, EnumerationProxy, NamespaceProxy)):
                return declaration
            else:
                return declaration.parent

    @property
    def scopes(self):
        if len(self._declarations) > 0:
            return self.declarations[0].ancestors[1:]
        else:
            return []
           
    @property         
    def _content(self):
        content = '#include "' + self.header.localname + '"\n'
        for arg in self.declarations:
            if isinstance(arg, ClassProxy) and arg.is_error:
                content += '\n\n' + self.ERROR.render(error = arg)
            # if arg.is_abstract:
            #     content += '\n\n' + self.ABSTRACT_CLASS.render(cls = arg)
        for arg in self.declarations:
            if isinstance(arg, ClassProxy):
                if arg.globalname not in self.IGNORE:
                    content += '\n\n' + self.DECORATOR.render(cls = arg)
        content += '\n\nvoid ' + self.prefix + '()\n{\n' + self.SCOPE.render(scopes = self.scopes, node_rename = node_rename, documenter = documenter)
        for arg in self.declarations:
            if isinstance(arg, EnumeratorProxy):
                content += '\n' + self.ENUMERATOR.render(enumerator = arg,
                        node_rename = node_rename,
                        documenter = documenter)
            elif isinstance(arg, EnumerationProxy):
                if arg.globalname not in self.IGNORE:
                    content += '\n' + self.ENUMERATION.render(enumeration = arg,
                                            node_rename = node_rename,
                                            documenter = documenter)
            elif isinstance(arg, VariableProxy):
                content += '\n' + self.VARIABLE.render(variable = arg,
                        node_rename = node_rename,
                        documenter = documenter)
            elif isinstance(arg, FunctionProxy):
                content += '\n' + self.FUNCTION.render(function = arg,
                        node_rename = node_rename,
                        documenter = documenter)
            elif isinstance(arg, ClassTemplateSpecializationProxy):
                if arg.globalname not in self.IGNORE and arg.specialize.globalname not in self.IGNORE:
                    content += '\n' + self.CLASS.render(cls = arg,
                            node_rename = node_rename,
                            documenter = documenter)
                if arg.specialize.globalname in self.TO:
                    content += '\n' + self.TO[arg.specialize.globalname].render(cls = arg)
                elif arg.globalname in self.TO:
                    content += '\n' + self.TO[arg.globalname].render(cls = arg)
                if arg.specialize.globalname in self.FROM:
                    content += '\n' + self.FROM[arg.specialize.globalname].render(cls = arg)
                elif arg.globalname in self.FROM:
                    content += '\n' + self.FROM[arg.globalname].render(cls = arg)
            elif isinstance(arg, ClassProxy):
                if arg.globalname not in self.IGNORE:
                    content += '\n' + self.CLASS.render(cls = arg,
                            node_rename = node_rename,
                            documenter = documenter)
                if arg.globalname in self.TO:
                    content += '\n' + self.TO[arg.globalname].render(cls = arg)
                if arg.globalname in self.FROM:
                    content += '\n' + self.FROM[arg.globalname].render(cls = arg)
            elif isinstance(arg, TypedefProxy):
                continue
            else:
                raise NotImplementedError(arg.__class__.__name__)
        content += '\n}'
        return content

    def edit(self, row):
        if row <= 0:
            raise ValueError()
        if not self.on_disk:
            raise ValueError()
        with open(self.globalname, 'r') as filehandler:
            lines = filehandler.readlines()
            if not row == len(lines):
                row = row - 1
                line = lines[row]
                parsed = parse.parse('    boost::python::class_< {globalname}, autowig::Held{suffix}', line)
                if parsed:
                    return "if asg['" + parsed["globalname"] + "'].is_copyable:\n\tasg['" + parsed["globalname"] + "'].is_copyable = False\nelse:\n\tasg['" + parsed["globalname"] + "'].boost_python_export = False\n\t\n\tif '" + self.globalname + "' in asg:\n\t\tasg['" + self.globalname + "'].remove()\n"
                else:
                    while row > 0 and parsed is None:
                        row = row - 1
                        parsed = parse.parse('    boost::python::class_< {globalname}, autowig::Held{suffix}', lines[row])
                    row = row + 1
                    while row < len(lines) and parsed is None:
                        parsed = parse.parse('    boost::python::class_< {globalname}, autowig::Held{suffix}', lines[row])
                        row = row + 1
                    if parsed:
                        node = self._asg[parsed["globalname"]]
                        parsed = parse.parse('    class_{hash}.def(boost::python::init< {parameters} >({documentation}));', line)
                        if not parsed:
                            parsed = parse.parse('    class_{hash}.def(boost::python::init<  >({documentation}));', line)
                        if parsed:
                            return "for constructor in asg['" + node.globalname + "'].constructors(access='public'):\n\tif constructor.prototype == '" + node.localname + "(" + parsed.named.get("parameters","") + ")" + "':\n\t\tconstructor.boost_python_export = False\n\t\tbreak\n"
                        else:
                            parsed = parse.parse('    class_{hash}.def{what}({python}, {cpp}, {documentation});', line)
                            if not parsed:
                                parsed = parse.parse('    class_{hash}.def({python}, {cpp}, {documentation});', line)
                            if parsed:
                                if 'what' not in parsed.named:
                                    if parsed['cpp'].startswith('method_pointer_'):
                                        pointer = parsed['cpp']
                                        parsed = None
                                        while row > 0 and parsed is None:
                                            row = row - 1
                                            parsed = parse.parse('    {return_type} (::{scope}::*'+ pointer + ')({parameters}){cv}= {globalname};', lines[row])
                                            if not parsed:
                                                parsed = parse.parse('    {return_type} (::{scope}::*'+ pointer + ')(){cv}= {globalname};', lines[row])
                                        if parsed:
                                            localname = parsed["globalname"].split('::')[-1]
                                            return "for method in asg['" + node.globalname + "'].methods(access='public'):\n\tif method.prototype == '" + parsed["return_type"].lstrip() + " " + localname + "(" + parsed.named.get("parameters","") + ")" + parsed["cv"].rstrip() + "':\n\t\tmethod.boost_python_export = False\n\t\tbreak\n"
                                        else:
                                            row = row + 1
                                            while row < len(lines) and parsed is None:
                                                parsed = parse.parse('    {return_type} (*'+ pointer + ')({parameters}){cv}= {globalname};', lines[row])
                                                if not parsed:
                                                    parsed = parse.parse('    {return_type} (*'+ pointer + ')(){cv}= {globalname};', lines[row])
                                                row = row + 1
                                            if parsed:
                                                localname = parsed["globalname"].split('::')[-1]
                                                return "for method in asg['" + node.globalname + "'].methods(access='public'):\n\tif method.prototype == 'static " + parsed["return_type"].lstrip() + " " + localname + "(" + parsed.named.get("parameters","") + ")" + parsed["cv"].rstrip() + "':\n\t\tmethod.boost_python_export = False\n\t\tbreak\n"
                                            else:
                                                return ""
                                    elif parsed['cpp'].startswith('function_pointer_'):
                                        return ""
                                    else:
                                        localname = parsed["cpp"].split('::')[-1]
                                        return "for method in asg['" + node.globalname + "'].methods(access='public'):\n\tif method.localname == '" + localname + "':\n\t\tmethod.boost_python_export = False\n\t\tbreak\n"
                                else:
                                    return "asg['" + parsed['cpp'].lstrip('&') + "'].boost_python_export = False"
                            else:
                                parsed = parse.parse('    {return_type} ({pointer})({parameters}){cv}= {globalname};', line)
                                if not parsed:
                                    parsed = parse.parse('    {return_type} ({pointer})(){cv}= {globalname};', line)
                                if parsed:
                                    localname = parsed["globalname"].split('::')[-1]
                                    return "for method in asg['" + node.globalname + "'].methods(access='public') + asg['" + node.globalname + "'].functions():\n\tif method.prototype == '" + parsed["return_type"].lstrip() + " " + localname + "(" + parsed.named.get("parameters","") + ")" + parsed["cv"].rstrip() + "':\n\t\tmethod.boost_python_export = False\n\t\tbreak\n"
                                else:
                                    return ""

                    else:
                        return ""
            else:
                return ('\n'.join("asg['" + declaration.globalname + "'].boost_python_export = False" for declaration in self.declarations if isinstance(declaration, ClassProxy))
                        + "\nif '" + self.globalname + "' in asg:\n\tasg['" + self.globalname + "'].remove()\n")
        return ""


def boost_python_exports(self, *args, **kwargs):
    return [export for export in self.files(*args, **kwargs) if isinstance(export, BoostPythonExportFileProxy)]

AbstractSemanticGraph.boost_python_exports = boost_python_exports
del boost_python_exports

boost_python_export = ProxyManager('autowig.boost_python_export', brief="",
        details="")

class BoostPythonHeaderFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return self.module._clean_default

    CONTENT = Template(text=r"""\
#ifndef ${header_guard}
#define ${header_guard}

#include <boost/python.hpp>
#include <type_traits>\
% for header in headers:

    % if header.language == 'c':
extern "C" {
    % endif
#include <${header.searchpath}>\
    % if header.language == 'c':

}\
    % endif
% endfor

% if held_header:
#include <${held_header}>
% endif

namespace autowig
{
     template<class T> struct Held {
        typedef ${held_type} Type;
        static bool const is_class = \
        % if held_header:
true;
        % else:
false;
        % endif
    };
}

""")

    HELDTYPE = {'raw'               : "T*",
                'std::shared_ptr'   : "std::shared_ptr< T >",
                'std::unique_ptr'   : "std::unique_ptr< T >",
                'boost::shared_ptr' : "boost::shared_ptr< T >"}

    HELDHEADER = {'raw'               : None,
                  'std::shared_ptr'   : 'memory',
                  'std::unique_ptr'   : 'memory',
                  'boost::shared_ptr' : 'boost/shared_ptr'}

    @property
    def module(self):
        return self._asg[self.globalname.rstrip(self.suffix) + self._module]

    def get_content(self):
        content = self.CONTENT.render(headers = [header for header in self._asg.files(header=True) if not header.is_external_dependency and header.is_self_contained],
                                      held_type = self.HELDTYPE[self.helder],
                                      held_header = self.HELDHEADER[self.helder],
                                      header_guard = self.guard)
        return content + "#endif"

    @property
    def helder(self):
        if not hasattr(self, '_helder'):
            return 'raw'
        else:
            return self._helder

    @helder.setter
    def helder(self, helder):
        if helder not in self.HELDTYPE or helder not in self.HELDHEADER:
            raise ValueError('`helder` parameter')
        self._asg._nodes[self._node]['_helder'] = helder
   
    @helder.deleter
    def helder(self):
        self._asg._nodes[self._node].pop('_helder', 'raw')

    @property
    def guard(self):
        if not hasattr(self, '_guard'):
            return 'AUTOWIG_' + self.prefix.upper()
        else:
            return self._guard

    @guard.setter
    def guard(self, guard):
        self._asg._nodes[self._node]['_guard'] = guard
   
    @guard.deleter
    def guard(self):
        self._asg._nodes[self._node].pop('_guard', '')
      
BoostPythonHeaderFileProxy.content = property(BoostPythonHeaderFileProxy.get_content)

class BoostPythonModuleFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return len(self._exports) == 0

    CONTENT = Template(text=r"""\
#include "${module.header.localname}"

% for export in module.exports:
    % if not export.is_empty:
void ${export.prefix}();
    % endif
% endfor

boost::python::docstring_options docstring_options(${int(module.docstring_user_defined)}, ${int(module.docstring_py_signatures)}, ${int(module.docstring_cpp_signatures)});

BOOST_PYTHON_MODULE(_${module.prefix})
{
% for export in module.exports:
    % if not export.is_empty:
    ${export.prefix}();
    %endif
% endfor
}""")

    def __init__(self, asg, node):
        super(BoostPythonModuleFileProxy, self).__init__(asg, node)
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
        temp = [declaration for export in self.exports for declaration in export.declarations]
        while len(temp) > 0:
            declaration = temp.pop()
            if isinstance(declaration, FunctionProxy):
                export = declaration.return_type.desugared_type.unqualified_type.boost_python_export
                if export and export is not True:
                    module = export.module
                    if module is not None:
                        modules.add(module.globalname)
                for prm in declaration.parameters:
                    export = prm.qualified_type.desugared_type.unqualified_type.boost_python_export
                    if export and export is not True:
                        module = export.module
                        if module is not None:
                            modules.add(module.globalname)
            elif isinstance(declaration, (VariableProxy, TypedefProxy)):
                export = declaration.qualified_type.desugared_type.unqualified_type.boost_python_export
                if export and export is not True:
                    module = export.module
                    if module is not None:
                        modules.add(module.globalname)
            elif isinstance(declaration, ClassProxy):
                export = declaration.boost_python_export
                if export and export is not True:
                    module = export.module
                    if module is not None:
                        modules.add(module.globalname)
                temp.extend([bse for bse in declaration.bases() if bse.access == 'public'])
                temp.extend([dcl for dcl in declaration.declarations() if dcl.access == 'public'])
            elif isinstance(declaration, ClassTemplateProxy):
                export = declaration.boost_python_export
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
        return self.CONTENT.render(module = self)

    @property
    def decorator(self):
        if '_decorator' in self._asg._nodes[self._node]:
            return self._asg[self._decorator]

    @decorator.setter
    def decorator(self, decorator):
        if isinstance(decorator, basestring):
            decorator = self._asg[decorator]
        if not isinstance(decorator, BoostPythonDecoratorFileProxy):
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

    def write(self, header=True, exports=True, decorator=True):
        super(BoostPythonModuleFileProxy, self).write()
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
        super(BoostPythonModuleFileProxy, self).remove()
        if header:
            self.header.remove()
        if exports:
            for export in self.exports:
                export.remove()
        if decorator:
            self.decorator.remove()

BoostPythonModuleFileProxy.dependencies = property(BoostPythonModuleFileProxy.get_dependencies)

BoostPythonModuleFileProxy._content = property(BoostPythonModuleFileProxy.get_content)

def boost_python_modules(self, **kwargs):
    return [module for module in self.files(**kwargs) if isinstance(module, BoostPythonModuleFileProxy)]

AbstractSemanticGraph.boost_python_modules = boost_python_modules
del boost_python_modules

boost_python_module = ProxyManager('autowig.boost_python_module', brief="",
        details="")

class BoostPythonDecoratorFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return not hasattr(self, '_module')

    @property
    def module(self):
        if hasattr(self, '_module'):
            return self._asg[self._module]

    @module.setter
    def module(self, module):
        if isinstance(module, basestring):
            module = self._asg[module]
        if not isinstance(module, BoostPythonModuleFileProxy):
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
        while parent is not None and os.path.exists(parent.globalname + '__init__.py'):
            modules.append(parent.localname.strip(os.sep))
            parent = parent.parent
        return '.'.join(reversed(modules))

class BoostPythonDecoratorDefaultFileProxy(BoostPythonDecoratorFileProxy):

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
<% target = tdf.qualified_type.desugared_type.unqualified_type.boost_python_export.module.decorator %>\
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
    % endfor
% endif""")

    def get_content(self):

        IGNORE = self.module.exports[0].IGNORE

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
            for declaration in export.declarations:
                if isinstance(declaration.parent, ClassProxy) and not ignore(declaration):
                    scopes.append(declaration)
        content.append(self.SCOPES.render(scopes = sorted(scopes, key = lambda scope: len(scope.ancestors)), decorator = self, module = self.module,
                node_rename = node_rename))
        templates = dict()
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration, ClassTemplateSpecializationProxy) and not ignore(declaration):
                    spc = declaration.specialize.globalname
                    if spc in templates:
                        templates[spc].append(declaration)
                    else:
                        templates[spc] = [declaration]
        content.append(self.TEMPLATES.render(decorator = self, module = self.module, templates = [(self._asg[tpl], spcs) for tpl, spcs in templates.iteritems()],
                node_rename = node_rename))
        typedefs = []
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration, TypedefProxy) and declaration.qualified_type.desugared_type.unqualified_type.boost_python_export and declaration.qualified_type.desugared_type.unqualified_type.boost_python_export is not True and not ignore(declaration):
                    typedefs.append(declaration)
                elif isinstance(declaration, ClassProxy) and not ignore(declaration):
                    typedefs.extend([tdf for tdf in declaration.typedefs() if tdf.boost_python_export and tdf.qualified_type.desugared_type.unqualified_type.boost_python_export and tdf.qualified_type.desugared_type.unqualified_type.boost_python_export is not True])
        content.append(self.TYPEDEFS.render(decorator = self, module = self.module, typedefs = typedefs, node_rename=node_rename))
        return "\n".join(content)


BoostPythonDecoratorDefaultFileProxy._content = property(BoostPythonDecoratorDefaultFileProxy.get_content)

boost_python_decorator = ProxyManager('autowig.boost_python_decorator', brief="",
        details="")

def boost_python_generator(asg, nodes, module='./module.cpp', decorator=None, **kwargs):
    """
    """

    if module in asg:
        module = asg[module]
    else:
        module = asg.add_file(module, proxy=boost_python_module())
        asg.add_file(module.globalname[:-len(module.suffix)] + '.' + 'h',
                     _module = module.suffix,
                     proxy= BoostPythonHeaderFileProxy)

    directory = module.parent
    suffix = module.suffix
    prefix = kwargs.pop('prefix', 'wrapper_')

    if kwargs.pop('closure', True):
        plugin = visitor.plugin
        visitor.plugin = 'boost_python_closure'
        nodes += asg.dependencies(*nodes)
        visitor.plugin = plugin

    exports = set()
    for node in nodes:
        if node.boost_python_export is True:
            if isinstance(node, EnumeratorProxy) and isinstance(node.parent, (EnumerationProxy, ClassProxy)) or isinstance(node, TypedefProxy) and isinstance(node.parent, ClassProxy) or isinstance(node, (FieldProxy, MethodProxy, ConstructorProxy, DestructorProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy)) or isinstance(node, FunctionProxy) and isinstance(node.parent, ClassProxy):
                continue
            elif not isinstance(node, NamespaceProxy) and not any(isinstance(ancestor, ClassTemplateProxy) for ancestor in reversed(node.ancestors)):
                export = directory.globalname + node_path(node, prefix=prefix, suffix=suffix).strip('./')
                if export in asg:
                    export = asg[export]
                else:
                    export = asg.add_file(export, proxy=boost_python_export())
                node.boost_python_export = export
                exports.add(export._node)

    exports = [asg[export] for export in exports]
    for export in exports:
        export.module = module

    if decorator:
        if decorator in asg:
            decorator = asg[decorator]
        else:
            decorator = asg.add_file(decorator, proxy=boost_python_decorator())
        decorator.module = module

    if 'helder' in kwargs:
        module.header.helder = kwargs.pop('helder')

    return module

def boost_python_pattern_generator(asg, pattern=None, *args, **kwargs):
    """
    """
    return boost_python_generator(asg, asg.declarations(pattern=pattern), *args, **kwargs)


def boost_python_internal_generator(asg, pattern=None, *args, **kwargs):
    """
    """
    return boost_python_generator(asg,
                                  [node for node in asg.declarations(pattern=pattern) if not getattr(node.header, 'is_external_dependency', True)],
                                  *args, **kwargs)
