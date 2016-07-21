"""
"""

from .tools import camel_case_to_lower
from .asg import *

__all__ = []

def scope_node_path(node, prefix='', suffix='', update_suffix=True):
    if not isinstance(node, DeclarationProxy):
        raise TypeError('\'node\' parameter is not \'autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
    if update_suffix and (any(isinstance(ancestor, ClassTemplateSpecializationProxy) for ancestor in node.ancestors) or isinstance(node, ClassTemplateSpecializationProxy)):
        suffix = '_' + node.hash + suffix
    if node.globalname == '::':
        filepath = './' + prefix + suffix.strip('_')
    else:
        if isinstance(node, ClassTemplateSpecializationProxy):
            filepath = flat_node_path(node.specialize, prefix, suffix, False)
        elif isinstance(node, (TypedefProxy, EnumeratorProxy)):
            filepath = flat_node_path(node.parent, prefix, suffix, update_suffix)
        else:
            filepath = flat_node_path(node.parent, prefix, '_' + camel_case_to_lower(node.localname) + suffix, False)
    return filepath

def hash_node_path( node, prefix='', suffix=''):
    if not isinstance(node, DeclarationProxy):
        raise TypeError('\'node\' parameter is not \'autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
    if prefix and not prefix.endswith('_'):
        prefix = prefix + '_'
    if isinstance(node, EnumeratorProxy):
        node = node.parent
    #if not isinstance(node, EnumeratorProxy):
    #    prefix = prefix + camel_case_to_lower(node.__class__.__name__)
    #    prefix = prefix.replace('_proxy', '')
    #else:
    #    prefix = prefix + 'enumerators'
    #    node = node.parent
    return prefix + node.hash + suffix
