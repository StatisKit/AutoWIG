"""
"""
import uuid

from .tools import camel_case_to_lower
from .asg import *

__all__ = []

def hash_node_path( node, prefix='', suffix=''):
    if not isinstance(node, DeclarationProxy):
        raise TypeError('\'node\' parameter is not \'autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
    if prefix and not prefix.endswith('_'):
        prefix = prefix + '_'
    if isinstance(node, EnumeratorProxy):
        node = node.parent
    return prefix + node.hash + suffix
