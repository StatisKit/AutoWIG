import anydbm

from .asg import AbstractSemanticGraph
from .boost_python import BoostPythonExportClassTemplate

class BoostPythonExportExceptionTemplate(BoostPythonExportClassTemplate):

    template = Template(text=r"""\
#include <boost/python.hpp>
% for header in obj.headers:
${obj.include(header)}
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
    boost::python::class_< ${obj.cls.globalname}\
    % if obj.cls.smart_pointer:
, ${obj.cls.smart_pointer}\
    % else:
, ${obj.cls.globalname}*\
    % endif
    % if any(base.access == 'public' for base in obj.cls.bases()):
, boost::python::bases< ${", ".join(base.globalname for base in obj.cls.bases() if base.access == 'public')} >\
    % endif
    % if obj.cls.is_abstract or not obj.cls.is_copyable:
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

        .def("${obj.methodname(method)}", \
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
    % if obj.cls.smart_pointer:
        % for base in obj.cls.bases():
            % if base.access == 'public':
        boost::python::implicitly_convertible< ${obj.cls.smart_pointer}, ${base.smart_pointer} >();
            % endif
        % endfor
    % endif
}""")

    def get_name(self, exception):
        index = 0
        name = ''
        while index < len(exception):
            if exception[index] == '_':
                index += 1
                name += exception[index].upper()
            else:
                name += exception[index]
            index += 1
        return name

    @property
    def headers(self):
        headers = dict()
        header = self.cls.header
        if not header is None:
            headers[header.globalname] = header
        for field in self.cls.fields():
            header = field.header
            if not header is None:
                headers[header.globalname] = header
            header = field.type.target.header
            if not header is None:
                headers[header.globalname] = header
        for method in self.cls.methods():
            header = method.result_type.target.header
            if not header is None:
                headers[header.globalname] = header
            for parameter in method.parameters:
                header = parameter.type.target.header
                if not header is None:
                    headers[header.globalname] = header
        for constructor in self.cls.constructors:
            for parameter in constructor.parameters:
                header = parameter.type.target.header
                if not header is None:
                    headers[header.globalname] = header
        return [header for filename, header in sorted(headers.items())]

builtin_exceptions = []
front = [BaseException]
while len(front_exceptions) > 0:
    builtin_exceptions.append(front.pop())
    front.extend(builtin_exceptions[-1].__subclasses__())
builtin_exceptions = {exception.__name__ for exception in builtin_exceptions}

def boost_python_exception(self, filename, pattern, force=False, **kwargs):
    """
    """
    modulenode = self._add_boost_python_module(filename, **kwargs)
    _classes = self._nodes[modulenode.id]['_classes']
    suffix = modulenode.suffix
    directory = modulenode.parent.globalname
    database = anydbm.open(directory+kwargs.get('database', '.autowig.db'), 'c')
    if 'class ::std::exception' in self:
        candidates = [inheritor for self['class ::std::exception'].inheritors(True) if re.match(pattern, inheritor.globalname)]
    else:
        candidates = []
    _builtin_exceptions = []
    template = dict.pop(kwargs, 'template', BoostPythonExportExceptionTemplate)
    for node in candidates:
        if template.compute_name(node.localname) in builtin_exceptions:
            _builtin_exceptions.append(node)
        else:
            filenode = self.add_file(directory + 'export_class_' + to_path(node.globalname) + suffix, language='c++', export=True, _is_protected=False)
            if filenode.on_disk:
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
                filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''),
                    *node.ancestors, cls=cls, include=include))
            database[filenode.localname] = filenode.md5()
            _classes.append(filenode.id)
    template = dict.pop(kwargs, 'template', BoostPythonExportBuiltinExceptionTemplate)
    for node in _builtin_exceptions:
        filenode = self.add_file(directory + 'export_class_' + to_path(node.globalname) + suffix, language='c++', export=True, _is_protected=False)
            if filenode.on_disk:
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
                filenode.content = str(template(filenode.localname.replace(filenode.suffix, ''),
                    *node.ancestors, cls=cls, include=include))
    database.close()


