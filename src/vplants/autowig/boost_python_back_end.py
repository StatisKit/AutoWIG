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
from .node_path import node_path
from .node_rename import node_rename, PYTHON_OPERATOR, CONST_PYTHON_OPERATOR, NON_CONST_PYTHON_OPERATOR

__all__ = []

CodeNodeProxy.boost_python_export = None

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self._boost_python_export
        if isinstance(boost_python_export, bool):
            return boost_python_export
        else:
            return self.asg[boost_python_export]
    else:
        return True

def set_boost_python_export(self, boost_python_export):
    if not isinstance(boost_python_export, bool):
        raise TypeError('\'boost_python_export\' parameter is not a boolean')
    self.asg._nodes[self.node]['_boost_python_export'] = boost_python_export

def del_boost_python_export(self):
    self.asg._nodes[self.node].pop('_boost_python_export', True)

EnumConstantProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
EnumProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
DestructorProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
ClassProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
ClassTemplateSpecializationProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
del get_boost_python_export, set_boost_python_export

def is_invalid_pointer(edge):
    return edge.nested.is_pointer or edge.is_pointer and isinstance(edge.target, FundamentalTypeProxy)

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        return self._boost_python_export
    else:
        return not is_invalid_pointer(self.type)

def set_boost_python_export(self, boost_python_export):
    if not isinstance(boost_python_export, bool):
        raise TypeError('\'boost_python_export\' parameter is not a boolean')
    if boost_python_export:
        del self.boost_python_export
        if not self.boost_python_export:
            raise ValueError('\'boost_python_export\' parameter cannot be set to \'' + str(boost_python_export) +'\'')
    self.asg._nodes[self.node]['_boost_python_export'] = boost_python_export

VariableProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)
TypedefProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)

del get_boost_python_export

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self._boost_python_export
        if isinstance(boost_python_export, bool):
            return boost_python_export
        else:
            return self.asg[boost_python_export]
    else:
        if self.localname.startswith('operator'):
            return False
        else:
            return not(is_invalid_pointer(self.result_type) or any(is_invalid_pointer(prm.type) for prm in self.parameters))

FunctionProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)

del get_boost_python_export

def is_valid_operator(node):
    operator = node.localname.strip('operator').strip()
    return operator in PYTHON_OPERATOR or node.is_const and operator in CONST_PYTHON_OPERATOR or not node.is_const and operator in NON_CONST_PYTHON_OPERATOR

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self._boost_python_export
        if isinstance(boost_python_export, bool):
            return boost_python_export
        else:
            return self.asg[boost_python_export]
    else:
        if not(is_invalid_pointer(self.result_type) or any(is_invalid_pointer(prm.type) for prm in self.parameters)):
            if self.localname.startswith('operator'):
                return is_valid_operator(self)
            else:
                return True
        else:
            return False

MethodProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)

del get_boost_python_export

def get_boost_python_export(self):
    if hasattr(self, '_boost_python_export'):
        boost_python_export = self._boost_python_export
        if isinstance(boost_python_export, bool):
            return boost_python_export
        else:
            return self.asg[boost_python_export]
    else:
        if self.localname.startswith('operator'):
            return False
        else:
            return not any(is_invalid_pointer(prm.type) for prm in self.parameters)

ConstructorProxy.boost_python_export = property(get_boost_python_export, set_boost_python_export, del_boost_python_export)

del get_boost_python_export, set_boost_python_export

del del_boost_python_export

def get_to_python(self):
    if not hasattr(self, '_to_python'):
        return False
    else:
        return self._to_python

def set_to_python(self, to_python):
    if not isinstance(to_python, bool):
        raise TypeError('\'to_python\' parameter')
    if to_python:
        self.asg._nodes[self.node]['_to_python'] = True
    else:
        del self._to_python

def del_to_python(self):
    self.asg._nodes[self.node].pop('_to_python', True)

CodeNodeProxy.to_python = property(get_to_python, set_to_python, del_to_python)
del get_to_python, set_to_python, del_to_python

def get_to_python(self):
    return any([dcl.to_python for dcl in self.declarations()])

NamespaceProxy.to_python = property(get_to_python)
del get_to_python

class BoostPythonExportFileProxy(FileProxy):

    language = 'c++'

    HEADER = Template(text=r"""\
#include <boost/python.hpp>\
% for header in obj.headers:

${obj.include(header)}\
% endfor""")

    SCOPE = Template(text=r"""\
% for scope in obj.scopes:

        std::string ${obj.node_rename(scope, scope=True) + '_' + scope.hash}_name = boost::python::extract< std::string >(boost::python::scope().attr("__name__") + ".${obj.node_rename(scope, scope=True)}");
        boost::python::object ${obj.node_rename(scope, scope=True) + '_' + scope.hash}_module(boost::python::handle<  >(boost::python::borrowed(PyImport_AddModule(${obj.node_rename(scope, scope=True) + '_' + scope.hash}_name.c_str()))));
        boost::python::scope().attr("${obj.node_rename(scope, scope=True)}") = ${obj.node_rename(scope, scope=True) + '_' + scope.hash}_module;
        boost::python::scope ${obj.node_rename(scope, scope=True) + '_' + scope.hash}_scope = ${obj.node_rename(scope, scope=True) + '_' + scope.hash}_module;\
% endfor""")

    CONSTANT = Template(text="""\
            boost::python::scope().attr("${obj.node_rename(constant)}") = (int)(${constant.globalname});\
""")

    ENUM = Template(text=r"""\
        boost::python::enum_< ${enum.globalname} >("${obj.node_rename(enum)}")\
    % for constant in enum.constants:
        % if constant.boost_python_export:

            .value("${obj.node_rename(constant)}", ${constant.globalname})\
        % endif
    % endfor
;""")

    VARIABLE = Template(text="""\
            boost::python::scope().attr("${obj.node_rename(variable)}") = ${variable.globalname};\
""")

    FUNCTION = Template(text=r"""\
    % if function.is_overloaded:
        ${function.result_type.globalname} (\
${'::'.join(ancestor.localname for ancestor in function.ancestors)}::*function_pointer_${function.hash})(${", ".join(parameter.type.globalname for parameter in function.parameters)}) = ${function.globalname};
    % endif
        boost::python::def("${obj.node_rename(function)}", \
    % if function.is_overloaded:
function_pointer_${function.hash}\
    % else:
${function.globalname}\
    % endif
    % if obj.return_value_policy(function):
, ${obj.return_value_policy(function)}\
    % endif
);""")

    CLASS = Template(text=r"""\
    % for method in cls.methods():
        % if method.access == 'public' and method.is_overloaded:
        ${method.result_type.globalname} (${method.parent.globalname.replace('class ', '').replace('struct ', '').replace('union ', '')}::*method_pointer_${method.hash})(${", ".join(parameter.type.globalname for parameter in method.parameters)})\
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
 >("${obj.node_rename(cls)}", boost::python::no_init)\
    % if not cls.is_abstract:
        % for constructor in cls.constructors:
            % if constructor.access == 'public' and constructor.boost_python_export:

            .def(boost::python::init< ${", ".join(parameter.type.globalname for parameter in constructor.parameters)} >())\
            % endif
        % endfor
    % endif
    % for method in cls.methods():
        % if method.access == 'public' and method.boost_python_export:
            % if not hasattr(method, 'as_constructor') or not method.as_constructor:

            .def("${obj.node_rename(method)}", \
                % if method.is_overloaded:
method_pointer_${method.hash}\
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
        % if field.access == 'public' and field.boost_python_export:
            % if field.type.is_const:

            .def_readonly\
            % else:

            .def_readwrite\
            % endif
("${obj.node_rename(field)}", \
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

    def add_wrap(self, wrap):
        if len(self._wraps) == 0 or self.scope.globalname == wrap.parent.globalname:
            self.asg._nodes[self.node]['_wraps'].append(wrap.node)
            wrap.to_python = True
            self.asg._nodes[wrap.node]['_boost_python_export'] = self.node
        else:
            raise ValueError('\'wrap\' parameter has scope \'' + wrap.parent.globalname + '\' instead of \'' + self.scope.globalname + '\'')

    @property
    def wraps(self):
        wraps = [self.asg[wrap] for wrap in self._wraps]
        return [wrap for wrap in wraps if not isinstance(wrap, ClassProxy) if wrap.to_python] + sorted([wrap for wrap in wraps if isinstance(wrap, ClassProxy) and wrap.to_python], key = lambda cls: cls.depth)

    @property
    def is_empty(self):
        return not any(wrap.to_python for wrap in self.wraps)

    def write(self, database=None, force=False):
        content = self.content
        self.content = content
        super(BoostPythonExportFileProxy, self).write(database=None, force=False)

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
        return self.asg.headers(*self.wraps)

    @property
    def scope(self):
        return self.asg[self.asg._nodes[self.node]['_wraps'][0]].parent

    @property
    def scopes(self):
        return self.asg[self._wraps[0]].ancestors[1:]

    def return_value_policy(self, function):
        result_type = function.result_type
        if result_type.is_reference or result_type.is_pointer:
            return_value_policy = 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        else:
            return_value_policy = None
        return return_value_policy

    def include(self, header):
        if header.language == 'c':
            return 'extern "C" { #include <' + self.asg.include_path(header) + '> }'
        else:
            return '#include <' + self.asg.include_path(header) + '>'

    _held_type = None

    def held_type(self, cls):
        if self._held_type is None:
            return None
        else:
            return self._held_type + '< ' + cls.globalname + ' >'

    def node_rename(self, node, scope=False):
        return node_rename(node, scope=scope)

def get_content(self):
    if not hasattr(self, '_content') or self._content == "":
        if self.is_empty:
            filepath = path(self.globalname)
            if filepath.exists():
                return "".join(filepath.lines())
            else:
                return ""
        else:
            content = self.HEADER.render(obj=self)
            content += '\n\nvoid ' + self.prefix + '()\n{'
            content += self.SCOPE.render(obj=self)
            for arg in self.wraps:
                if isinstance(arg, EnumConstantProxy):
                    content += '\n' + self.CONSTANT.render(obj=self, constant=arg)
                elif isinstance(arg, EnumProxy):
                    content += '\n' + self.ENUM.render(obj=self, enum=arg)
                elif isinstance(arg, VariableProxy):
                    content += '\n' + self.VARIABLE.render(obj=self, variable=arg)
                elif isinstance(arg, FunctionProxy):
                    content += '\n' + self.FUNCTION.render(obj=self, function=arg)
                elif isinstance(arg, ClassProxy):
                    content += '\n' + self.CLASS.render(obj=self, cls=arg)
                elif isinstance(arg, TypedefProxy):
                    continue
                else:
                    raise NotImplementedError(arg.__class__.__name__)
            content += '\n}'
            return content
    else:
        return self._content

def set_content(self, content):
    self.asg._nodes[self.node]['_content'] = content

def del_content(self):
    self.asg._nodes[self.node].pop('_content', False)

BoostPythonExportFileProxy.content = property(get_content, set_content, del_content)
del get_content, set_content, del_content

def get_boost_python_module(self):
    if hasattr(self, '_boost_python_module'):
        return self.asg[self._boost_python_module]

def set_boost_python_module(self, module):
    self.asg._nodes[self.node]['_boost_python_module'] = module

def del_boost_python_module(self):
    self.asg._nodes[self.node].pop('_boost_python_module', None)

BoostPythonExportFileProxy.boost_python_module = property(get_boost_python_module, set_boost_python_module, del_boost_python_module)
del get_boost_python_module, set_boost_python_module, del_boost_python_module

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

    MODULE = Template("""\
#include <boost/python.hpp>

% for export in obj.boost_python_exports:
void ${export.prefix}();
% endfor

BOOST_PYTHON_MODULE(_${obj.prefix})
{
% for export in obj.boost_python_exports:
    ${export.prefix}();
% endfor
}""")

    SCONSCRIPT = Template("""\
# -*-python-*-

import os

Import("${obj.environment}")

wrapper_${obj.environment} = ${obj.environment}.Clone()

% if not obj.prepend is None:
wrapper_${obj.environment}.Prepend(${',\\n        ' + ' ' * len(obj.environment) + "        ".join(key + " =  [" + ", ".join(value for value in values) + "]" for key, values in obj.prepend.iteritems())})
% endif
% if not obj.prepend_unique is None:
wrapper_${obj.environment}.PrependUnique(${',\\n        ' + ' ' * len(obj.environment) + "        ".join(key + " =  [" + ", ".join(value for value in values) + "]" for key, values in obj.prepend_unique.iteritems())})
% endif
% if not obj.append is None:
wrapper_${obj.environment}.Append(${',\\n        ' + ' ' * len(obj.environment) + "        ".join(key + " =  [" + ", ".join(value for value in values) + "]" for key, values in obj.append.iteritems())})
% endif
% if not obj.append_unique is None:
wrapper_${obj.environment}.AppendUnique(${',\\n        ' + ' ' * len(obj.environment) + "        ".join(key + " =  [" + ", ".join(value for value in values) + "]" for key, values in obj.append_unique.iteritems())})
% endif

sources = ["${'",\\n           "'.join(export.parent.relativename(obj.parent) + export.localname for export in obj.boost_python_exports)}"]
sources.append("${obj.localname}")

target = str(wrapper_${obj.environment}.Dir("${obj.target.relativename(obj.parent)}").srcnode()) + "/_${obj.prefix}"

kwargs = dict()

if os.name == 'nt':
    kwargs['SHLIBSUFFIX'] = '.pyd'
else:
    kwargs['SHLIBSUFFIX'] = '.so'

kwargs['SHLIBPREFIX'] = ''

if wrapper_${obj.environment}['compiler'] == 'msvc' and '8.0' in wrapper_${obj.environment}['MSVS_VERSION']:
    kwargs['SHLINKCOM'] = [wrapper_${obj.environment}['SHLINKCOM'],
    'mt.exe -nologo -manifest ${'${'}TARGET${'}'}.manifest -outputresource:$TARGET;2']

if os.name == 'nt':
    # Fix bug with Scons 0.97, Solved in newer versions.
    wrap = wrapper_${obj.environment}.SharedLibrary(target, sources, **kwargs)
elif os.sys.platform == 'darwin':
    wrap = wrapper_${obj.environment}.LoadableModule(target, sources, LDMODULESUFFIX='.so',
                           FRAMEWORKSFLAGS = '-flat_namespace -undefined suppress', **kwargs)
else:
    wrap = wrapper_${obj.environment}.LoadableModule(target, sources, **kwargs)

Alias("${obj.alias}", wrap)
""")

    IMPORT = Template("""\
% for module in obj.imports:
from ${module.python_path} import ${module.prefix}
% endfor
import _${obj.prefix}
from _${obj.prefix} import *
if hasattr(_${obj.prefix}, '${obj.prefix}'):
    from _${obj.prefix}.${obj.prefix} import *
""")

    SCOPE = Template("""\
% for wrap in export.wraps:
${'.'.join(obj.node_rename(ancestor, scope=True) for ancestor in export.scope.ancestors[1:])}.${obj.node_rename(export.scope)}.${obj.node_rename(wrap)} = ${'.'.join(obj.node_rename(ancestor, scope=True) for ancestor in export.scope.ancestors[1:])}.${obj.node_rename(export.scope, scope=True)}.${obj.node_rename(wrap)}
% endfor""")

    TYPEDEF = Template("""\
${'.'.join(obj.node_rename(ancestor, scope=True) for ancestor in tdf.ancestors[1:])}.${obj.node_rename(tdf)} = ${'.'.join(obj.node_rename(ancestor, scope=True) for ancestor in tdf.type.target.ancestors[1:])}.${obj.node_rename(tdf.type.target)}
""")

    @property
    def python_path(self):
        parent = self.target
        if not parent.globalname + '__init__.py' in self.asg and path(parent.globalname + '__init__.py').exists():
            initnode = self.asg.add_file(parent.globalname + '__init__.py')
            initnode.language = 'py'
        python_path = ''
        while parent.globalname + '__init__.py' in self.asg:
            python_path = parent.localname + '.' + python_path
            parent = parent.parent
            if not parent.globalname + '__init__.py' in self.asg and path(parent.globalname + '__init__.py').exists():
                initnode = self.asg.add_file(parent.globalname + '__init__.py')
                initnode.language = 'py'
        return python_path.rstrip('.')

    @property
    def is_empty(self):
        return len(self._boost_python_exports) == 0

    def write(self, database=None, force=False):
        self.imports = [f.globalname for f in self.imports]
        content = self.content
        self.content = content
        super(BoostPythonModuleFileProxy, self).write(database=database, force=force)

    @property
    def initscript(self):
        initnode = self.asg.add_file(self.target.globalname + '__init__.py')
        initnode.language = 'py'
        return initnode

    @property
    def targetscript(self):
        targetnode = self.asg.add_file(self.target.globalname + self.prefix + '.py')
        targetnode.language = 'py'
        if not hasattr(targetnode, '_content') or targetnode._content == "":
            scopes = set()
            targetnode.content = self.IMPORT.render(obj=self)
            for export in self.boost_python_exports:
                for wrap in export.wraps:
                    if isinstance(wrap, TypedefProxy):
                        export = wrap.type.target.boost_python_export
                        if export and not export is True:
                            targetnode.content += self.TYPEDEF.render(obj=self, tdf=wrap)
                scope = export.scope
                if isinstance(scope, ClassProxy) and not scope.globalname in scopes:
                    targetnode.content += self.SCOPE.render(obj=self, export=export)
                    scopes.add(scope.globalname)
        return targetnode

    @property
    def sconscript(self):
        sconscript = self.asg.add_file(self.parent.globalname + 'SConscript')
        sconscript.language = 'py'
        if not hasattr(sconscript, '_content') or sconscript._content == "":
            sconscript.content = self.SCONSCRIPT.render(obj=self)
        return sconscript

    def add_boost_python_export(self, filename, proxy=BoostPythonExportFileProxy, **kwargs):
        filenode = self.asg.add_file(filename, proxy=proxy, **kwargs)
        if not '_wraps' in self.asg._nodes[filenode.node]:
            self.asg._nodes[filenode.node]['_wraps'] = []
        if not isinstance(filenode, BoostPythonExportFileProxy) and not 'depth' in kwargs:
            self.asg._nodes[filenode.node]['depth'] = 0
        self._boost_python_exports.add(filenode.node)
        self.asg._nodes[filenode.node]['_boost_python_module'] = self.node
        return filenode

    @property
    def boost_python_exports(self):
        return [export for export in sorted([self.asg[export] for export in self._boost_python_exports], key = attrgetter('depth')) if not export.is_empty]

    def node_rename(self, node, scope=False):
        return node_rename(node, scope=scope)

def get_target(self):
    if hasattr(self, '_target'):
        return self.asg[self._target]
    else:
        return self.parent

def set_target(self, target):
    self.asg._nodes[self.node]['_target'] = target

def del_target(self):
    self.asg._nodes[self.node].pop('_target', None)

BoostPythonModuleFileProxy.target = property(get_target, set_target, del_target)
del get_target, set_target, del_target

def get_content(self):
    if not hasattr(self, '_content') or self._content == "":
        if self.is_empty:
            filepath = path(self.globalname)
            if filepath.exists():
                return "".join(filepath.lines())
            else:
                return ""
        else:
            return str(self.MODULE.render(obj=self))
    else:
        return self._content

def set_content(self, content):
    self.asg._nodes[self.node]['_content'] = content

def del_content(self):
    self.asg._nodes[self.node].pop('_content', False)

BoostPythonModuleFileProxy.content = property(get_content, set_content, del_content)
del get_content, set_content, del_content

def get_imports(self):
    if not hasattr(self, '_imports'):
        modules = set()
        for export in self.boost_python_exports:
            for wrap in export.wraps:
                if isinstance(wrap, FunctionProxy):
                    boost_python_export = wrap.result_type.target.boost_python_export
                    if not boost_python_export is None:
                        boost_python_module = boost_python_export.boost_python_module
                        if not boost_python_module is None:
                            modules.add(boost_python_module.globalname)
                    for prm in wrap.parameters:
                        boost_python_export = prm.type.target.boost_python_export
                        if not boost_python_export is None:
                            boost_python_module = boost_python_export.boost_python_module
                            if not boost_python_module is None:
                                modules.add(boost_python_module.globalname)
                elif isinstance(wrap, (VariableProxy, TypedefProxy)):
                    boost_python_export = wrap.type.target.boost_python_export
                    if not boost_python_export is None:
                        boost_python_module = boost_python_export.boost_python_module
                        if not boost_python_module is None:
                            modules.add(boost_python_module.globalname)
                elif isinstance(wrap, ClassProxy):
                    boost_python_export = wrap.boost_python_export
                    if not boost_python_export is None:
                        boost_python_module = boost_python_export.boost_python_module
                        if not boost_python_module is None:
                            modules.add(boost_python_module.globalname)
        if self.globalname in modules:
            modules.remove(self.globalname)
        return [self.asg[module] for module in modules]
    else:
        return self._imports

def set_imports(self, imports):
    self.asg._nodes[self.node]['_imports'] = imports

def del_imports(self):
    self.asg._nodes[self.node].pop('_imports', [])

BoostPythonModuleFileProxy.get_imports = get_imports
BoostPythonModuleFileProxy.imports = property(get_imports, set_imports, del_imports)
del get_imports, set_imports, del_imports

#def get_depth(self):
#    if not hasattr(self, '_depth'):
#        imports = self.imports
#        if len(imports) == 0:
#            return 0
#        else:
#            return max([module.level for module in self.imports])
#    else:
#        return self._depth
#
#def set_depth(self, depth):
#    self.asg._nodes[self.node]['_depth'] = depth
#
#def del_depth(self):
#    self.asg._nodes[self.node].pop('_depth', 0)
#
#BoostPythonModuleFileProxy.depth = property(get_depth, set_depth, del_depth)
#del get_depth, set_depth, del_depth

def get_alias(self):
    if not hasattr(self, '_alias'):
        return 'build'
    else:
        return self._alias

def set_alias(self, alias):
    self.asg._nodes[self.node]['_alias'] = alias

def del_alias(self):
    self.asg._nodes[self.node].pop('_alias', 'build')

BoostPythonModuleFileProxy.alias = property(get_alias, set_alias, del_alias)
del get_alias, set_alias, del_alias

def get_environment(self):
    if not hasattr(self, '_environment'):
        return 'env'
    else:
        return self._environment

def set_environment(self, environment):
    self.asg._nodes[self.node]['_environment'] = environment

def del_environment(self):
    self.asg._nodes[self.node].pop('_environment', 'env')

BoostPythonModuleFileProxy.environment = property(get_environment, set_environment, del_environment)
del get_environment, set_environment, del_environment

def get_prepend(self):
    if hasattr(self, '_prepend'):
        return self._prepend

def set_prepend(self, prepend):
    if not isinstance(prepend, list):
        raise TypeError('\'prepend\' parameter shoud be a list')
    if any(not isinstance(p, basestring) for p in prepend):
        raise ValueError('\'prepend\' parameter contains not basestring instances')
    self.asg._nodes[self.node]['_prepend'] = prepend

def del_prepend(self):
    self.asg._nodes[self.node].pop('_prepend', None)

BoostPythonModuleFileProxy.prepend = property(get_prepend, set_prepend, del_prepend)
del get_prepend, set_prepend, del_prepend

def get_prepend_unique(self):
    if hasattr(self, '_prepend_unique'):
        return self._prepend_unique

def set_prepend_unique(self, prepend_unique):
    if not isinstance(prepend_unique, list):
        raise TypeError('\'prepend_unique\' parameter shoud be a list')
    if any(not isinstance(p, basestring) for p in prepend_unique):
        raise ValueError('\'prepend\' parameter contains not basestring instances')
    self.asg._nodes[self.node]['_prepend_unique'] = prepend_unique

def del_prepend_unique(self):
    self.asg._nodes[self.node].pop('_prepend_unique', None)

BoostPythonModuleFileProxy.prepend_unique = property(get_prepend_unique, set_prepend_unique, del_prepend_unique)
del get_prepend_unique, set_prepend_unique, del_prepend_unique

def get_append(self):
    if hasattr(self, '_append'):
        return self._append

def set_append(self, append):
    if not isinstance(append, list):
        raise TypeError('\'append\' parameter shoud be a list')
    if any(not isinstance(a, basestring) for a in append):
        raise ValueError('\'append\' parameter contains not basestring instances')
    self.asg._nodes[self.node]['_append'] = append

def del_append(self):
    self.asg._nodes[self.node].pop('_append', None)

BoostPythonModuleFileProxy.append = property(get_append, set_append, del_append)
del get_append, set_append, del_append

def get_append_unique(self):
    if hasattr(self, '_append_unique'):
        return self._append_unique

def set_append_unique(self, append_unique):
    if not isinstance(append_unique, list):
        raise TypeError('\'append\' parameter shoud be a list')
    if any(not isinstance(a, basestring) for a in append_unique):
        raise ValueError('\'append\' parameter contains not basestring instances')
    self.asg._nodes[self.node]['_append_unique'] = append_unique

def del_append_unique(self):
    self.asg._nodes[self.node].pop('_append_unique', None)

BoostPythonModuleFileProxy.append_unique = property(get_append_unique, set_append_unique, del_append_unique)
del get_append_unique, set_append_unique, del_append_unique

def boost_python_modules(self, pattern=None):
    class _MetaClass(object):
        __metaclass__ = ABCMeta
    _MetaClass.register(BoostPythonModuleFileProxy)
    metaclass = _MetaClass
    return self.nodes(pattern=pattern, metaclass=metaclass)

AbstractSemanticGraph.boost_python_modules = boost_python_modules
del boost_python_modules

def back_end(asg, filename, **kwargs):
    from vplants.autowig.back_end import BackEndDiagnostic
    prev = time.time()
    for fdt in subclasses(FundamentalTypeProxy):
        if isinstance(fdt.node, basestring) and fdt.node in asg:
            asg[fdt.node].to_python = True
    if 'class ::boost::shared_ptr' in asg:
        for spc in asg['class ::boost::shared_ptr'].specializations(partial=False):
            spc.to_python = True
    if 'class ::std::smart_ptr' in asg:
        for spc in asg['class ::std::smart_ptr'].specializations(partial=False):
            spc.to_python = True
    if filename in asg:
        modulenode = asg[filename]
    else:
        modulenode = asg.add_file(filename, proxy=kwargs.pop('module', BoostPythonModuleFileProxy), _boost_python_exports = set())
        if 'target' in kwargs:
            target = asg.add_directory(kwargs.pop('target'))
            modulenode.target = target.globalname
    export = kwargs.pop('export', BoostPythonExportFileProxy)
    suffix = modulenode.suffix
    directory = modulenode.parent.globalname
    pattern = kwargs.pop('pattern', None)
    for node in asg.nodes(pattern=pattern):
        if isinstance(node, CodeNodeProxy) and node.boost_python_export is True and not node.to_python:
            if isinstance(node, EnumConstantProxy):
                parent = node.parent
                if not isinstance(parent, EnumProxy) and (not isinstance(parent, ClassProxy) or node.access == 'public'):
                    exportnode = modulenode.add_boost_python_export(directory + node_path(node, prefix='export_enum_constants_', suffix=suffix), proxy = export)
                    exportnode.add_wrap(node)
            elif isinstance(node, EnumProxy):
                parent = node.parent
                if not isinstance(parent, ClassProxy) or node.access == 'public':
                    exportnode = modulenode.add_boost_python_export(directory + node_path(node, prefix='export_enum_', suffix=suffix), proxy = export)
                    exportnode.add_wrap(node)
            elif isinstance(node, VariableProxy) and not isinstance(node, FieldProxy):
                exportnode = modulenode.add_boost_python_export(directory + node_path(node, prefix='export_variable_', suffix=suffix), proxy = export)
                exportnode.add_wrap(node)
            elif isinstance(node, FunctionProxy) and not isinstance(node, MethodProxy):
                exportnode = modulenode.add_boost_python_export(directory + node_path(node, prefix='export_function_', suffix=suffix), proxy = export)
                exportnode.add_wrap(node)
            elif isinstance(node, ClassProxy):
                if not isinstance(node, ClassTemplateSpecializationProxy) or not node.is_smart_pointer:
                    parent = node.parent
                    if not isinstance(parent, ClassProxy) or node.access == 'public':
                        exportnode = modulenode.add_boost_python_export(directory + node_path(node, prefix='export_class_', suffix=suffix), proxy = export)
                        exportnode.add_wrap(node)
            elif isinstance(node, TypedefProxy):
                parent = node.parent
                if not isinstance(parent, ClassProxy) or node.access == 'public':
                    exportnode = modulenode.add_boost_python_export(directory + node_path(parent, prefix='export_typedefs_', suffix=suffix), proxy = export)
                    exportnode.add_wrap(node)
    diagnostic = BackEndDiagnostic()
    if kwargs.pop('on_disk', True):
        database = kwargs.pop('database', None)
        modulenode.write(database=database)
        for exportnode in modulenode.boost_python_exports:
            exportnode.write(database=database)
        diagnostic._nodes = [modulenode] + modulenode.boost_python_exports
        if kwargs.pop('initscript', True):
            modulenode.initscript.write(database=database)
            diagnostic._nodes.append(modulenode.initscript)
        if kwargs.pop('targetscript', True):
            modulenode.targetscript.write(database=database)
            diagnostic._nodes.append(modulenode.targetscript)
        if kwargs.pop('sconscript', True):
            modulenode.sconscript.write(database=database)
            diagnostic._nodes.append(modulenode.sconscript)
    curr = time.time()
    diagnostic.elapsed = curr - prev
    return diagnostic

def char_pointer(asg, filename, on_disk=True, **kwargs):
    prev = time.time()
    def is_char_pointer(proxy):
        return proxy.is_pointer and not proxy.nested.is_reference and not proxy.nested.is_pointer and isinstance(proxy.target, CharTypeProxy)
    def is_invalid_pointer(proxy):
        return proxy.nested.is_pointer or proxy.is_pointer and isinstance(proxy.target, FundamentalTypeProxy)
    if not isinstance(filename, basestring):
        raise TypeError('\'filename\' parameter')
    if filename in asg:
        modulenode = asg[filename]
    else:
        modulenode = asg.add_file(filename, proxy=kwargs.pop('module', BoostPythonModuleFileProxy))
    directory = modulenode.parent.globalname
    exportnode = modulenode.add_boost_python_export(directory + 'export_char_pointer_as_std_string.cpp', proxy=FileProxy)
    exportnode.content = ""
    functions = []
    for fct in asg.functions(pattern=kwargs.pop('pattern', None), free=None):
        if fct.boost_python_export and not fct.to_python:
            if is_char_pointer(fct.result_type) and not is_invalid_pointer(fct.resul_type) or any(is_char_pointer(prm.type) for prm in fct.parameters) and not any(is_invalid_pointer(prm.type) for prm in fct.parameters) and all(prm.localname for prm in fct.parameters):
                if isinstance(fct, MethodProxy):
                    parent = fct.parent
                    access = fct.access
                    while access == 'public' and hasattr(parent, 'access'):
                        access = parent.access
                        parent = parent.parent
                    if access == 'public':
                        functions.append(fct)
                else:
                    functions.append(fct)
    for fct in functions:
        rtype = fct.result_type
        if is_char_pointer(rtype):
            rtype = rtype.nested
            rtype._target = '::std::string'
        content = rtype.globalname + ' '
        content += 'char_pointer_to_std_string_' + fct.hash + '('
        if isinstance(fct, MethodProxy) and not fct.is_static:
            parent = fct.parent
            content += parent.globalname + ' const'*fct.is_const + ' * pointer_' + parent.hash + ', '
        for prm in fct.parameters:
            ptype = prm.type
            if is_char_pointer(ptype):
                ptype = ptype.nested
                ptype._target = '::std::string'
            content += ptype.globalname + ' ' + prm.localname +', '
        if content:
            content = content[:-2] + ')\n{\n'
            for prm in fct.parameters:
                ptype = prm.type
                if is_char_pointer(ptype):
                    content += '\t' + ptype.globalname + ' parameter_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::' + str(prm.index))).replace('-', '_') + ' = '
                    if ptype.nested.is_const:
                        content += prm.localname + '.c_str();\n'
                    else:
                        content += ' new char[' + prm.localname + '.length() + 1];\n'
                        content += '\t::std::strcpy(parameter_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::' + str(prm.index))).replace('-', '_') + ', ' + prm.localname + '.c_str());\n'
            rtype = fct.result_type
            if not isinstance(rtype.target, VoidTypeProxy):
                content += '\t' + rtype.globalname + ' result_'
                if is_char_pointer(rtype):
                    content += str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::char')).replace('-', '_')
                else:
                    content += str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname)).replace('-', '_')
                content += ' = '
            else:
                content += '\t'
            if isinstance(fct, MethodProxy) and not fct.is_static:
                content += 'pointer_' + fct.parent.hash + '->' + fct.localname
            else:
                content += fct.globalname
            content += '(' + ', '.join(prm.localname if not is_char_pointer(prm.type) else 'parameter_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::' + str(prm.index))).replace('-', '_') for prm in fct.parameters) + ');\n'
            for prm in fct.parameters:
                ptype = prm.type
                if is_char_pointer(ptype):
                    content += '\tdelete [] parameter_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::' + str(prm.index))).replace('-', '_') + ';\n'
            if not isinstance(rtype.target, VoidTypeProxy):
                if is_char_pointer(rtype):
                    rtype = rtype.nested
                    rtype._target = '::std::string'
                    content += '\t' + rtype.globalname + ' ' + ' result_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::std::string')).replace('-', '_') + '(result_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::char')).replace('-', '_') +');\n'
                    content += '\tdelete [] result_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::char')).replace('-', '_') + ';\n'
                    content += '\treturn result_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname + '::std::string')).replace('-', '_') +';\n'
                else:
                    content += '\treturn result_' + str(uuid.uuid5(uuid.NAMESPACE_X500, fct.globalname)).replace('-', '_').replace('-', '_') +';\n'
            content += '}\n'
            exportnode.content += '\n' + content
    content = ""
    for header in asg.headers(asg['::std::string'], *functions):
        if header.language == 'c':
            content += 'extern "C" { #include <' + asg.include_path(header) + '> }\n'
        else:
            content += '#include <' + asg.include_path(header) + '>\n'
    exportnode.content = content + '\n' + exportnode.content + '\n\nvoid export_char_pointer_as_std_string()\n{\n'
    for fct in functions:
        exportnode.content += '\tboost::python::def(char_pointer_as_std_string_' + fct.hash + ', char_pointer_as_std_string_' + fct.hash + ');\n'
    exportnode.content += '}'
    raise NotImplementedError() # TODO
    if on_disk:
        exportnode.write()
        modulenode.write()
    pydir = kwargs.pop('pydir', None)
    if kwargs.pop('python', True) and not pydir is None:
        asg.add_python_file(pydir=pydir, **kwargs)
    if kwargs.pop('sconscript', True) and not pydir is None:
        asg.add_sconsript(pydir=pydir, **kwargs)
    curr = time.time()
    diagnostic = BackEndDiagnostic()
    diagnostic.elapsed = curr - prev
    diagnostic._nodes = [modulenode, exportnode]
    return diagnostic
