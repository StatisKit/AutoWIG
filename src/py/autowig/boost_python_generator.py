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
                  FilesystemProxy,
                  DeclarationProxy,
                  ClassProxy,
                  FileProxy,
                  FieldProxy,
                  HeaderProxy,
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
from .plugin_manager import node_path, node_rename, documenter, visitor
from .proxy_manager import ProxyManager
from .node_rename import PYTHON_OPERATOR
from .plugin_manager import PluginManager
from .generator import iterator_range

__all__ = ['boost_python_call_policy', 'boost_python_export_factory', 'boost_python_module_factory', 'boost_python_decorator_factory']

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
        if isinstance(node, ClassTemplateSpecializationProxy) and node.is_smart_pointer:
            return node.templates[0].desugared_type.unqualified_type.boost_python_export
        else:
            return True
    else:
        return isinstance(node, FundamentalTypeProxy)

def get_boost_python_export(self):
    desugared_type = self.desugared_type
    if desugared_type.is_pointer_chain or desugared_type.is_rvalue_reference:
        return False
    elif desugared_type.is_fundamental_type:
        return not desugared_type.is_pointer
    else:
        if desugared_type.is_class and not desugared_type.unqualified_type.is_copyable:
            if desugared_type.is_reference and desugared_type.is_const or not desugared_type.is_qualified:
                return getattr(desugared_type.unqualified_type, 'is_smart_pointer', False)
        return desugared_type.unqualified_type.boost_python_export

def set_boost_python_export(self, boost_python_export):
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
    self._asg._nodes[self._node]['_boost_python_export'] = boost_python_export
    if isinstance(boost_python_export, BoostPythonExportFileProxy):
        scope = boost_python_export.scope
        boost_python_export._declarations.add(self._node)
        boost_python_export = boost_python_export._node

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
    return not self.localname.startswith('_') and len(self.declarations()) > 0 and bool(self.parent.boost_python_export)

NamespaceProxy._default_boost_python_export = property(_default_boost_python_export)
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
        return not qualified_type.is_reference and not qualified_type.is_pointer and bool(qualified_type.unqualified_type.boost_python_export)
    else:
        return False

TypedefProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return bool(self.parent.boost_python_export)

FunctionProxy._default_boost_python_export = property(_default_boost_python_export)

def _valid_boost_python_export(self):
    if boost_python_call_policy(self) == 'boost::python::return_value_policy< boost::python::reference_existing_object >()':
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
del _valid_boost_python_export

def _valid_boost_python_export(self):
    if boost_python_call_policy(self) in ['boost::python::return_internal_reference<>()',
                                          'boost::python::return_value_policy< boost::python::reference_existing_object >()']:
        if not isinstance(self.return_type.desugared_type.unqualified_type, ClassProxy):
            return False
    if self.access == 'public' and self.return_type.boost_python_export and all(bool(parameter.boost_python_export) for parameter in self.parameters):
        return not self.localname.startswith('operator') or self.localname.strip('operator').strip() in PYTHON_OPERATOR
    else:
        return False

MethodProxy._valid_boost_python_export = property(_valid_boost_python_export)
del _valid_boost_python_export

MethodProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

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
    def scope(self):
        if hasattr(self, '_scope'):
            return self._scope

    @scope.setter
    def scope(self, scope):
        self._asg._nodes[self._node]['_scope'] = scope

    @scope.deleter
    def del_scope(self):
        self._asg._nodes[self._node].pop('_scope')

    @property
    def module(self):
        if hasattr(self, '_module'):
            return self._asg[self._module]

    @module.setter
    def module(self, module):
        _module = self.module
        if _module:
            _module._exports.remove(self._node)
        if isinstance(module, BoostPythonModuleFileProxy):
            module = module._node
        self._asg._nodes[self._node]['_module'] = module
        self.module._exports.add(self._node)

    @module.deleter
    def module(self):
        module = self.module
        if module:
            module._exports.remove(self._node)
        self._asg._nodes[self._node].pop('_module', None)

    def edit(self, line):
        pass

class BoostPythonExportBasicFileProxy(BoostPythonExportFileProxy):

    language = 'c++'

    HEADER = Template(text=r"""\
#include <type_traits>
#include <boost/python.hpp>\
% for header in headers:

    % if header.language == 'c':
extern "C" {
    % endif
#include <${header.searchpath}>\
    % if header.language == 'c':

}\
    % endif
% endfor""")

    HELDTYPE = "namespace autowig { template<class T> using HeldType = std::shared_ptr< T >; }"

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
    boost::python::enum_< ${enumeration.globalname} >("${node_rename(enumeration)}")\
    % if enumeration.is_scoped:
        % for enumerator in enumeration.enumerators:
            % if enumerator.boost_python_export:

        .value("${node_rename(enumerator)}", ${enumerator.globalname})\
            % endif
        % endfor
    % else:
        % for enumerator in enumeration.enumerators:
            % if enumerator.boost_python_export:

        .value("${node_rename(enumerator)}", ${enumerator.globalname.replace(enumeration.localname + '::', '')})\
            % endif
        % endfor
    % endif
;""")

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
    % if call_policy(function):
, ${call_policy(function)}\
    % endif
, "${documenter(function)}");""")

    ERROR = Template(text=r"""\
namespace autowig
{
    PyObject* error_${error.hash} = nullptr;

    void translate_${error.hash}(${error.globalname} const & error)
    { PyErr_SetString(error_${error.hash}, error.what()); };
}""")

    DECORATOR = Template(text=r"""\
% if not cls.is_error:
namespace autowig
{
    % for method in cls.methods(access='public'):
        % if method.boost_python_export and method.return_type.is_reference and not method.return_type.is_const and method.return_type.unqualified_type.is_assignable:
    void method_decorator_${method.hash}\
(${cls.globalname + " const" * bool(method.is_const) + " & instance, " + \
   ", ".join(parameter.qualified_type.globalname + ' param_in_' + str(parameter.index) for parameter in method.parameters) + ", " * bool(method.nb_parameters > 0) + 'const ' + method.return_type.globalname + ' param_out'})
    { instance.${method.localname}\
(${", ".join('param_in_' + str(parameter.index) for parameter in method.parameters)}) = param_out; }
        % endif
    % endfor
}
%endif""")

    CLASS = Template(text=r"""\
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
    boost::python::class_< ${cls.globalname}, autowig::HeldType< ${cls.globalname} >\
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
                % if method.is_overloaded:
method_pointer_${method.hash}, \
                % else:
&${method.globalname}, \
                % endif
                % if call_policy(method):
${call_policy(method)}, \
                % endif
"${documenter(method)}");
                % if method.return_type.is_reference and not method.return_type.is_const and method.return_type.unqualified_type.is_assignable:
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
                % if call_policy(function):
${call_policy(function)}, \
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

    if(std::is_class< autowig::HeldType< ${cls.globalname} > >::value)
    {
        % for bse in cls.bases(access='public'):
            % if bse.boost_python_export:
        boost::python::implicitly_convertible< autowig::HeldType< ${cls.globalname} >, autowig::HeldType< ${bse.globalname} > >();
            % endif
        % endfor
    }
    % endif
% else:
    std::string name_${cls.hash} = boost::python::extract< std::string >(boost::python::scope().attr("__name__"));
    name_${cls.hash} = name_${cls.hash} + "." + "${node_rename(cls)}";
    autowig::error_${cls.hash} = PyErr_NewException(strdup(name_${cls.hash}.c_str()), PyExc_RuntimeError, NULL);
    boost::python::scope().attr("${node_rename(cls)}") = boost::python::object(boost::python::handle<>(boost::python::borrowed(autowig::error_${cls.hash})));
    boost::python::register_exception_translator< ${cls.globalname} >(&autowig::translate_${cls.hash});
% endif""")

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
    def scopes(self):
        if len(self._declarations) > 0:
            return self.declarations[0].ancestors[1:]
        else:
            return []

    @property
    def _content(self):
        content = self.HEADER.render(headers = [self._asg[header] for header in self._asg._headers])
        #[header for header in self._asg.files(header=True) if header.is_self_contained])
        if any(declaration for declaration in self.declarations if isinstance(declaration, ClassProxy)):
            content += '\n\n' + self.HELDTYPE
        for arg in self.declarations:
            if isinstance(arg, ClassProxy) and arg.is_error:
                content += '\n\n' + self.ERROR.render(error = arg)
        for arg in self.declarations:
            if isinstance(arg, ClassProxy):
                content += '\n\n' + self.DECORATOR.render(cls = arg)
        content += '\n\nvoid ' + self.prefix + '()\n{\n'
        content += self.SCOPE.render(scopes = self.scopes,
                node_rename = node_rename,
                documenter = documenter)
        for arg in self.declarations:
            if isinstance(arg, EnumeratorProxy):
                content += '\n' + self.ENUMERATOR.render(enumerator = arg,
                        node_rename = node_rename,
                        documenter = documenter)
            elif isinstance(arg, EnumerationProxy):
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
                        documenter = documenter,
                        call_policy = boost_python_call_policy)
            elif isinstance(arg, ClassProxy):
                content += '\n' + self.CLASS.render(cls = arg,
                        node_rename = node_rename,
                        documenter = documenter,
                        call_policy = boost_python_call_policy,
                        iterator_range = iterator_range)
            elif isinstance(arg, TypedefProxy):
                continue
            else:
                raise NotImplementedError(arg.__class__.__name__)
        content += '\n}'
        return content

    def _feedback(self, row):
        if row is None:
            return '\n'.join("asg['" + declaration.globalname + "'].boost_python_export = False"
                             for declaration in self.declarations
                             if isinstance(declaration, ClassProxy)) + \
                    "\nif '" + self.globalname + "' in asg:\n\tasg['" + self.globalname + "'].remove()\n"
        if row <= 0:
            raise ValueError()
        if not self.on_disk:
            raise ValueError()
        with open(self.globalname, 'r') as filehandler:
            lines = filehandler.readlines()
            if not row == len(lines):
                row = row - 1
                line = lines[row]
                parsed = parse.parse('    boost::python::class_< {globalname}, autowig::HeldType{suffix}', line)
                if parsed:
                    return "if asg['" + parsed["globalname"] + "'].is_copyable:\n\tasg['" + parsed["globalname"] + "'].is_copyable = False\nelse:\n\tasg['" + parsed["globalname"] + "'].boost_python_export = False\n\t\n\tif '" + self.globalname + "' in asg:\n\t\tasg['" + self.globalname + "'].remove()\n"
                else:
                    while row > 0 and parsed is None:
                        row = row - 1
                        parsed = parse.parse('    boost::python::class_< {globalname}, autowig::HeldType{suffix}', lines[row])
                    row = row + 1
                    while row < len(lines) and parsed is None:
                        parsed = parse.parse('    boost::python::class_< {globalname}, autowig::HeldType{suffix}', lines[row])
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
                                if not 'what' in parsed.named:
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
        return ""





class BoostPythonExportMappingFileProxy(BoostPythonExportBasicFileProxy):

    TO = {
            "class ::std::unique_ptr" : Template(r"""\
    struct unique_ptr_${cls.hash}_to_python
    {
        static PyObject* convert(${cls.globalname} const & unique_ptr_${cls.hash})
        {
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
                result.push_back((${cls.templates[0].globalname})(boost::python::extract< ${cls.templates[0].globalname} >(py_elem_obj)));
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

    IGNORE = {"class ::std::shared_ptr", "class ::std::unique_ptr"}

    def get_content(self):
        content = self.HEADER.render(headers = [self._asg[header] for header in self._asg._headers])
        #[header for header in self._asg.files(header=True) if header.is_self_contained])
        #self._asg.includes(*self.declarations))
        #content = self.HEADER.render(headers = self._asg.includes(*self.declarations), errors = [declaration for declaration in self.declarations if isinstance(declaration, ClassProxy) and declaration.is_error])
        if any(declaration for declaration in self.declarations if isinstance(declaration, ClassProxy)):
            content += '\n\n' + self.HELDTYPE
        for arg in self.declarations:
            if isinstance(arg, ClassProxy) and arg.is_error:
                content += '\n\n' + self.ERROR.render(error = arg)
        for arg in self.declarations:
            if isinstance(arg, ClassProxy):
                content += '\n\n' + self.DECORATOR.render(cls = arg)
        content += '\n\nvoid ' + self.prefix + '()\n{\n' + self.SCOPE.render(scopes = self.scopes, node_rename = node_rename, documenter = documenter)
        for arg in self.declarations:
            if isinstance(arg, EnumeratorProxy):
                content += '\n' + self.ENUMERATOR.render(enumerator = arg,
                        node_rename = node_rename,
                        documenter = documenter)
            elif isinstance(arg, EnumerationProxy):
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
                        documenter = documenter,
                        call_policy = boost_python_call_policy)
            elif isinstance(arg, ClassTemplateSpecializationProxy):
                if arg.globalname not in self.IGNORE and arg.specialize.globalname not in self.IGNORE:
                    content += '\n' + self.CLASS.render(cls = arg,
                            node_rename = node_rename,
                            documenter = documenter,
                            call_policy = boost_python_call_policy,
                            iterator_range = iterator_range)
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
                            documenter = documenter,
                            call_policy = boost_python_call_policy,
                            iterator_range = iterator_range)
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

BoostPythonExportMappingFileProxy._content = property(BoostPythonExportMappingFileProxy.get_content)

def boost_python_exports(self, *args, **kwargs):
    return [export for export in self.files(*args, **kwargs) if isinstance(export, BoostPythonExportFileProxy)]

AbstractSemanticGraph.boost_python_exports = boost_python_exports
del boost_python_exports

boost_python_export_factory = ProxyManager('autowig.boost_python_export', BoostPythonExportFileProxy, brief="",
        details="")

class BoostPythonModuleFileProxy(FileProxy):

    @property
    def _clean_default(self):
        return len(self._exports) == 0

    CONTENT = Template(text=r"""\
#include <boost/python.hpp>

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
                    if not module is None:
                        modules.add(module.globalname)
                for prm in declaration.parameters:
                    export = prm.qualified_type.desugared_type.unqualified_type.boost_python_export
                    if export and export is not True:
                        module = export.module
                        if not module is None:
                            modules.add(module.globalname)
            elif isinstance(declaration, (VariableProxy, TypedefProxy)):
                export = declaration.qualified_type.desugared_type.unqualified_type.boost_python_export
                if export and export is not True:
                    module = export.module
                    if not module is None:
                        modules.add(module.globalname)
            elif isinstance(declaration, ClassProxy):
                export = declaration.boost_python_export
                if export and export is not True:
                    module = export.module
                    if not module is None:
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

BoostPythonModuleFileProxy.dependencies = property(BoostPythonModuleFileProxy.get_dependencies)

BoostPythonModuleFileProxy._content = property(BoostPythonModuleFileProxy.get_content)

def boost_python_modules(self, **kwargs):
    return [module for module in self.files(**kwargs) if isinstance(module, BoostPythonModuleFileProxy)]

AbstractSemanticGraph.boost_python_modules = boost_python_modules
del boost_python_modules

boost_python_module_factory = ProxyManager('autowig.boost_python_module', BoostPythonModuleFileProxy, brief="",
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
import ${decorator.package}._${module.prefix}
""")

    SCOPES = Template(text=r"""\
% if len(scopes) > 0:
# Resolve scopes
    % for scope in scopes:
${decorator.package}._${module.prefix}.${".".join(node_rename(ancestor) for ancestor in scope.ancestors[1:])}.${node_rename(scope)} = ${decorator.package}._${module.prefix}.${".".join(node_rename(ancestor, scope=True) for ancestor in scope.ancestors[1:])}.${node_rename(scope)}
    % endfor
% endif
""")

    TEMPLATES = Template(text=r"""\
% if templates:
# Group template specializations
    % for tpl, spcs in templates:
${decorator.package}._${module.prefix}.\
        % if len(tpl.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tpl.ancestors[1:])}.${node_rename(tpl)} = [${", ".join([decorator.package + '._' + module.prefix + "." + ".".join(node_rename(ancestor) for ancestor in spc.ancestors[1:]) + "." + node_rename(spc) for spc in spcs])}]
        % else:
${node_rename(tpl)} = [${", ".join([decorator.package + '._' + module.prefix + "." + node_rename(spc) for spc in spcs])}]
        % endif
    % endfor
% endif""")

    TYPEDEFS = Template(text=r"""\
% if typedefs:
# Define aliases
    % for tdf in typedefs:
${decorator.package}._${module.prefix}.\
        % if len(tdf.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.ancestors[1:])}.\
        % endif
${node_rename(tdf)} = ${tdf.qualified_type.desugared_type.unqualified_type.boost_python_export.module.decorator.package}._${tdf.qualified_type.desugared_type.unqualified_type.boost_python_export.module.prefix}.\
        % if len(tdf.qualified_type.desugared_type.unqualified_type.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.qualified_type.desugared_type.unqualified_type.ancestors[1:])}.\
        % endif
${node_rename(tdf.qualified_type.desugared_type.unqualified_type)}
    % endfor
% endif""")

    def get_content(self):
        dependencies = [module for module in self.module.get_dependencies()]
        content = [self.IMPORTS.render(decorator = self, module = self.module, dependencies = [module.decorator for module in sorted(dependencies, key = lambda dependency: dependency.depth)])]
        scopes = []
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration.parent, ClassProxy):
                    scopes.append(declaration)
        content.append(self.SCOPES.render(scopes = scopes, decorator = self, module = self.module,
                node_rename = node_rename))
        templates = dict()
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration, ClassTemplateSpecializationProxy):
                    spc = declaration.specialize._node
                    if spc in templates:
                        templates[spc].append(declaration)
                    else:
                        templates[spc] = [declaration]
        content.append(self.TEMPLATES.render(decorator = self, module = self.module, templates = [(self._asg[tpl], spcs) for tpl, spcs in templates.iteritems()],
                node_rename = node_rename))
        typedefs = []
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration, TypedefProxy) and declaration.qualified_type.desugared_type.unqualified_type.boost_python_export and declaration.qualified_type.desugared_type.unqualified_type.boost_python_export is not True:
                    typedefs.append(declaration)
                elif isinstance(declaration, ClassProxy):
                    typedefs.extend([tdf for tdf in declaration.typedefs() if tdf.boost_python_export and tdf.qualified_type.desugared_type.unqualified_type.boost_python_export and tdf.qualified_type.desugared_type.unqualified_type.boost_python_export is not True])
        content.append(self.TYPEDEFS.render(decorator = self, module = self.module, typedefs = typedefs, node_rename=node_rename))
        return "\n".join(content)


BoostPythonDecoratorDefaultFileProxy._content = property(BoostPythonDecoratorDefaultFileProxy.get_content)

boost_python_decorator_factory = ProxyManager('autowig.boost_python_decorator', BoostPythonDecoratorFileProxy, brief="",
        details="")

def boost_python_generator(asg, nodes, module='./module.cpp', decorator=None, **kwargs):
    """
    """
    if 'env' in kwargs:
        env = kwargs.pop('env')
        if 'autowig_generator_closure' in env and 'closure'not in kwargs:
            kwargs['closure'] = env['autowig_generator_closure']
        if 'autowig_generator_prefix' in env and 'prefix' not in kwargs:
            kwargs['prefix'] = env['autowig_generator_prefix']
        if 'autowig_generator_cache' in env and 'cache' not in kwargs:
            kwargs['cache'] = env['autowig_generator_cache']

    if module in asg:
        module = asg[module]
    else:
        module = asg.add_file(module, proxy=boost_python_module_factory())

    if kwargs.pop('cache', True):
        asg._headers = [header.globalname for header in asg.files(header=True) if not header.is_external_dependency and header.is_self_contained]

    white = [asg['::']]
    while len(white) > 0:
        node = white.pop()
        export = node.boost_python_export
        if not export:
            black = [node]
            while len(black) > 0:
                temp = black.pop()
                if not getattr(temp, '_boost_python_export', False):
                    temp.boost_python_export = False
                    if isinstance(temp, NamespaceProxy):
                        black.extend(temp.declarations())
                    elif isinstance(temp, EnumerationProxy):
                        black.extend(temp.enumerators)
                    elif isinstance(temp, ClassProxy):
                        black.extend(temp.declarations())
        else:
            if isinstance(node, NamespaceProxy):
                node.boost_python_export = export
                white.extend(node.declarations())
            elif isinstance(node, EnumerationProxy):
                node.boost_python_export = export
                white.extend(node.enumerators)
            elif isinstance(node, ClassProxy):
                node.boost_python_export = export
                white.extend(node.declarations())

    white = [asg['::']]
    while len(white) > 0:
        node = white.pop()
        export = node.boost_python_export
        if export:
            node.boost_python_export = export
            if isinstance(node, NamespaceProxy):
                white.extend(node.declarations())
            elif isinstance(node, EnumerationProxy):
                white.extend(node.enumerators)
            elif isinstance(node, ClassProxy):
                white.extend(node.declarations())

    directory = module.parent
    suffix = module.suffix
    prefix = kwargs.pop('prefix', 'wrapper_')

    if kwargs.pop('closure', True):
        plugin = visitor.plugin
        visitor.plugin = 'boost_python'
        nodes += asg.dependencies(*nodes)
        visitor.plugin = plugin

    _nodes = set([node._node for node in nodes])

    exports = set()
    for node in nodes:
        if node.boost_python_export is True:
            if isinstance(node, EnumeratorProxy) and isinstance(node.parent, EnumerationProxy) or isinstance(node, TypedefProxy) and isinstance(node.parent, ClassProxy) or isinstance(node, (FieldProxy, MethodProxy, ConstructorProxy, DestructorProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy)) or isinstance(node, FunctionProxy) and isinstance(node.parent, ClassProxy):
                continue
            else:
                export = directory.globalname + node_path(node, prefix=prefix, suffix=suffix).strip('./')
                if export in asg:
                    export = asg[export]
                else:
                    export = asg.add_file(export, proxy=boost_python_export_factory())
                node.boost_python_export = export
                exports.add(export._node)

    exports = [asg[export] for export in exports]
    for export in exports:
        export.module = module

    if decorator:
        if decorator in asg:
            decorator = asg[decorator]
        else:
            decorator = asg.add_file(decorator, proxy=boost_python_decorator_factory())
        decorator.module = module
        return [module] + exports + [decorator]
    else:
        return [module] + exports

def boost_python_pattern_generator(asg, pattern=None, **kwargs):
    """
    """
    return boost_python_generator(asg, asg.declarations(pattern=pattern), **kwargs)


def boost_python_internal_generator(asg, pattern=None, **kwargs):
    """
    """
    return boost_python_generator(asg,
                                  [node for node in asg.declarations(pattern=pattern) if not getattr(node.header, 'is_external_dependency', True)],
                                  **kwargs)
