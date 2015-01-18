"""
"""

from vplants.autowig.parser import parse
import asciitree


def ascii(mod):
    """
    """

    def node_children(node):
        """
        """
        return (c for c in node.get_children() if c.location.file.name == sys.argv[1])

    def print_node(node):
        """
        """
        text = node.spelling or node.displayname
        kind = str(node.kind)[str(node.kind).index('.')+1:]
        return '{} {}'.format(kind, text)

    return "\n".join([asciitree.draw_tree(translation_unit.cursor, node_children, print_node) for translation_unit in parse(mod)])
