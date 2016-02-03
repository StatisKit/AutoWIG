class BoostPythonBackEndPlugin(object):

    modulename = 'autowig.boost_python_back_end'

class BoostPythonExportBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:export'
    objectname = 'export_back_end'


class BoostPythonModuleBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:module'
    objectname = 'module_back_end'


class BoostPythonImportBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    name = 'boost_python:import'
    objectname = 'import_back_end'
