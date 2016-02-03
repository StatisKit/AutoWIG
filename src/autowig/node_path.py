"""
"""

from .tools import camel_case_to_lower
from .asg import DeclarationProxy, TypedefProxy, EnumeratorProxy, ClassTemplateSpecializationProxy

__all__ = []

def flat_node_path( node, prefix='', suffix='', update_suffix=True):
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

def nested_node_path(node, prefix, suffix, camel_case=False):
    if not isinstance(node, CodeNodeProxy):
        raise TypeError('\'node\' parameter is not \'autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
    if node.globalname == '::':
        filepath = '.' + prefix + suffix
    else:
        if isinstance(node, ClassTemplateSpecializationProxy):
            filepath = nested_node_path(node.specialize, prefix=prefix, suffix=suffix, camel_case=camel_case)
        else:
            if camel_case:
                filepath = prefix + node.localname + suffix
            else:
                filepath = prefix + camel_case_to_lower(node.localname) + suffix
            filepath = nested_node_path(node.parent, prefix='', suffix='', camel_case=True) + '/' + filepath
    return filepath
