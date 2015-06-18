from abc import ABCMeta
import os
from mako.template import Template
import re
import itertools
from path import path
import anydbm
import warnings

from .asg import AbstractSemanticGraph, DirectoryProxy, FileProxy, CodeNodeProxy, FundamentalTypeProxy, NamespaceProxy, EnumConstantProxy, EnumProxy, VariableProxy, FunctionProxy, FieldProxy, MethodProxy, ConstructorProxy, ClassProxy, ClassTemplateSpecializationProxy
from .tools import to_path, lower, remove_templates
from .custom_warnings import NotImplementedOperatorWarning

__all__ = ['HeldType', 'BoostSharedPointer', 'BoostPythonExportTemplate', 'BoostPythonExportEnumConstantsTemplate', 'BoostPythonExportEnumTemplate', 'BoostPythonExportVariableTemplate', 'BoostPythonExportFunctionsTemplate', 'BoostPythonExportClassTemplate', 'BoostPythonFileProxy']

def get_to_python(self):
    if not hasattr(self, '_to_python'):
        return False
    else:
        return self._to_python

def set_to_python(self, to_python):
    if to_python:
        self._asg._nodes[self.id]['_to_python'] = True
    else:
        del self._to_python

def del_to_python(self):
    self._asg._nodes[self._id].pop('_to_python', True)

CodeNodeProxy.to_python = property(get_to_python, set_to_python, del_to_python)
del get_to_python, set_to_python, del_to_python

class HeldType(object):
    """
    """

    def include(self):
        return ''

    @staticmethod
    def __call__(cls):
        return cls.globalname + ' *'

    def match(self, cls):
        return False

class BoostSharedPointer(HeldType):
    """
    """

    def include(self):
        return '\n#include <boost/shared_ptr.hpp>'

    @staticmethod
    def __call__(cls):
        return 'boost::shared_ptr< ' + cls.globalname + ' >'

    def match(self, cls):
        return re.match(cls.globalname, '^boost::shared_ptr<(.*)>$')

def get_return_value_policy(self):
    if hasattr(self, '_return_value_policy'):
        return self._return_value_policy
    else:
        result_type = self.result_type
        if result_type.is_reference or result_type.is_pointer:
            self.return_value_policy = 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        else:
            self.return_value_policy = None
        return self._return_value_policy

def set_return_value_policy(self, return_value_policy):
    self._asg._nodes[self.id]['_return_value_policy'] = return_value_policy

def del_return_value_policy(self):
    self._asg._nodes[self._node].pop('_return_value_policy', None)

FunctionProxy.return_value_policy = property(get_return_value_policy, set_return_value_policy, del_return_value_policy)
del get_return_value_policy, set_return_value_policy, del_return_value_policy

class BoostPythonExportTemplate(object):

    def __init__(self, filename, *scopes, **kwargs):
        include = kwargs.get('include', None)
        if include is None:
            def include(header):
                return '<' + re.sub('(.*)include/(.*)', r'\2', header.globalname) + '>'
            self._include = include
        else:
            if not callable(include):
                raise TypeError('\'include\' parameter')
            self._include = include
        self.filename = filename
        self.scopes = scopes

    def include(self, header):
        if header.language == 'c++':
            return "#include " + self._include(header) + ""
        elif header.language == 'c':
            return "extern \"C\" { #include " + self._include(header) + "}"

    def __str__(self):
        return self.template.render(obj=self)

    @classmethod
    def scopename(cls, scope):
        if isinstance(scope, ClassProxy):
            return '_' + lower(scope.localname)
        else:
            return lower(scope.localname)

    @classmethod
    def fctname(cls, function):
        return lower(function.localname)

    @classmethod
    def mtdname(cls, method):
        fctname = method.localname
        pattern = re.compile('operator(.*)')
        if pattern.match(fctname):
            operator = pattern.split(fctname)[1].replace(' ', '')
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
                return '__neq__'
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
                if method.is_const:
                    return '__getitem__'
                else:
                    return '__setitem__'
            elif operator == '()':
                return '__call__'
            else:
                warnings.warn(operator, NotImplementedOperatorWarning)
        else:
            return cls.fctname(method)

    def clsname(self, cls):
        if isinstance(cls, ClassTemplateSpecializationProxy):
            return remove_templates(cls.localname) + '_' + cls.hash
        else:
            return cls.localname

class BoostPythonExportEnumConstantsTemplate(BoostPythonExportTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor

void ${obj.filename}()
{
% for scope in obj.scopes:
    % if not scope.globalname == '::':
    std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scopename(scope)}");
    boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
    boost::python::scope().attr("${obj.scopename(scope)}") = ${scope.localname + '_' + scope.hash}_module;
    boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;
    % endif
% endfor
% for constant in obj.constants:
    boost::python::scope().attr("${constant.localname}") = (int)(${constant.globalname});
% endfor
}""")

    def __init__(self, filename, *scopes, **kwargs):
        super(BoostPythonExportEnumConstantsTemplate, self).__init__(filename, *scopes, **kwargs)
        self.constants = kwargs.pop('constants')

    @property
    def headers(self):
        headers = dict()
        for header in [constant.header for constant in self.constants]:
            headers[header.globalname] = header
        return [header for filename, header in sorted(headers.items())]


class BoostPythonExportEnumTemplate(BoostPythonExportTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>
${obj.include(obj.header)}

void ${obj.filename}()
{
% for scope in obj.scopes:
    % if not scope.globalname == '::':
    std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scopename(scope)}");
    boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
    boost::python::scope().attr("${obj.scopename(scope)}") = ${scope.localname + '_' + scope.hash}_module;
    boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;
    % endif
% endfor
    boost::python::enum_< ${obj.enum.globalname} >("${obj.enum.localname}")\
    % for constant in obj.enum.constants:

        .value("${constant.localname}", ${constant.globalname})\
    % endfor
;
}""")

    def __init__(self, filename, *scopes, **kwargs):
        super(BoostPythonExportEnumTemplate, self).__init__(filename, *scopes, **kwargs)
        self.enum = kwargs.pop('enum')

    @property
    def header(self):
        return self.enum.header

class BoostPythonExportVariableTemplate(BoostPythonExportTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor

void ${obj.filename}()
{
% for scope in obj.scopes:
    % if not scope.globalname == '::':
    std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scopename(scope)}");
    boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
    boost::python::scope().attr("${obj.scopename(scope)}") = ${scope.localname + '_' + scope.hash}_module;
    boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;
    % endif
% endfor
    boost::python::scope().attr("${obj.variable.localname}") = ${obj.variable.globalname};
}""")

    def __init__(self, filename, *scopes, **kwargs):
        super(BoostPythonExportVariableTemplate, self).__init__(filename, *scopes, **kwargs)
        self.variable = kwargs.pop('variable')

    @property
    def header(self):
        return self.variable.header

    @property
    def headers(self):
        headers = dict()
        header = self.variable.header
        if not header is None:
            headers[header.globalname] = header
        if not isinstance(self.variable.type.target, FundamentalTypeProxy):
            header = self.variable.type.target.header
            if not header is None:
                headers[header.globalname] = header
        return [header for filename, header in sorted(headers.items())]


class BoostPythonExportFunctionsTemplate(BoostPythonExportTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor

% if any(function.is_overloaded for function in obj.functions):
namespace autowig
{
    % for function in obj.functions:
        % if function.is_overloaded:
    ${function.result_type.globalname} (\
            % if len(obj.scopes) > 0:
::\
            % endif
${'::'.join(obj.scopes)}::*${function.localname}_${function.hash})(${", ".join(parameter.type.globalname for parameter in function.parameters)}) \
            % if function.is_const:
const \
            % endif
= ${function.globalname};
        % endif
    % endfor
}
% endif

void ${obj.filename}()
{
% for scope in obj.scopes:
    % if not scope.globalname == '::':
    std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scopename(scope)}");
    boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
    boost::python::scope().attr("${obj.scopename(scope)}") = ${scope.localname + '_' + scope.hash}_module;
    boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;
    % endif
% endfor
% for function in obj.functions:
    boost::python::def("${obj.fctname(function)}", \
    % if function.is_overloaded:
autowig::${function.localname}_${function.hash}\
    % else:
${function.globalname}\
    % endif
    % if function.return_value_policy:
, ${function.return_value_policy}\
    % endif
);
% endfor
}""")

    def __init__(self, filename, *scopes, **kwargs):
        super(BoostPythonExportFunctionsTemplate, self).__init__(filename, *scopes, **kwargs)
        self.functions = kwargs.pop('functions')

    @property
    def headers(self):
        headers = dict()
        for function in self.functions:
            header = function.header
            if not header is None:
                headers[header.globalname] = header
            if not isinstance(function.result_type.target, FundamentalTypeProxy):
                header = function.result_type.target.header
                if not header is None:
                    headers[header.globalname] = header
            for parameter in function.parameters:
                if not isinstance(parameter.type.target, FundamentalTypeProxy):
                    header = parameter.type.target.header
                    if not header is None:
                        headers[header.globalname] = header
        return [header for filename, header in sorted(headers.items())]

class BoostPythonExportClassTemplate(BoostPythonExportTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor

% if any(method.is_overloaded for method in obj.cls.methods() if method.access == 'public'):
namespace autowig
{
    % for method in obj.cls.methods():
        % if method.access == 'public' and method.is_overloaded:
    ${method.result_type.globalname} (${obj.cls.globalname.replace('class ', '').replace('struct ', '').replace('union ', '')}::*${method.localname}_${method.hash})(${", ".join(parameter.type.globalname for parameter in method.parameters)})\
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
}
% endif

void ${obj.filename}()
{
% for scope in obj.scopes:
    % if not scope.globalname == '::':
    std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scopename(scope)}");
    boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
    boost::python::scope().attr("${obj.scopename(scope)}") = ${scope.localname + '_' + scope.hash}_module;
    boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;
    % endif
% endfor
    boost::python::class_< ${obj.cls.globalname}, ${obj.cls.globalname} *\
    % if any(base.access == 'public' for base in obj.cls.bases()):
, boost::python::bases< ${", ".join(base.globalname for base in obj.cls.bases() if base.access == 'public')} >\
    % endif
    % if not obj.cls.is_copyable:
, boost::noncopyable\
    % endif
 >("${obj.clsname(obj.cls)}", boost::python::no_init)\
    % if not obj.cls.is_abstract:
        % for constructor in obj.cls.constructors:
            % if constructor.access == 'public':

        .def(boost::python::init< ${", ".join(parameter.type.globalname for parameter in constructor.parameters)} >())\
            % endif
        % endfor
    % endif
    % for method in obj.cls.methods():
        % if method.access == 'public':
            % if not hasattr(method, 'as_constructor') or not method.as_constructor:

        .def("${obj.mtdname(method)}", \
                % if method.is_overloaded:
autowig::${method.localname}_${method.hash}\
                % else:
                    % if not method.is_static:
&\
                    % endif
${method.globalname}\
                % endif
                % if method.return_value_policy:
, ${method.return_value_policy}\
                % endif
)\
            % else:

        .def("__init__", boost::python::make_constructor(\
                % if method.is_overloaded:
${method.localname}_${method.hash}
                % else:
${method.globalname}\
))\
                % endif
            % endif
        % endif
    % endfor
    % for field in obj.cls.fields():
        % if field.access == 'public':
            % if field.type.is_const:

        .def_readonly\
            % else:

        .def_readwrite\
            % endif
("${field.localname}", \
            % if not field.is_static:
&\
            % endif
${field.globalname})\
        % endif
    % endfor
;
}""")

    def __init__(self, filename, *scopes, **kwargs):
        super(BoostPythonExportClassTemplate, self).__init__(filename, *scopes, **kwargs)
        self.cls = kwargs.pop('cls')

    @property
    def headers(self):
        headers = dict()
        header = self.cls.header
        if not header is None:
            headers[header.globalname] = header
        for field in self.cls.fields():
            if field.access == 'public':
                header = field.header
                if not header is None:
                    headers[header.globalname] = header
                if not isinstance(field.type.target, FundamentalTypeProxy):
                    header = field.type.target.header
                    if not header is None:
                        headers[header.globalname] = header
        for method in self.cls.methods():
            if method.access == 'public':
                if not isinstance(method.result_type.target, FundamentalTypeProxy):
                    header = method.result_type.target.header
                    if not header is None:
                        headers[header.globalname] = header
                for parameter in method.parameters:
                    if not isinstance(parameter.type.target, FundamentalTypeProxy):
                        header = parameter.type.target.header
                        if not header is None:
                            headers[header.globalname] = header
        for constructor in self.cls.constructors:
            if constructor.access == 'public':
                for parameter in constructor.parameters:
                    if not isinstance(parameter.type.target, FundamentalTypeProxy):
                        header = parameter.type.target.header
                        if not header is None:
                            headers[header.globalname] = header
        return [header for filename, header in sorted(headers.items())]

class BoostPythonExportClassBoostSharedPtrTemplate(BoostPythonExportClassTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>
#include <boost/shared_ptr.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor

% if any(method.is_overloaded for method in obj.cls.methods() if method.access == 'public'):
namespace autowig
{
    % for method in obj.cls.methods():
        % if method.access == 'public' and method.is_overloaded:
    ${method.result_type.globalname} (${obj.cls.globalname.replace('class ', '').replace('struct ', '').replace('union ', '')}::*${method.localname}_${method.hash})(${", ".join(parameter.type.globalname for parameter in method.parameters)})\
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
}
% endif

void ${obj.filename}()
{
% for scope in obj.scopes:
    % if not scope.globalname == '::':
    std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scopename(scope)}");
    boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
    boost::python::scope().attr("${obj.scopename(scope)}") = ${scope.localname + '_' + scope.hash}_module;
    boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;
    % endif
% endfor
    boost::python::class_< ${obj.cls.globalname}, boost::shared_ptr< ${obj.cls.globalname} >\
    % if any(base.access == 'public' for base in obj.cls.bases()):
, boost::python::bases< ${", ".join(base.globalname for base in obj.cls.bases() if base.access == 'public')} >\
    % endif
    % if not obj.cls.is_copyable:
, boost::noncopyable\
    % endif
 >("${obj.cls.localname}", boost::python::no_init)\
    % if not obj.cls.is_abstract:
        % for constructor in obj.cls.constructors:
            % if constructor.access == 'public':

        .def(boost::python::init< ${", ".join(parameter.type.globalname for parameter in constructor.parameters)} >())\
            % endif
        % endfor
    % endif
    % for method in obj.cls.methods():
        % if method.access == 'public':
            % if not hasattr(method, 'as_constructor') or not method.as_constructor:

        .def("${obj.mtdname(method)}", \
                % if method.is_overloaded:
autowig::${method.localname}_${method.hash}\
                % else:
                    % if not method.is_static:
&\
                    % endif
${method.globalname}\
                % endif
                % if method.return_value_policy:
, ${method.return_value_policy}\
                % endif
)\
            % else:

        .def("__init__", boost::python::make_constructor(\
                % if method.is_overloaded:
${method.localname}_${method.hash}
                % else:
${method.globalname}\
))\
                % endif
            % endif
        % endif
    % endfor
    % for field in obj.cls.fields():
        % if field.access == 'public':
            % if field.type.is_const:

        .def_readonly\
            % else:

        .def_readwrite\
            % endif
("${field.localname}", \
            % if not field.is_static:
&\
            % endif
${field.globalname})\
        % endif
    % endfor
;
}""")

class BoostPythonFileProxy(FileProxy):

    export = True

    language = 'c++'

    template = Template("""\
#include <boost/python.hpp>

% for export in obj.enum_constants:
void ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.enums:
void ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.variables:
void ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.functions:
void ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.classes:
void ${export.localname.replace(obj.suffix, '')}();
% endfor

BOOST_PYTHON_MODULE(_${obj.localname.replace(obj.suffix, '')})
{
% for export in obj.enum_constants:
    ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.enums:
    ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.variables:
    ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.functions:
    ${export.localname.replace(obj.suffix, '')}();
% endfor
% for export in obj.classes:
    ${export.localname.replace(obj.suffix, '')}();
% endfor
}""")

    @property
    def _content(self):
        return str(self.template.render(obj=self))

    def add_enum_constants(self, filename):
        filenode = self._asg.add_file(filename, language='c++')
        self._enum_constants += [filenode.id]

    def add_enum(self, filename):
        filenode = self._asg.add_file(filename, language='c++')
        self._enums += [filenode.id]

    def add_variable(self, filename):
        filenode = self._asg.add_file(filename, language='c++')
        self._variables += [filenode.id]

    def add_functions(self, filename):
        filenode = self._asg.add_file(filename, language='c++')
        self._functions += [filenode.id]

    def add_class(self, filename, depth):
        if not isinstance(depth, int):
            raise TypeError('\'depth\' parameter')
        if not depth >= 0:
            raise ValueError('\'depth\' parameter')
        filenode = self._asg.add_file(filename, language='c++', depth=depth)
        self._classes += [filenode.id]

def get_enum_constants(self):
    return [self._asg[enum_constants] for enum_constants in self._enum_constants]

BoostPythonFileProxy.enum_constants = property(get_enum_constants)

def get_enums(self):
    return [self._asg[enum] for enum in self._enums]

BoostPythonFileProxy.enums = property(get_enums)

def get_variables(self):
    return [self._asg[variable] for variable in self._variables]

BoostPythonFileProxy.variables = property(get_variables)

def get_functions(self):
    return [self._asg[functions] for functions in self._functions]

BoostPythonFileProxy.functions = property(get_functions)

def get_classes(self):
    return sorted([self._asg[cls] for cls in self._classes], key=lambda node: node.depth)

BoostPythonFileProxy.classes = property(get_classes)

def boost_python_candidates(self, pattern):
    for node in self[pattern]:
        if isinstance(node, CodeNodeProxy) and node.export and not node.to_python:
            if isinstance(node, EnumConstantProxy):
                if not isinstance(node.parent, EnumProxy):
                    if not isinstance(node.parent, ClassProxy) or node.access == 'public':
                        yield node
            elif isinstance(node, EnumProxy):
                if not isinstance(node.parent, ClassProxy) or node.access == 'public':
                    yield node
            elif isinstance(node, VariableProxy):
                if not isinstance(node, FieldProxy) and not isinstance(node.parent, (ConstructorProxy, FunctionProxy)):
                    yield node
            elif isinstance(node, FunctionProxy):
                if not isinstance(node, MethodProxy):
                    yield node
            elif isinstance(node, ClassProxy):
                if not isinstance(node.parent, ClassProxy) or node.access == 'public':
                    yield node

AbstractSemanticGraph.boost_python_candidates = boost_python_candidates
del boost_python_candidates

def _add_boost_python_module(self, filename, proxy=BoostPythonFileProxy, **kwargs):
    """
    """
    modulenode = self.add_file(filename, proxy=proxy,
            _is_protected=False)
    if not '_enum_constants' in self._nodes[modulenode.id]:
        self._nodes[modulenode.id]['_enum_constants'] = []
    if not '_enums' in self._nodes[modulenode.id]:
        self._nodes[modulenode.id]['_enums'] = []
    if not '_variables' in self._nodes[modulenode.id]:
        self._nodes[modulenode.id]['_variables'] = []
    if not '_functions' in self._nodes[modulenode.id]:
        self._nodes[modulenode.id]['_functions'] = []
    if not '_classes' in self._nodes[modulenode.id]:
        self._nodes[modulenode.id]['_classes'] = []
    return modulenode

AbstractSemanticGraph._add_boost_python_module = _add_boost_python_module
del _add_boost_python_module

def boost_python_module(self, filename, pattern, force=False, remove=True, **kwargs):
    """
    {
        E [label="Export\nobject", shape="flowchart.condition"];
        M [label="Wrapper\nmodified", shape="flowchart.condition"];
        D [label="Wrapper on disk", shape="flowchart.condition"];
        WM [label="Missing wrapper", shape="flowchart.terminator", color="red"];
        WRG [label="Rewriting\nwrapper", shape="flowchart.terminator", color="red"];
        RG [label="Regenerate wrapper\n content"];
        G [label="Generate wrapper\n content"];
        F [label="Force\nrewriting", shape="flowchart.condition"];
        L [label="Load wrapper\ncontent"];
        RL [label="Reload wrapper\ncontent"];
        WRL [label="Reload\nwrapper", shape="flowchart.terminator", color="red"];
    }
    """
    modulenode = self._add_boost_python_module(filename, **kwargs)
    _enum_constants = self._nodes[modulenode.id]['_enum_constants']
    _enums = self._nodes[modulenode.id]['_enums']
    _variables = self._nodes[modulenode.id]['_variables']
    _functions = self._nodes[modulenode.id]['_functions']
    _classes = self._nodes[modulenode.id]['_classes']
    suffix = modulenode.suffix
    directory = modulenode.parent.globalname
    enum_constants = dict()
    enums = dict()
    variables = dict()
    functions = dict()
    classes = dict()
    for node in self.boost_python_candidates(pattern):
        if isinstance(node, EnumConstantProxy):
            node.to_python = True
            filename = to_path(node.parent.globalname)
            if filename in enum_constants:
                enum_constants[filename]['constants'].append(node)
            else:
                enum_constants[filename] = dict(scopes = node.ancestors,
                        constants=[node])
        elif isinstance(node, EnumProxy):
            node.to_python = True
            enums[to_path(node.globalname)] = node
        elif isinstance(node, VariableProxy):
            node.to_python = True
            variables[to_path(node.globalname)] = node
        elif isinstance(node, FunctionProxy):
            node.to_python = True
            filename = to_path(node.globalname)
            if filename in functions:
                functions[filename]['functions'].append(node)
            else:
                functions[filename] = dict(scopes = node.ancestors,
                        functions=[node])
        elif isinstance(node, ClassProxy):
            node.to_python = True
            if isinstance(node, ClassTemplateSpecializationProxy):
                classes[to_path(remove_templates(node.globalname) + '_' + node.hash)] = node
            else:
                classes[to_path(node.globalname)] = node
        else:
            raise NotImplementedError()
    database = anydbm.open(directory+kwargs.get('database', '.autowig.db'), 'c')
    filenames = set()
    include = kwargs.get('include', None)
    template = kwargs.get('enum_constants', BoostPythonExportEnumConstantsTemplate)
    for filename in enum_constants:
        filenode = self.add_file(directory+'export_enum_constants_'+filename+suffix, language='c++', export=True, _is_protected=False)
        filenames.add(filenode.localname)
        if filenode.on_disk:
            if filenode.localname in database:
                if database[filenode.localname] == filenode.md5() or force:
                    filenode.content = str(template(filenode.localname.replace(filenode.suffix, '').replace(filenode.suffix, ''), *enum_constants[filename]['scopes'],
                        constants=enum_constants[filename]['constants'],
                        include=include))
                    database[filenode.localname] = filenode.md5()
                    if force:
                        warnings.warn('\'' + filenode.globalname + '\': rewritten', UserWarning)
                else:
                    warnings.warn('\'' + filenode.globalname + '\': not written', UserWarning)
        else:
            filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *enum_constants[filename]['scopes'],
                        constants=enum_constants[filename]['constants'],
                        include=include))
            database[filenode.localname] = filenode.md5()
        _enum_constants.append(filenode.id)
    template = kwargs.get('enum', BoostPythonExportEnumTemplate)
    for filename, enum in enums.iteritems():
        filenode = self.add_file(directory+'export_enum_'+filename+suffix, language='c++', export=True, _is_protected=False)
        filenames.add(filenode.localname)
        if filenode.on_disk:
            if filenode.localname in database:
                if database[filenode.localname] == filenode.md5() or force:
                    filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *enum.ancestors,
                        enum=enum,
                        include=include))
                    database[filenode.localname] = filenode.md5()
                    if force:
                        warnings.warn('\'' + filenode.globalname + '\': rewritten', UserWarning)
                else:
                    warnings.warn('\'' + filenode.globalname + '\': not written', UserWarning)
        else:
            filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *enum.ancestors,
                enum=enum,
                include=include))
            database[filenode.localname] = filenode.md5()
        _enums.append(filenode.id)
    template = kwargs.get('variable', BoostPythonExportVariableTemplate)
    for filename, variable in variables.iteritems():
        filenode = self.add_file(directory+'export_variable_'+filename+suffix, language='c++', export=True, _is_protected=False)
        filenames.add(filenode.localname)
        if filenode.on_disk:
            if filenode.localname in database:
                if database[filenode.localname] == filenode.md5() or force:
                    filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *variable.ancestors,
                        variable=variable,
                        include=include))
                    database[filenode.localname] = filenode.md5()
                    if force:
                        warnings.warn('\'' + filenode.globalname + '\': rewritten', UserWarning)
                else:
                    warnings.warn('\'' + filenode.globalname + '\': not written', UserWarning)
        else:
            filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *variable.ancestors,
                        variable=variable,
                        include=include))
            database[filenode.localname] = filenode.md5()
        _variables.append(filenode.id)
    template = kwargs.get('functions', BoostPythonExportFunctionsTemplate)
    for filename in functions:
        filenode = self.add_file(directory+'export_functions_'+filename+suffix, language='c++', export=True, _is_protected=False)
        filenames.add(filenode.localname)
        if filenode.on_disk:
            if filenode.localname in database:
                if database[filenode.localname] == filenode.md5() or force:
                    filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *functions[filename]['scopes'],
                        functions=functions[filename]['functions'],
                        include=include))
                    database[filenode.localname] = filenode.md5()
                    if force:
                        warnings.warn('\'' + filenode.globalname + '\': rewritten', UserWarning)
                else:
                    warnings.warn('\'' + filenode.globalname + '\': not written', UserWarning)
        else:
            filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *functions[filename]['scopes'],
                functions=functions[filename]['functions'],
                        include=include))
            database[filenode.localname] = filenode.md5()
        _functions.append(filenode.id)
    template = kwargs.get('cls', BoostPythonExportClassTemplate)
    for filename, cls in classes.iteritems():
        filenode = self.add_file(directory+'export_class_'+filename+suffix, language='c++', export=True, depth=cls.depth, _is_protected=False)
        filenames.add(filenode.localname)
        if filenode.on_disk:
            if filenode.localname in database:
                if database[filenode.localname] == filenode.md5() or force:
                    filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *cls.ancestors,
                        cls=cls,
                        include=include))
                    database[filenode.localname] = filenode.md5()
                    if force:
                        warnings.warn('\'' + filenode.globalname + '\': rewritten', UserWarning)
                else:
                    warnings.warn('\'' + filenode.globalname + '\': not written', UserWarning)
        else:
            filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''), *cls.ancestors,
                cls=cls,
                include=include))
            database[filenode.localname] = filenode.md5()
        _classes.append(filenode.id)
    if remove:
        for filename in database.keys():
            if not filename in filenames:
                filenode = self.add_file(directory + filename, language='c++', export=True, _is_protected=False)
                content = database.pop(filename)
                if content == filenode.md5() or force:
                    filenode.remove()
                else:
                    warnings.warn('\'' + filenode.globalname + '\': not removed', UserWarning)
                    database[filenode] = content
    database.close()
    return modulenode

AbstractSemanticGraph.boost_python_module = boost_python_module
del boost_python_module

#def boost_python(self, pattern='::(.*)', directory='.', module='lib', export_proxy=BoostPythonExportFileProxy, module_proxy=BoostPythonModuleFileProxy, suffix='.cpp'):
#    directory = self.add_directory(directory).globalname
#    nodes = self[pattern]
#    if not isinstance(nodes, list):
#        nodes = [nodes]
#    if re.match('(.*)export_(.*).' + suffix + '$', module):
#        raise ValueError('\'module\' parameter')
#    exported = {node.id for node in itertools.chain(*[export.exports for export in self.files() if isinstance(export, BoostPythonExportFileProxy)])}
#    zeros = len(str(max([node.level for node in nodes if isinstance(node, ClassProxy)])))
#    export = []
#    for node in nodes:
#        if node.traverse and not node.id in exported:
#            export.append(directory + to_path(node.scope.globalname) + os.sep + 'export_')
#            if isinstance(node, EnumConstantProxy) and not hasattr(node, 'access') and not isinstance(node.scope, EnumProxy):
#                export[-1] += 'enum_constants'
#            elif isinstance(node, EnumProxy) and not hasattr(node, 'access'):
#                export[-1] += 'enum_' + to_path(node.localname)
#            elif isinstance(node, VariableProxy) and not hasattr(node, 'access'):
#                export[-1] += 'variable_' + to_path(node.localname)
#            elif isinstance(node, FunctionProxy) and not hasattr(node, 'access'):
#                export[-1] += 'function_' + to_path(node.localname)
#            elif isinstance(node, ClassProxy) and (not hasattr(node, 'access') or node.access == 'public'):
#                export[-1] += 'class_' + str(node.level).zfill(zeros) + '_' + to_path(node.localname)
#            else:
#                export[-1] = None
#            if not export[-1] is None:
#                export[-1] += suffix
#                export[-1] = self.add_file(export[-1], proxy = export_proxy)
#                self._boost_python_edges[export[-1].id] = [node.id]
#            else:
#                export.pop()
#    if any(self[directory].walkfiles('*export_*' + suffix, True)):
#        export.append(self.add_file(directory + module + suffix, proxy=module_proxy, module=module))
#    return export
#
#TEMPLATES = dict()
