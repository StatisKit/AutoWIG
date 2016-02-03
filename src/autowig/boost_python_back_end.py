"""
"""

from mako.template import Template
from operator import attrgetter

from .asg import *
from .plugin import node_path, node_rename
from .node_rename import PYTHON_OPERATOR
from .tools import Plugin, camel_case_to_lower, to_camel_case, camel_case_to_upper

__all__ = ['boost_python_call_policy', 'boost_python_held_type', 'boost_python_export', 'boost_python_module', 'boost_python_decorator']

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

boost_python_call_policy = Plugin('autowig.boost_python_call_policy', brief="AutoWIG Boost.Python call policy plugins",
        detailed="")

def boost_python_default_call_policy(self, node):
    if isinstance(node, FunctionProxy):
        return_type = node.return_type.desugared_type
        if return_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif return_type.is_reference:
            if return_type.is_const or isinstance(return_type.unqualified_type, (FundamentalTypeProxy, EnumerationProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
    elif isinstance(node, MethodProxy):
        return_type = node.return_type.desugared_type
        if return_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif return_type.is_reference:
            if return_type.is_const or isinstance(return_type.unqualified_type, (FundamentalTypeProxy, EnumerationProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_internal_reference<>()'

boost_python_call_policy['default'] = boost_python_default_call_policy
del boost_python_default_call_policy
boost_python_call_policy.plugin = 'default'

boost_python_held_type = Plugin('autowig.boost_python_held_type', brief="AutoWIG Boost.Python policy plugins",
        detailed="")

def ptr_held_type(self, node):
    if isinstance(node, ClassProxy):
        return node.globalname + '*'
    elif not isinstance(node, BoostPythonExportFileProxy):
        raise TypeError('\'node\' parameter')

boost_python_held_type['ptr'] = ptr_held_type
del ptr_held_type

def std_unique_ptr_held_type(self, node):
    if isinstance(node, ClassProxy):
        return 'std::unique_ptr< ' + node.globalname + ' >'
    elif isinstance(node, BoostPythonExportFileProxy):
        return '#include <memory>'
    else:
        raise TypeError('\'node\' parameter')

boost_python_held_type['std::unique_ptr'] = std_unique_ptr_held_type
del std_unique_ptr_held_type
boost_python_held_type.plugin = 'std::unique_ptr'

def std_shared_ptr_held_type(self, node):
    if isinstance(node, ClassProxy):
        return 'std::shared_ptr< ' + node.globalname + ' >'
    elif isinstance(node, BoostPythonExportFileProxy):
        return '#include <memory>'
    else:
        raise TypeError('\'node\' parameter')

boost_python_held_type['std::shared_ptr'] = std_shared_ptr_held_type
del std_shared_ptr_held_type

def boost_shared_ptr_held_type(self, node):
    if isinstance(node, ClassProxy):
        return 'boost::shared_ptr< ' + node.globalname + ' >'
    elif isinstance(node, BoostPythonExportFileProxy):
        return '#include <boost/shared_ptr.hpp>'
    else:
        raise TypeError('\'node\' parameter')

boost_python_held_type['boost::shared_ptr'] = boost_shared_ptr_held_type
del boost_shared_ptr_held_type

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self._boost_python_export
        if isinstance(boost_python_export, bool):
            return boost_python_export
        else:
            return self._asg[boost_python_export]
    elif self.globalname == '::':
        return True
    elif self._valid_boost_python_export and getattr(self, 'access', 'public') == 'public':
        return self._default_boost_python_export and self.parent.boost_python_export
    else:
        return False

def set_boost_python_export(self, boost_python_export):
    if boost_python_export and not self._valid_boost_python_export:
        raise ValueError('\'boost_python_export\' cannot be set to another value than \'False\'')
    elif not boost_python_export and self.globalname == '::':
        raise ValueError('\'boost_python_export\' cannot be set to \'False\'')
    if isinstance(boost_python_export, basestring):
        boost_python_export = self._asg[boost_python_export]
    if isinstance(boost_python_export, BoostPythonExportFileProxy):
        scope = boost_python_export.scope
        if scope is None or scope == self.parent:
            del self.boost_python_export
            boost_python_export._declarations.add(self._node)
            boost_python_export = boost_python_export._node
    elif not isinstance(boost_python_export, bool):
        raise TypeError('\'boost_python_export\' parameter must be boolean, a \'' + BoostPythonExportFileProxy.__class__.__name__ + '\' instance or identifer')
    self._asg._nodes[self._node]['_boost_python_export'] = boost_python_export

def del_boost_python_export(self):
    boost_python_export = self.boost_python_export
    if isinstance(boost_python_export, BoostPythonExportFileProxy):
        boost_python_export._declarations.remove(self._node)
    self._asg._nodes[self._node].pop('_boost_python_export', boost_python_export)

DeclarationProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
DeclarationProxy._default_boost_python_export = False
DeclarationProxy._valid_boost_python_export = True

def boost_python_export(self):
    desugared_type = self.desugared_type
    return not(desugared_type.is_pointer_chain or desugared_type.is_rvalue_reference)

QualifiedTypeProxy.boost_python_export = property(boost_python_export)
del boost_python_export

def _default_boost_python_export(self):
    return not self.localname.startswith('_')

NamespaceProxy._default_boost_python_export = property(_default_boost_python_export)
ClassProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return not self.localname.startswith('_') and not self.is_smart_pointer

ClassTemplateProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return self.specialize is None and not self.is_smart_pointer or self.specialize.boost_python_export

ClassTemplateSpecializationProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return self.qualified_type.boost_python_export

VariableProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    return all(parameter.qualified_type.boost_python_export for parameter in self.parameters)

ConstructorProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
del get_boost_python_export

def _default_boost_python_export(self):
    if self.return_type.boost_python_export and all(parameter.qualified_type.boost_python_export for parameter in self.parameters):
        return not self.localname.startswith('operator')
    else:
        return False

FunctionProxy._default_boost_python_export = property(_default_boost_python_export)
del _default_boost_python_export

def _default_boost_python_export(self):
    if self.return_type.boost_python_export and all(parameter.qualified_type.boost_python_export for parameter in self.parameters):
        return not self.localname.startswith('operator') or self.localname.node.localname.strip('operator').strip() in PYTHON_OPERATOR
    else:
        return False

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
        return [declaration for declaration in declarations if not isinstance(declaration, ClassProxy)] + sorted([declaration for declaration in declarations if isinstance(declaration, ClassProxy)], key = lambda cls: cls.depth)

def get_depth(self):
    if not hasattr(self, '_depth'):
        return 0
    else:
        return self._depth

def set_depth(self, depth):
    self._asg._nodes[self._node]['_depth'] = depth

def del_depth(self):
    self._asg._nodes[self._node].pop('_depth')

BoostPythonExportFileProxy.depth = property(get_depth, set_depth, del_depth)
del get_depth, set_depth, del_depth

def get_scope(self):
    if hasattr(self, '_scope'):
        return self._scope

def set_scope(self, scope):
    self._asg._nodes[self._node]['_scope'] = scope

def del_scope(self):
    self._asg._nodes[self._node].pop('_scope')

BoostPythonExportFileProxy.scope = property(get_scope, set_scope, del_scope)
del get_scope, set_scope, del_scope

def get_module(self):
    if hasattr(self, '_module'):
        return self._asg[self._module]

def set_module(self, module):
    _module = self.module
    if _module:
        _module._exports.remove(self._node)
    if isinstance(module, BoostPythonModuleFileProxy):
        module = module._node
    self._asg._nodes[self._node]['_module'] = module
    self.module._exports.add(self._node)

def del_module(self):
    module = self.module
    if module:
        module._exports.remove(self._node)
    self._asg._nodes[self._node].pop('_module', None)

BoostPythonExportFileProxy.module = property(get_module, set_module, del_module)
del get_module, set_module, del_module

class BoostPythonExportBasicFileProxy(BoostPythonExportFileProxy):

    language = 'c++'

    HEADER = Template(text=r"""\
#include <boost/python.hpp>\
% for header in headers:

    % if header.language == 'c':
extern "C" {
    % endif
#include <${header.path}>\
    % if header.language == 'c':

}\
    % endif
% endfor
% for error in errors:

PyObject* error_type_${error.hash} = 0;

void translate_error_${error.hash}(${error.globalname} const & error)
{ PyErr_SetObject(error_type_${error.hash}, boost::python::object(error).ptr()); }
% endfor
""")

    SCOPE = Template(text=r"""\
% for scope in scopes:
        std::string ${node_rename(scope, scope=True) + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${node_rename(scope, scope=True)}");
        boost::python::object ${node_rename(scope, scope=True) + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${node_rename(scope, scope=True) + '_' + scope.hash}_name.c_str()))));
        boost::python::scope().attr("${node_rename(scope, scope=True)}") = ${node_rename(scope, scope=True) + '_' + scope.hash}_module;
        boost::python::scope ${node_rename(scope, scope=True) + '_' + scope.hash}_scope = ${node_rename(scope, scope=True) + '_' + scope.hash}_module;\
% endfor""")

    ENUMERATOR = Template(text="""\
        boost::python::scope().attr("${node_rename(enumerator)}") = (int)(${enumerator.globalname});\
""")

    ENUMERATION = Template(text=r"""\
        boost::python::enum_< ${enumeration.globalname} >("${node_rename(enumation)}")\
    % for enumerator in enumeration.enumerators():
        % if enumerator.boost_python_export:

            .value("${node_rename(enumerator)}", ${enumerator.globalname})\
        % endif
    % endfor
;""")

    VARIABLE = Template(text="""\
        boost::python::scope().attr("${node_rename(variable)}") = ${variable.globalname};\
""")

    FUNCTION = Template(text=r"""\
    % if function.is_overloaded:
        ${function.return_type.globalname} (*function_pointer_${function.hash})(${", ".join(parameter.qualified_type.globalname for parameter in function.parameters)}) = ${function.globalname};
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
);""")

    CLASS = Template(text=r"""\
    % for method in cls.methods():
        % if method.boost_python_export and method.access == 'public' and method.is_overloaded:
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
    % if cls.is_error:
        boost::python::scope class_${cls.hash} = \
    % else:
        \
    % endif
boost::python::class_< ${cls.globalname}, \
    % if held_type(cls):
${held_type(cls)}\
    % else:
${cls.globalname} *\
    % endif
    % if any(base.access == 'public' for base in cls.bases() if base.access == 'public' and base.boost_python_export):
, boost::python::bases< ${", ".join(base.globalname for base in cls.bases() if base.access == 'public' and base.boost_python_export)} >\
    % endif
    % if not cls.is_copyable or cls.is_abstract:
, boost::noncopyable\
    % endif
 >("${node_rename(cls)}", boost::python::no_init)\
    % if not cls.is_abstract:
        % for constructor in cls.constructors:
            % if constructor.access == 'public' and constructor.boost_python_export:

            .def(boost::python::init< ${", ".join(parameter.qualified_type.globalname for parameter in constructor.parameters)} >())\
            % endif
        % endfor
    % endif
    % for method in cls.methods():
        % if method.access == 'public' and method.boost_python_export:

            .def("${node_rename(method)}", \
                % if method.is_overloaded:
method_pointer_${method.hash}\
                % else:
&${method.globalname}\
                % endif
                % if call_policy(method):
, ${call_policy(method)}\
                % endif
)\
        % endif
    % endfor
    % for methodname in set([node_rename(method) for method in cls.methods() if method.access == 'public' and method.is_static and method.boost_python_export]):

            .staticmethod("${methodname}")\
    % endfor
    % for field in cls.fields():
        % if field.access == 'public' and field.boost_python_export:
            % if field.qualified_type.is_const:

            .def_readonly\
            % else:

            .def_readwrite\        //static PyObject* _type = class_${cls.hash}.ptr();
        //struct Translator
        //{ static void translate(${cls.globalname} const & error) { PyErr_SetObject(_type, boost::python::object(error).ptr()); } };
        //Translator< ${cls.globalname} > translator = Translator< ${cls.globalname} >(class_${cls.hash}.ptr());
        //boost::python::register_exception_translator< ${cls.globalname} >(&translator.translate);
            % endif
("${node_rename(field)}", \
            % if not field.is_static:
&\
            % endif
${field.globalname})\
        % endif
    % endfor
;\
    % if held_type(cls):
        % for bse in cls.bases():
            % if bse.access == 'public' and bse.boost_python_export and held_type(bse):

        boost::python::implicitly_convertible< ${held_type(cls)}, ${held_type(bse)} >();\
            % endif
        % endfor
    % endif
    % if cls.is_error:

        error_type_${cls.hash} = class_${cls.hash}.ptr();
        boost::python::register_exception_translator< ${cls.globalname} >(&translate_error_${cls.hash});
    % endif
    """)

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

    #@property
    #def headers(self):
    #    if self._held_type is None:
    #        return self._asg.headers(*self.declarations)
    #    else:
    #        return self._asg.headers(self._asg[self._held_type], *self.declarations)

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
        content = self.HEADER.render(headers = self._asg.headers(*self.declarations), errors = [declaration for declaration in self.declarations if isinstance(declaration, ClassProxy) and declaration.is_error])
        content += '\n\nvoid ' + self.prefix + '()\n{\n'
        content += self.SCOPE.render(scopes = self.scopes,
                node_rename = node_rename)
        for arg in self.declarations:
            if isinstance(arg, EnumeratorProxy):
                content += '\n' + self.ENUMERATOR.render(enumerator = arg,
                        node_rename = node_rename)
            elif isinstance(arg, EnumerationProxy):
                content += '\n' + self.ENUMERATION.render(enumeration = arg,
                        node_rename = node_rename)
            elif isinstance(arg, VariableProxy):
                content += '\n' + self.VARIABLE.render(variable = arg,
                        node_rename = node_rename)
            elif isinstance(arg, FunctionProxy):
                content += '\n' + self.FUNCTION.render(function = arg,
                        node_rename = node_rename,
                        call_policy = boost_python_call_policy)
            elif isinstance(arg, ClassProxy):
                content += '\n' + self.CLASS.render(cls = arg,
                        node_rename = node_rename,
                        held_type = boost_python_held_type,
                        call_policy = boost_python_call_policy)
            elif isinstance(arg, TypedefProxy):
                continue
            else:
                raise NotImplementedError(arg.__class__.__name__)
        content += '\n}'
        return content

class BoostPythonExportMappingFileProxy(BoostPythonExportBasicFileProxy):

    MAPPING = {"class ::std::vector" : Template(r"""\
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

    @property
    def _content(self):
        content = self.HEADER.render(headers = self._asg.headers(*self.declarations), errors = [declaration for declaration in self.declarations if isinstance(declaration, ClassProxy) and declaration.is_error])
        content += '\n\nvoid ' + self.prefix + '()\n{\n'
        content += self.SCOPE.render(scopes = self.scopes,
                node_rename = node_rename)
        for arg in self.declarations:
            if isinstance(arg, EnumeratorProxy):
                content += '\n' + self.ENUMERATOR.render(constant = arg,
                        node_rename = node_rename)
            elif isinstance(arg, EnumerationProxy):
                content += '\n' + self.ENUMERATION.render(enum = arg,
                        node_rename = node_rename)
            elif isinstance(arg, VariableProxy):
                content += '\n' + self.VARIABLE.render(variable = arg,
                        node_rename = node_rename)
            elif isinstance(arg, FunctionProxy):
                content += '\n' + self.FUNCTION.render(function = arg,
                        node_rename = node_rename,
                        call_policy = boost_python_call_policy)
            elif isinstance(arg, ClassProxy):
                content += '\n' + self.CLASS.render(cls = arg,
                        node_rename = node_rename,
                        held_type = boost_python_held_type,
                        call_policy = boost_python_call_policy)
                if arg.globalname in self.MAPPING:
                    content += '\n' + self.MAPPING[arg.globalname].render(cls = arg)
                elif isinstance(arg, ClassTemplateSpecializationProxy) and arg.specialize.globalname in self.MAPPING:
                    content += '\n' + self.MAPPING[arg.specialize.globalname].render(cls = arg)
                elif isinstance(arg, TypedefProxy):
                    continue
                else:
                    raise NotImplementedError(arg.__class__.__name__)
        content += '\n}'
        return content

def boost_python_exports(self, *args, **kwargs):
    return [export for export in self.files(*args, **kwargs) if isinstance(export, BoostPythonExportFileProxy)]

AbstractSemanticGraph.boost_python_exports = boost_python_exports
del boost_python_exports

boost_python_export = Plugin('autowig.boost_python_export', brief="",
        detailed="")

class BoostPythonExportPlugin(object):
    """Plugin for Boost.Python export creation"""

    def __init__(self, proxy):
        if not issubclass(proxy, BoostPythonExportFileProxy):
            raise TypeError('\'proxy\' parameter')
        self._proxy = proxy

    def __call__(self, asg, export):
        if module in asg:
            return asg[module]
        else:
            return asg.add_file(export, proxy=self._proxy)

boost_python_export['basic'] = BoostPythonExportPlugin(BoostPythonExportBasicFileProxy)
boost_python_export['mapping'] = BoostPythonExportPlugin(BoostPythonExportMappingFileProxy)
boost_python_export.plugin = 'mapping'

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

BOOST_PYTHON_MODULE(${module.prefix})
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
    def exports(self):
        if not hasattr(self, '_exports'):
            return []
        else:
            return [export for export in sorted([self._asg[export] for export in self._exports], key = attrgetter('depth'))]

    @property
    def dependencies(self):
        modules = set([self.globalname])
        temp = [declaration for export in self.exports for declaration in export.declarations]
        while len(temp) > 0:
            declaration = temp.pop()
            if isinstance(declaration, FunctionProxy):
                export = declaration.return_type.target.boost_python_export
                if export and not export is True:
                    module = export.module
                    if not module is None:
                        modules.add(module.globalname)
                for prm in declaration.parameters:
                    export = prm.qualified_type.desugared_type.unqualified_type.boost_python_export
                    if export and not export is True:
                        module = export.module
                        if not module is None:
                            modules.add(module.globalname)
            elif isinstance(declaration, (VariableProxy, TypedefProxy)):
                export = declaration.qualified_type.desugared_type.unqualified_type.boost_python_export
                if export and not export is True:
                    module = export.module
                    if not module is None:
                        modules.add(module.globalname)
            elif isinstance(declaration, ClassProxy):
                export = declaration.boost_python_export
                if export and not export is True:
                    module = export.module
                    if not module is None:
                        modules.add(module.globalname)
                temp.extend([bse for bse in declaration.bases() if bse.access == 'public'])
                temp.extend([dcl for dcl in declaration.declarations() if dcl.access == 'public'])
            elif isinstance(declaration, ClassTemplateProxy):
                export = declaration.boost_python_export
                if export and not export is True:
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

    @property
    def _content(self):
        return self.CONTENT.render(module = self)

def boost_python_modules(self, **kwargs):
    return [module for module in self.files(**kwargs) is isinstance(module, BoostPythonModuleFileProxy)]

AbstractSemanticGraph.boost_python_modules = boost_python_modules
del boost_python_modules

boost_python_module = Plugin('autowig.boost_python_module', brief="",
        detailed="")

class BoostPythonModulePlugin(object):
    """Plugin for Boost.Python module creation"""

    def __init__(self, proxy):
        if not issubclass(proxy, BoostPythonModuleFileProxy):
            raise TypeError('\'proxy\' parameter')
        self._proxy = proxy

    def __call__(self, asg, module):
        if module in asg:
            return asg[module]
        else:
            return asg.add_file(module, proxy=self._proxy)

boost_python_module['default'] = BoostPythonModulePlugin(BoostPythonModuleFileProxy)
boost_python_module.plugin = 'default'

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
        self._asg._nodes[self._node]['_module'] = module._node

class BoostPythonDecoratorDefaultFileProxy(BoostPythonDecoratorFileProxy):

    IMPORTS = Template(text=r"""\
__all__ = []\

% for module in modules:

import ${module.package}.${module.modulename}\
% endfor
""")

    SCOPES = Template(text=r"""\
% for scope in scopes:

${module.package}.${module.modulename}.${".".join(node_rename(ancestor) for ancestor in scope.ancestors[1:])}.${node_rename(scope)} = ${module.package}.${module.modulename}.${".".join(node_rename(ancestor, scope=True) for ancestor in scope.ancestors[1:])}.${node_rename(scope)}\
% endfor
""")

    TEMPLATES = Template(text=r"""\
% for tpl, spcs in templates:

${module.package}.${module.modulename}.\
    % if len(tpl.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tpl.ancestors[1:])}.${node_rename(tpl)} = [${", ".join([module.package + "." + module.modulename + "." + ".".join(node_rename(ancestor) for ancestor in spc.ancestors[1:]) + "." + node_rename(spc) for spc in spcs])}]\
    % else:
${node_rename(tpl)} = [${", ".join([module.package + "." + module.modulename + "." + node_rename(spc) for spc in spcs])}]\
    % endif
% endfor""")

    TYPEDEFS = Template(text=r"""\
% for tdf in typedefs:

${module.package}.${module.modulename}.\
    % if len(tdf.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.ancestors[1:])}.\
    % endif
${node_rename(tdf)} = ${tdf.qualified_type.desugared_type.unqualified_type.boost_python_export.module.package}.${tdf.qualified_type.desugared_type.unqualified_type.boost_python_export.module.modulename}.\
    % if len(tdf.qualified_type.desugared_type.unqualified_type.ancestors) > 1:
${".".join(node_rename(ancestor) for ancestor in tdf.qualified_type.desugared_type.unqualified_type.ancestors[1:])}.\
    % endif
${node_rename(tdf.qualified_type.desugared_type.unqualified_type)}\
% endfor""")

    @property
    def _content(self):
        dependencies = self.module.dependencies + [self.module]
        content = [self.IMPORTS.render(modules = sorted(dependencies, key = lambda dependency: dependency.depth))]
        scopes = []
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration.parent, ClassProxy):
                    scopes.append(declaration)
        content.append(self.SCOPES.render(scopes = scopes,
                module = self.module,
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
        content.append(self.TEMPLATES.render(templates = [(self._asg[tpl], spcs) for tpl, spcs in templates.iteritems()],
                module = self.module,
                node_rename = node_rename))
        typedefs = []
        for export in self.module.exports:
            for declaration in export.declarations:
                if isinstance(declaration, TypedefProxy) and declaration.qualified_type.desugared_type.unqualified_type.boost_python_export and not declaration.qualified_type.desugared_type.unqualified_type.boost_python_export is True:
                    typedefs.append(declaration)
                elif isinstance(declaration, ClassProxy):
                    typedefs.extend([tdf for tdf in declaration.typedefs() if tdf.boost_python_export and tdf.qualified_type.desugared_type.unqualified_type.boost_python_export and not tdf.qualified_type.desugared_type.unqualified_type.boost_python_export is True])
        content.append(self.TYPEDEFS.render(typedefs = typedefs, module = self.module, node_rename=node_rename))
        self.content = "\n".join(content)
        return self._content

boost_python_decorator = Plugin('autowig.boost_python', brief="",
        detailed="")

class BoostPythonDecoratorPlugin(object):
    """Plugin for Boost.Python module decoration"""

    def __init__(self, proxy):
        if not issubclass(proxy, BoostPythonDecoratorFileProxy):
            raise TypeError('\'proxy\' parameter')
        self._proxy = proxy

    def __call__(self, asg, decorator, module):
        if decorator in asg:
            decorator = asg[decorator]
        else:
            decorator = asg.add_file(decorator, proxy=self._proxy)
        decorator.module = module
        return decorator

boost_python_decorator['default'] = BoostPythonDecoratorPlugin(BoostPythonDecoratorDefaultFileProxy)
boost_python_decorator.plugin = 'default'

def back_end(asg, module, decorator=None, pattern='.*', prefix='_'):
    """
    """
    module = boost_python_module(asg, module)
    directory = module.parent
    suffix = module.suffix
    nodes = set()
    for node in asg.declarations(pattern=pattern):
        if node.boost_python_export is True:
            print node.gloablname
            if isinstance(node, EnumeratorProxy) and isinstance(node.parent, EnumerationProxy) or isinstance(node, TypedefProxy) and isinstance(node.parent, ClassProxy) or isinstance(node, (FieldProxy, MethodProxy, ConstructorProxy, DestructorProxy, NamespaceProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy)):
                continue
            else:
                node.boost_python_export = boost_python_export(asg, directory.globalname + node_path(node, prefix=prefix, suffix=suffix))
                nodes.add(node.boost_python_export._node)
    for export in asg.boost_python_exports(directory.globalname + '.*' + suffix):
        export.module = module
    if decorator is not None:
        boost_python_decorator(asg, decorator, module.globalname)

def boost_python_closure(self):
    nodes = []
    forbidden = set()
    for node in self.nodes():
        if hasattr(node, 'boost_python_export'):
            if node.boost_python_export and not node.boost_python_export is True:
                nodes.append(node)
            elif not node.boost_python_export:
                target = node
                while isinstance(target, ClassTemplateSpecializationProxy) and target.is_smart_pointer:
                    target = target.templates[0].target
                if not target.boost_python_export:
                    if not isinstance(target, FundamentalTypeProxy):
                        forbidden.add(node._node)
            elif not isinstance(node, (NamespaceProxy, ClassTemplateProxy, ClassTemplatePartialSpecializationProxy)):
                if not isinstance(node, (FieldProxy, MethodProxy, ConstructorProxy, DestructorProxy)):
                    if isinstance(node, EnumConstantProxy):
                        if not isinstance(node.parent, EnumProxy):
                            node.boost_python_export = False
                    else:
                        node.boost_python_export = False
                elif not node.access == 'public':
                    node.boost_python_export = False
    while len(nodes) > 0:
        node = nodes.pop()
        if not node._node in forbidden and not isinstance(node, FundamentalTypeProxy):
            if not node.boost_python_export:
                node.boost_python_export = True
            if isinstance(node, (TypedefProxy, VariableProxy)):
                target = node.qualified_type.desugared_type.unqualified_type
                while isinstance(target, ClassTemplateSpecializationProxy) and target.is_smart_pointer:
                    target = target.templates[0].target
                if not target._node in forbidden:
                    if not target.boost_python_export:
                        nodes.append(target)
                else:
                    node.boost_python_export = False
            elif isinstance(node, FunctionProxy):
                return_type = node.return_type.desugared_type.unqualified_type
                while isinstance(return_type, ClassTemplateSpecializationProxy) and return_type.is_smart_pointer:
                    return_type = return_type.templates[0].target
                parameters = [parameter.qualified_type.desugared_type.unqualified_type for parameter in node.parameters]
                for index in range(len(parameters)):
                    while isinstance(parameters[index], ClassTemplateSpecializationProxy) and parameters[index].is_smart_pointer:
                        parameters[index] = parameters[index].templates[0].target
                if not return_type._node in forbidden and not any([parameter._node in forbidden for parameter in parameters]):
                    if not return_type.boost_python_export:
                        nodes.append(return_type)
                    for parameter in parameters:
                        if not parameter.boost_python_export:
                            nodes.append(parameter)
                else:
                    node.boost_python_export = False
            elif isinstance(node, ConstructorProxy):
                parameters = [parameter.qualified_type.desugared_type.unqualified_type for parameter in node.parameters]
                for index in range(len(parameters)):
                    while isinstance(parameters[index], ClassTemplateSpecializationProxy) and parameters[index].is_smart_pointer:
                        parameters[index] = parameters[index].templates[0].target
                if not any([parameter._node in forbidden for parameter in parameters]):
                    for parameter in parameters:
                        if not parameter.boost_python_export:
                            nodes.append(parameter)
                else:
                    node.boost_python_export = False
            elif isinstance(node, ClassProxy):
                for base in node.bases():
                    if not base.boost_python_export and base.access == 'public':
                        nodes.append(base)
                for dcl in node.declarations():
                    if dcl.boost_python_export is True and dcl.access == 'public':
                        nodes.append(dcl)
    for tdf in self.typedefs():
        if isinstance(tdf.boost_python_export, bool) and not tdf.boost_python_export:
            if not tdf._node in forbidden and tdf.qualified_type.desugared_type.unqualified_type.boost_python_export:
                tdf.boost_python_export = True
                parent = tdf.parent
                while not parent.boost_python_export:
                    parent.boost_python_export = True
                    parent = parent.parent
            else:
                tdf.boost_python_export = False

AbstractSemanticGraph.boost_python_closure = boost_python_closure
del boost_python_closure
