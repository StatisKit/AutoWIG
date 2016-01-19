"""
"""

from SCons.Builder import Builder
from SCons.Action import Action
from SCons.Node.FS import Dir
from mako.lookup import TemplateLookup
import os
from path import path

from ..cpp.interface import functions, resolve_scopes, header_interface

class BoostPythonModule(object):

    def __init__(self, *funcnames, **kwargs):
        """
        """
        self.funcnames = funcnames
        self.lookup = dict.pop(kwargs, 'lookup', TemplateLookup(directories=[str(path(__file__).parent)], strict_undefined=True))
        self.modname = dict.pop(kwargs, 'module', 'module')

    def implement(self):
        template = self.lookup.get_template('boost_python_module.cpp')
        return template.render(
                modname = self.modname,
                funcnames = self.funcnames)

def get_lookup(self):
    return self._lookup

def set_lookup(self, lookup):
    if not isinstance(lookup, TemplateLookup):
        raise TypeError('`lookup` parameter')
    self._lookup = lookup

BoostPythonModule.lookup = property(get_lookup, set_lookup)
del get_lookup, set_lookup

def boost_python_module_build(target, source, env):
    """
    """
    print target[0].path
    commonprefix = os.path.commonprefix([os.path.dirname(filenode.abspath)+os.path.sep for filenode in source+target])
    module = BoostPythonModule(*[node.abspath.replace(commonprefix, '').replace('.cpp', '') for node in source],
            module = target[0].abspath.replace(commonprefix, '').replace('.cpp', ''),
            flags = env.subst("$_CCCOMCOM").split(" "))
    filehandler = open(target[0].abspath, 'w')
    filehandler.write(module.implement())
    filehandler.close()
    return 0

boost_python_module = Builder(
        action = Action(boost_python_module_build, "Generate file: \"$TARGET\""))
