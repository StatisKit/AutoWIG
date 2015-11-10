class OnDiskBackEndPlugin(object):
    """Plugin for the AutoWIG back-end writing in memory files on disk"""

    name = 'on_disk'
    modulename = 'vplants.autowig.on_disk_back_end'
    objectname = 'on_disk_back_end'


class BoostPythonBackEndPlugin(object):

    modulename = 'vplants.autowig.boost_python_back_end'

class BoostPythonExportBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:export'
    objectname = 'export_back_end'

class BoostPythonClosureBackEndPlugin(BoostPythonBackEndPlugin):
    """
    """

    name = 'boost_python:closure'
    objectname = 'closure_back_end'

class BoostPythonModuleBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:module'
    objectname = 'module_back_end'

class BoostPythonInitBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:init'
    objectname = 'init_back_end'


class BoostPythonImportBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:import'
    objectname = 'import_back_end'

class SConsBoostPythonBackEndPlugin(object):
    """
    """

    name = 'scons:boost_python'
    modulename = 'vplants.autowig.scons'
    objectname = 'boost_python_back_end'
