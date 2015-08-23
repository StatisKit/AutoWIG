class LibclangFrontEndPlugin(object):
    """Plugin for the AutoWIG front-end based on the Libclang module"""

    modulename = 'vplants.autowig.libclang_front_end'
    objectname = 'front_end'

    implements = 'front-end'

class MiddleEndPlugin(object):
    """Default plugin for the AutoWIG middle-end"""

    modulename = 'vplants.autowig.default_middle_end'
    objectname = 'default_middle_end'

    implements = 'middle-end'

class BoostPythonInMemoryBackEndPlugin(object):
    """Boost.Python plugin for the AutoWIG back-end generating files in memory for Boost.Python wrappers"""

    modulename = 'vplants.autowig.boost_python_back_end'
    objectname = 'in_memory_back_end'

    implements = 'back-end'

class BoostPythonOnDiskBackEndPlugin(object):
    """Boost.Python plugin for the AutoWIG back-end writing in memory Boost.Python wrappers on disk"""

    modulename = 'vplants.autowig.boost_python_back_end'
    objectname = 'on_disk_back_end'

    implements = 'back-end'

class NodePathPlugin(object):
    """Plugin for the path computation of a node"""

    modulename = 'vplants.autowig.node_path'

    tags = ['node', 'path']

class FlatNodePathPlugin(NodePathPlugin):
    """Plugin for the flat path computation of a node"""

    objectpath = 'flat_node_path'

class NestedNodePathPlugin(NodePathPlugin):
    """Plugin for the nested path computation of a node"""

    objectpath = 'nested_node_path'
