from ..header.interface import FunctionHeaderInterface, functions, flatten, header_interface
from mako.lookup import TemplateLookup
from path import path

class BoostPythonModule(object):

    def __init__(dirpath, **kwargs):
        """
        """
        if not isinstance(dirpath, path):
            self._dirpath = path(dirpath)
        if not self._dirpath.exists():
            raise ValueError('`dirpath` parameter')
        self._flags = dict.pop(kwargs, 'flags', None)
        self.lookup = dict.pop(kwargs, 'lookup', TemplateLookup(directories=[str(path(__file__).parent)], strict_undefined=True))
        self._filename = dict.pop(kwargs, 'filename', 'export_module')
        self._tabsize = dict.pop(kwargs, 'tabsize', 4)

    def implementation(self):
        includes = set()
        module = ""
        for scope, interfaces in flatten(*[header_interface(filepath, flags) for filepath in dirpath.walkfiles(pattern='.h')], level=2):
            filtered = [interface for interface in functions(*interfaces) if str(interface.output) == 'void' and len(interface.inputs) == 0]
            module += (" "*self._tabsize).join(scope+str(interface)+"();\n" for interface in filtered)
            includes.update([interface.file for interface in filtered])
        template = lookup.get_template('boost_python_module.cpp')
        return template.render(
                includes = includes,
                module = module)

def get_lookup(self):
    return self._lookup

def set_lookup(self, lookup):
    if not isinstance(lookup, TemplateLookup):
        raise TypeError('`lookup` parameter')
    self._lookup = lookup

BoostPythonModule.lookup = property(get_lookup, set_lookup)
del get_lookup, set_lookup
