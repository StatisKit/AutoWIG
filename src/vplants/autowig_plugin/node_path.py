class NodePathPlugin(object):
    """Plugin for the path computation of a node"""

    modulename = 'vplants.autowig.node_path'

class FlatNodePathPlugin(NodePathPlugin):
    """Plugin for the flat path computation of a node"""

    objectpath = 'flat_node_path'

class NestedNodePathPlugin(NodePathPlugin):
    """Plugin for the nested path computation of a node"""

    objectpath = 'nested_node_path'
