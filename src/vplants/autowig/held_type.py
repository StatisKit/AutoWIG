from mako.template import Template
import re

from .asg import AbstractSemanticGraph
from .boost_python import BoostPythonExportClassTemplate

__all__ = []

def boost_python_held_type(self, include, held_type):
    for cls in self.classes():
        if re.match('^'+held_type+'<(.*)>$', cls.globalname):
            cls.to_python = True
    template = "#include <boost/python.hpp>\n"
    if include:
        template += include + "\\"
    template += r"""
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
    boost::python::class_< ${obj.cls.globalname}, """
    if held_type:
        template += held_type + "< ${obj.cls.globalname} >\\"
    else:
        template += '${obj.cls.globalname} *\\'
    template += r"""
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
"""
    if held_type:
        template += r"""    % for base in obj.cls.bases():
        % if base.access == 'public':"""
        template += "\n    boost::python::implicitly_convertible< " + held_type + "< ${obj.cls.globalname} >,  " + held_type +"< ${base.globalname} > >();"
        template += r"""
        % endif
    % endfor
"""
    template += "}"
    BoostPythonExportClassTemplate.template = Template(text = template)

AbstractSemanticGraph.boost_python_held_type = boost_python_held_type
del boost_python_held_type
