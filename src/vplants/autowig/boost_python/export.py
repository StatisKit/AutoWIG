"""
"""

from SCons.Builder import Builder
from SCons.Action import Action
from mako.lookup import TemplateLookup
from path import path
import re

from ..tools import lower
from ..cpp.interface import enums, functions, classes, header_interface, resolve_scopes

class BoostPythonExport(object):
    """
    """

    def __init__(self, *interfaces, **kwargs):
        self._scope = dict.pop(kwargs, 'scope', '')
        self._filename = dict.pop(kwargs, 'filename', 'export_objects')
        self._enums = [enum for enum in enums(*interfaces) if not enum.hidden]
        self._functions = [func for func in functions(*interfaces) if any([not ovld.hidden for ovld in func])]
        self._classes = [clss for clss in classes(*interfaces) if not clss.hidden]
        self.lookup = dict.pop(kwargs, 'lookup', TemplateLookup(directories=[str(path(__file__).parent)], strict_undefined=True))
        self._includes = set([interface.file for interface in interfaces])

    @property
    def path(self):
        return self.scope.replace('::', '/')+self.filename

    @property
    def scope(self):
        return self._scope

    @property
    def filename(self):
        return self._filename

    @property
    def includes(self):
        return self._includes

    @includes.setter
    def includes(self, includes):
        self._includes = includes

    @property
    def enums(self):
        return self._enums

    @property
    def functions(self):
        return self._functions

    @property
    def classes(self):
        return self._classes

    def implement(self):
        template = self.lookup.get_template('boost_python_export.cpp')
        return template.render(
                includes = self.includes,
                filename = self.filename,
                scope = self.scope,
                enums = self.enums,
                functions = self.functions,
                classes = self.classes,
                enum_thin = self.lookup.get_template('enum_thin.cpp'),
                enum_deep = self.lookup.get_template('enum_deep.cpp'),
                func_thin = self.lookup.get_template('func_thin.cpp'),
                func_deep = self.lookup.get_template('func_deep.cpp'),
                clss_thin = self.lookup.get_template('clss_thin.cpp'),
                clss_deep = self.lookup.get_template('clss_deep.cpp'),
                lookup = self.lookup)

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

def get_lookup(self):
    return self._lookup

def set_lookup(self, lookup):
    if not isinstance(lookup, TemplateLookup):
        raise TypeError('`lookup` parameter')
    self._lookup = lookup

BoostPythonExport.lookup = property(get_lookup, set_lookup)
del get_lookup, set_lookup


def boost_python_export_emit(target, source, env):
    interfaces = [header_interface(header.abspath, flags=env.subst("$_CCCOMCOM").split(" ")) for header in source]
    if 'AUTOWIG_FILTER' in env: env['AUTOWIG_FILTER'](*interfaces)
    env['AUTOWIG_SCOPES'] = resolve_scopes(*interfaces)
    env['AUTOWIG_EXPORT'] = [BoostPythonExport(enum, scope=scope, rootdir=source[0].abspath+'/', filename='export_enum_'+lower(str(enum))) for scope, interfaces in env['AUTOWIG_SCOPES'].iteritems() for enum in enums(*interfaces) if not enum.hidden]+[BoostPythonExport(*func, scope=scope, rootdir=source[0].abspath+'/', filename='export_function_'+lower(str(func[0]))) for scope, interfaces in env['AUTOWIG_SCOPES'].iteritems() for func in functions(*interfaces) if any(not over.hidden for over in
        func)]+[BoostPythonExport(clss, scope=scope, rootdir=source[0].abspath+'/', filename='export_class_'+lower(str(clss))) for scope, interfaces in env['AUTOWIG_SCOPES'].iteritems() for clss in classes(*interfaces) if not clss.hidden and not clss.has_templates]
    target = [target[0].abspath+'/'.join(export.scope.split('::'))+export.filename+'.'+ext for export in env['AUTOWIG_EXPORT'] for ext in ['h', 'cpp']]
    for export in env["AUTOWIG_EXPORT"]:
        export.includes = [re.sub('(.*)cpp', env.subst('$libname'), include) for include in export.includes]
    return target, source

def boost_python_export_build(target, source, env):
    """
    """
    for index, target in enumerate(target):
        filehandler = open(target.abspath, 'w')
        filehandler.write(env["AUTOWIG_EXPORT"][index/2].implement())
        filehandler.close()
    return 0

def boost_python_export_str(target, source, env, executor=None):
    """
    """
    return "\n".join("Generate file: \""+str(_target)+'\"' for _target in target)

boost_python_export = Builder(
        action = Action(boost_python_export_build, boost_python_export_str),
        emitter = boost_python_export_emit)
