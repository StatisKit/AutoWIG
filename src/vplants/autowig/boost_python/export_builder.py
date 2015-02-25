from SCons.Builder import Builder
from vplants.autowig.tools import lower
from vplants.autowig.header.interface import flatten
from vplants.autowig.boost_python.interface import BoostPythonInterface

def boost_python_export_emit(targets, sources, env):
    """
    """
    env['AUTOWIG_INTERFACES'] = {scope : [interface for interface in interfaces if isinstance(interface, BoostPythonInterface)] for scope, interfaces in flatten(*[interface(source) for source in sources if source.suffix == '.h'], level=1)}
    targets.extend(itertools.chain(*[[scope.replace('::', '/')+lower(str(interface))+'.'+ext for scope, interface in env['AUTOWIG_INTERFACES'] for ext in ['h', 'cpp']])
    return targets, sources

def boost_python_export_build(targets, sources, env):
    """
    """
    from path import path
    for target, (scope, interface) in zip([target for target in targets if , env['AUTOWIG_INTERFACES']):
        targetpath = path(str(target))
        if not targetpath.exists():
            targetpath.makedirs()
    return 0

__boost_python_export_builder = Builder(
        action = boost_python_export_build,
        emitter = boost_python_export_emit)

def generate(env):
    """Add Builders and construction variables to the Environment."""

    env['BUILDERS']['BoostPythonExport'] = __boost_python_export_builder

def exists(env):
    return 1
