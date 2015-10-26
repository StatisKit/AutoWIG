class BoostPythonBackEndPlugin(object):

    modulename = 'vplants.autowig.boost_python_back_end'

class BoostPythonInMemoryBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    objectname = 'in_memory_back_end'

class BoostPythonOnDiskBackEndPlugin(BoostPythonBackEndPlugin):
    """Boost.Python plugin for the AutoWIG back-end writing in memory Boost.Python wrappers on disk"""

    objectname = 'on_disk_back_end'
