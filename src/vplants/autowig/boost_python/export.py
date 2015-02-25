"""
"""

from ..header.interface import EnumHeaderInterface, FunctionHeaderInterface, UserDefinedTypeHeaderInterface, ScopeHeaderInterface, enums, functions, classes

from mako.lookup import TemplateLookup
from path import path

class BoostPythonExport(object):
    """
    """

    def __init__(self, *interfaces, **kwargs):
        self._scope = dict.pop(kwargs, 'scope', '')
        self._filename = dict.pop(kwargs, 'filename', 'export_objects')
        if not 'library' in kwargs:
            def library(filename):
                return filename
            self._library = library
        else:
            self._library = kwargs.pop('library')
            if not callable(self._library):
                raise TypeError('`library` parameter')
        self._enums = [enum for enum in enums(*interfaces) if not enum.hidden]
        self._functions = [func for func in functions(*interfaces) if any([not ovld.hidden for ovld in func])]
        self._classes = [clss for clss in classes(*interfaces) if not clss.hidden]
        self.lookup = dict.pop(kwargs, 'lookup', TemplateLookup(directories=[str(path(__file__).parent)], strict_undefined=True))
        self._includes = set([interface.file for interface in interfaces])

    def implementation(self):
        template = self.lookup.get_template('boost_python_export.cpp')
        return template.render(
                filename = self._filename,
                scope = self._scope,
                enums = self._enums,
                functions = self._functions,
                classes = self._classes,
                enum_thin = self.lookup.get_template('enum_thin.cpp'),
                enum_deep = self.lookup.get_template('enum_deep.cpp'),
                func_thin = self.lookup.get_template('func_thin.cpp'),
                func_deep = self.lookup.get_template('func_deep.cpp'),
                clss_thin = self.lookup.get_template('clss_thin.cpp'),
                clss_deep = self.lookup.get_template('clss_deep.cpp'),
                lookup = self.lookup)

    def header(self):
        template = self.lookup.get_template('boost_python_export.h')
        return template.render(
                library = self._library,
                includes = self._includes,
                enums = self._enums,
                functions = self._functions,
                classes = self._classes,
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
