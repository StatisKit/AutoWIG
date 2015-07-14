import time
from mako.template import Template
import re
from path import path
import anydbm
import warnings
from operator import attrgetter
from abc import ABCMeta

from .asg import *
from .tools import subclasses, to_path, lower, remove_templates
from .custom_warnings import NotImplementedOperatorWarning, InheritanceWarning, BackEndWarning


def get_to_python(self):
    if not hasattr(self, '_to_python'):
        return False
    else:
        return self._to_python

def set_to_python(self, to_python):
    if to_python:
        self._asg._nodes[self.node]['_to_python'] = True
    else:
        del self._to_python

def del_to_python(self):
    self._asg._nodes[self.node].pop('_to_python', True)

CodeNodeProxy.to_python = property(get_to_python, set_to_python, del_to_python)
del get_to_python, set_to_python, del_to_python


class BoostPythonExportFileProxy(FileProxy):

    language = 'c++'

    hdr = Template(text=r"""\
#include <boost/python.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor""")

    scp = Template(text=r"""\
% for scope in obj.scopes:
    % if not scope.globalname == '::':

        std::string ${scope.localname + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.scope_name(scope)}");
        boost::python::object ${scope.localname + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${scope.localname + '_' + scope.hash}_name.c_str()))));
        boost::python::scope().attr("${obj.scope_name(scope)}") = ${scope.localname + '_' + scope.hash}_module;
        boost::python::scope ${scope.localname + '_' + scope.hash}_scope = ${scope.localname + '_' + scope.hash}_module;\
    % endif
% endfor""")

    cst = Template(text='boost::python::scope().attr("${constant.localname}") = (int)(${constant.globalname});\\')

    enm = Template(text=r"""\
        boost::python::enum_< ${enum.globalname} >("${enum.localname}")\
    % for constant in enum.constants:
        % if constant.traverse:
            .value("${constant.localname}", ${constant.globalname})\
        % endif
    % endfor
;""")

    var = Template(text='boost::python::scope().attr("${variable.localname}") = ${variable.globalname};\\')

    fct = Template(text=r"""\
    % if function.is_overloaded:
        ${function.result_type.globalname} (\
${'::'.join(ancestor.localname for ancestor in function.ancestors)}::*${function.localname}_${function.hash})(${", ".join(parameter.type.globalname for parameter in function.parameters)}) = ${function.globalname};
    % endif
        boost::python::def("${obj.function_name(function)}", \
    % if function.is_overloaded:
${function.localname}_${function.hash}\
    % else:
${function.globalname}\
    % endif
    % if obj.return_value_policy(function):
, ${obj.return_value_policy(function)}\
    % endif
);""")

    cls = Template(text=r"""\
    % for method in cls.methods():
        % if method.access == 'public' and method.is_overloaded:
        ${method.result_type.globalname} (${method.parent.globalname.replace('class ', '').replace('struct ', '').replace('union ', '')}::*${method.localname}_${method.hash})(${", ".join(parameter.type.globalname for parameter in method.parameters)})\
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
        boost::python::class_< ${cls.globalname}, \
    % if obj.held_type(cls):
${obj.held_type(cls)}\
    % else:
${cls.globalname} *\
    % endif
    % if any(base.access == 'public' for base in cls.bases() if base.access == 'public' and base.to_python):
, boost::python::bases< ${", ".join(base.globalname for base in cls.bases() if base.access == 'public' and base.to_python)} >\
    % endif
    % if not cls.is_copyable or cls.is_abstract:
, boost::noncopyable\
    % endif
 >("${obj.class_name(cls)}", boost::python::no_init)\
    % if not cls.is_abstract:
        % for constructor in cls.constructors:
            % if constructor.access == 'public' and constructor.traverse:

            .def(boost::python::init< ${", ".join(parameter.type.globalname for parameter in constructor.parameters)} >())\
            % endif
        % endfor
    % endif
    % for method in cls.methods():
        % if method.access == 'public' and method.traverse:
            % if not hasattr(method, 'as_constructor') or not method.as_constructor:

            .def("${obj.method_name(method)}", \
                % if method.is_overloaded:
${method.localname}_${method.hash}\
                % else:
                    % if not method.is_static:
&\
                    % endif
${method.globalname}\
                % endif
                % if obj.return_value_policy(method):
, ${obj.return_value_policy(method)}\
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
    % for field in cls.fields():
        % if field.access == 'public' and field.traverse:
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
;\
    % if obj.held_type(cls) and any(base.access == 'public' for base in cls.bases() if base.access == 'public' and base.to_python):
        % for bse in cls.bases():
            % if bse.access == 'public' and bse.to_python:

            boost::python::implicitly_convertible< ${obj.held_type(cls)}, ${obj.held_type(bse)} >();\
            % endif
        % endfor
    % endif""")

    def __init__(self, asg, node):
        if not hasattr(asg, '_boost_python_export_edges'):
            asg._boost_python_export_edges = dict()
        if not node in asg._boost_python_export_edges:
            asg._boost_python_export_edges[node] = []
        super(BoostPythonExportFileProxy, self).__init__(asg, node)

    def add_wrap(self, wrap):
        self._asg._boost_python_export_edges[self.node].append(wrap.node)

    @property
    def wraps(self):
        wraps = [self._asg[wrap] for wrap in self._asg._boost_python_export_edges[self.node]]
        return [wrap for wrap in wraps if not isinstance(wrap, ClassProxy) if wrap.to_python] + sorted([wrap for wrap in wraps if isinstance(wrap, ClassProxy) and wrap.to_python], key = lambda cls: cls.depth)

    @property
    def is_empty(self):
        return not any(wrap.to_python for wrap in self.wraps)

    @property
    def content(self):
        if self.is_empty:
            filepath = path(self.globalname)
            if filepath.exists():
                return "".join(filepath.lines())
            else:
                return ""
        else:
            content = self.hdr.render(obj=self)
            content += '\n\nvoid ' + self.localname.replace(self.suffix, '()') + '\n{'
            content += self.scp.render(obj=self)
            for arg in self.wraps:
                if isinstance(arg, EnumConstantProxy):
                    content += '\n' + self.cst.render(obj=self, constant=arg)
                elif isinstance(arg, EnumProxy):
                    content += '\n' + self.enm.render(obj=self, enum=arg)
                elif isinstance(arg, VariableProxy):
                    content += '\n' + self.var.render(obj=self, variable=arg)
                elif isinstance(arg, FunctionProxy):
                    content += '\n' + self.fct.render(obj=self, function=arg)
                elif isinstance(arg, ClassProxy):
                    content += '\n' + self.cls.render(obj=self, cls=arg)
                else:
                    raise NotImplementedError(arg.__class__.__name__)
            content += '\n}'
            return content

    @property
    def depth(self):
        if self.is_empty:
            return 0
        else:
            wrap = self.wraps[-1]
            if isinstance(wrap, ClassProxy):
                return wrap.depth
            else:
                return 0

    @property
    def headers(self):
        #white = self.wraps
        #headers = []
        #while len(white) > 0:
        #    node = white.pop()
        #    if not node.header is None:
        #        headers.append(node.header)
        #    if isinstance(node, ClassTemplateSpecializationProxy):
        #        white.extend([template.target for template in node.templates])
        #return headers
        #headers = dict()
        #for wrap in self.wraps:
        #    if not wrap.header is None:
        #        headers[wrap.header.node] = wrap.header
        #    if isinstance(wrap, ClassTemplateSpecializationProxy):
        #        for template in wrap.templates:
        #            if not template.header is None:
        #                headers[template.header.node] = template.header
        #return headers.values()
        return self._asg.headers(*self.wraps)

    @property
    def scopes(self):
        ancestors = list(self.wraps[0].ancestors)
        for arg in self.wraps[1:]:
            for index, ancestor in enumerate(arg.ancestors):
                if index >= len(ancestors):
                    ancestors = ancestors[:index]
                    break
                elif not ancestors[index] == ancestor:
                    ancestors = ancestors[:index]
                    break
        return ancestors

    def return_value_policy(self, function):
        result_type = function.result_type
        if result_type.is_reference or result_type.is_pointer:
            return_value_policy = 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        else:
            return_value_policy = None
        return return_value_policy

    def scope_name(self, scope):
        if isinstance(scope, ClassProxy):
            return '_' + lower(scope.localname)
        else:
            return lower(scope.localname)

    def function_name(self, function):
        return lower(function.localname)

    def method_name(self, method):
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
            return self.function_name(method)

    def class_name(self, cls):
        if isinstance(cls, ClassTemplateSpecializationProxy):
            return remove_templates(cls.localname) + '_' + cls.hash
        else:
            return cls.localname

    def _include(self, header):
        return '<' + re.sub('(.*)include/(.*)', r'\2', header.globalname) + '>'

    def include(self, header):
        if isinstance(header, basestring):
            if header.startswith('#include') or header.startswith('extern '):
                return header
            else:
                return '#include ' + header
        if header.language == 'c++' or header.language is None:
            return "#include " + self._include(header)
        elif header.language == 'c':
            return "extern \"C\" { #include " + self._include(header) + "}"

    _held_type = None

    def held_type(self, cls):
        if self._held_type is None:
            return None
        else:
            return self._held_type + '< ' + cls.globalname + ' >'

def boost_python_exports(self, pattern=None):
    class _MetaClass(object):
        __metaclass__ = ABCMeta
    _MetaClass.register(BoostPythonExportFileProxy)
    metaclass = _MetaClass
    return self.nodes(pattern=pattern, metaclass=metaclass)

AbstractSemanticGraph.boost_python_exports = boost_python_exports
del boost_python_exports

class BoostPythonModuleFileProxy(FileProxy):

    language = 'c++'

    body = Template("""\
#include <boost/python.hpp>

% for export in obj.exports:
void ${export.localname.replace(export.suffix, '()')};
% endfor

BOOST_PYTHON_MODULE(_${obj.localname.replace(obj.suffix, '')})
{
% for export in obj.exports:
    ${export.localname.replace(export.suffix, '')}();
% endfor
}""")

    def __init__(self, asg, node):
        if not hasattr(asg, '_boost_python_module_edges'):
            asg._boost_python_module_edges = dict()
        if not node in asg._boost_python_module_edges:
            asg._boost_python_module_edges[node] = set()
        super(BoostPythonModuleFileProxy, self).__init__(asg, node)

    @property
    def content(self):
        return str(self.body.render(obj=self))

    #def write(self, force=False, exports=True):
    #    try:
    #        with warnings.catch_warnings():
    #            warnings.simplefilter('error')
    #            super(BoostPythonModuleFileProxy, self).write(force=force)
    #            if exports:
    #                for export in self.exports:
    #                    try:
    #                        if not export.is_empty:
    #                            export.write(force=force)
    #                    except Warning:
    #                        pass
    #                    except:
    #                        raise
    #                    else:
    #                        if self.database:
    #                            self.database[export.node] = export.md5()
    #    except Warning:
    #        pass
    #    except:
    #        raise

    def add_export(self, filename, proxy=BoostPythonExportFileProxy, **kwargs):
        filenode = self._asg.add_file(filename, proxy=proxy, **kwargs)
        if not filenode.node in self._asg._boost_python_export_edges:
            self._asg._boost_python_export_edges[filenode.node] = []
        if not isinstance(filenode, BoostPythonExportFileProxy) and not 'depth' in kwargs:
            self._asg._nodes[filenode.node]['depth'] = 0
        self._asg._boost_python_module_edges[self.node].add(filenode.node)
        return filenode

    @property
    def exports(self):
        return [export for export in sorted([self._asg[export] for export in self._asg._boost_python_module_edges[self.node]], key = attrgetter('depth')) if not export.is_empty]

    def check_inheritance(self):
        black = set()
        for export in self.exports:
            for cls in self.wraps:
                if isinstance(cls, ClassProxy):
                    black.add(cls.node)
                    for bse in cls.bases():
                        if bse.to_python and not bse.node in black:
                            warnings.warn('Base class \'' + base.globalname + '\' of class \'' + cls.globalname + '\'', InheritanceWarning)

def boost_python_modules(self, pattern=None):
    class _MetaClass(object):
        __metaclass__ = ABCMeta
    _MetaClass.register(BoostPythonModuleFileProxy)
    metaclass = _MetaClass
    return self.nodes(pattern=pattern, metaclass=metaclass)

AbstractSemanticGraph.boost_python_modules = boost_python_modules
del boost_python_modules

def _boost_python_back_end(self, filename=None, *args, **kwargs):
    prev = time.time()
    modulenode = self.add_file(filename, proxy=kwargs.pop('module', BoostPythonModuleFileProxy))
    export = kwargs.pop('export', BoostPythonExportFileProxy)
    include = kwargs.pop('include', None)
    held_type = kwargs.pop('held_type', None)
    if not include is None:
        if not callable(include):
            raise TypeError('\'include\' parameter')
        export._include = include
    held_type = kwargs.pop('held_type', None)
    if not held_type is None:
        if not isinstance(held_type, basestring):
            raise TypeError('\'held_type\' parameter')
        export._held_type = held_type
        self._held_types.add(held_type)
    self._compute_held_types()
    suffix = modulenode.suffix
    directory = modulenode.parent.globalname
    for node in self.nodes(pattern=kwargs.pop('pattern', None), metaclass=kwargs.pop('metaclass', None)):
        if node.traverse and isinstance(node, CodeNodeProxy) and not node.to_python:
            if isinstance(node, EnumConstantProxy):
                parent = node.parent
                if not isinstance(parent, (EnumProxy, ClassProxy)) or isinstance(parent, ClassProxy) and node.access == 'public':
                    node.to_python = True
                    exportnode = modulenode.add_export(directory + 'export_enum_constants_' + to_path(node.parent) + suffix, proxy = export)
                    exportnode.add_wrap(node)
            elif isinstance(node, EnumProxy):
                parent = node.parent
                if not isinstance(parent, ClassProxy) or node.access == 'public':
                    node.to_python = True
                    exportnode = modulenode.add_export(directory + 'export_enum_' + to_path(node) + suffix, proxy = export)
                    exportnode.add_wrap(node)
            elif isinstance(node, VariableProxy):
                parent = node.parent
                if not isinstance(parent, (ClassProxy, FunctionProxy)):
                    node.to_python = True
                    exportnode = modulenode.add_export(directory + 'export_variable_' + to_path(node) + suffix, proxy = export)
                    exportnode.add_wrap(node)
            elif isinstance(node, FunctionProxy) and not isinstance(node, MethodProxy):
                node.to_python = True
                exportnode = modulenode.add_export(directory + 'export_function_' + to_path(node) + suffix, proxy = export)
                exportnode.add_wrap(node)
            elif isinstance(node, ClassProxy):
                if not isinstance(node, ClassTemplateSpecializationProxy) or not node.as_held_type:
                    parent = node.parent
                    if not isinstance(parent, ClassProxy) or node.access == 'public':
                        node.to_python = True
                        exportnode = modulenode.add_export(directory + 'export_class_' + to_path(node) + suffix, proxy = export)
                        exportnode.add_wrap(node)
    curr = time.time()
    diagnostic = BackEndDiagnostic(self)
    diagnostic.elapsed = curr - prev
    diagnostic._files = [modulenode.node] + [exportnode.node for exportnode in modulenode.exports]
    if kwargs.pop('on_disk', True):
        database = kwargs.pop('database', None)#'.autowig.db')
        if database is None:
            modulenode.write()
            for exportnode in modulenode.exports:
                exportnode.write()
        else:
            raise NotImplementedError()
    if kwargs.pop('check', True):
        for fdt in subclasses(FundamentalTypeProxy):
            if isinstance(fdt.node, basestring) and fdt.node in self:
                self[fdt.node].to_python = True
        for nsp in self.namespaces():
            for var in nsp.variables():
                if var.to_python:
                    if not var.type.target.to_python:
                        warnings.warn(str(var.type.target.node), BackEndWarning)
            for fct in nsp.functions():
                if fct.to_python:
                    if not fct.result_type.target.to_python:
                        warnings.warn(str(fct.result_type.target.node), BackEndWarning)
                    for prm in fct.parameters:
                        if not prm.type.target.to_python:
                            warnings.warn(str(prm.type.target.node), BackEndWarning)
        for cls in self.classes():
            for bse in cls.bases():
                if bse.access == 'public' and bse.traverse and not bse.to_python:
                    warnings.warn(bse.node, BackEndWarning)
            for ctr in cls.constructors:
                if ctr.access == 'public' and ctr.traverse:
                    for prm in ctr.parameters:
                        if not prm.type.target.to_python:
                            warnings.warn(str(prm.type.target.node), BackEndWarning)
            for fld in cls.fields():
                if fld.access == 'public' and fld.traverse and not flt.type.target.to_python:
                    warnings.warn(str(fld.type.target.node), BackEndWarning)
            for mtd in cls.methods():
                if mtd.access == 'public' and mtd.traverse:
                    if not mtd.result_type.target.to_python:
                        warnings.warn(str(mtd.result_type.target.node), BackEndWarning)
                    for prm in mtd.parameters:
                        if not prm.type.target.to_python:
                            warnings.warn(str(prm.type.target.node), BackEndWarning)
    return diagnostic

AbstractSemanticGraph._boost_python_back_end = _boost_python_back_end
del _boost_python_back_end

def get_database(self):
    if hasattr(self, '_database'):
        return self._database
    else:
        return None

def set_database(self, database):
    self._asg._nodes[self.node]['_database'] = anydbm.open(str(self.parent) + database, 'c')

def del_database(self):
    if self.database:
        self.database.close()
        self._asg._nodes[self.node].pop('_database')

BoostPythonModuleFileProxy.database = property(get_database, set_database, del_database)
del get_database, set_database, del_database

from .back_end import BackEndDiagnostic
