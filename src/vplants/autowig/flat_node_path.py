from openalea.core.util import camel_case_to_lower
from vplants.autowig.asg import CodeNodeProxy, TypedefProxy, EnumConstantProxy, ClassTemplateSpecializationProxy

def flat_node_path( node, prefix='', suffix='', update_suffix=True):
    if not isinstance(node, CodeNodeProxy):
        raise TypeError('\'node\' parameter is not \'vplants.autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
    if update_suffix and (any(isinstance(ancestor, ClassTemplateSpecializationProxy) for ancestor in node.ancestors) or isinstance(node, ClassTemplateSpecializationProxy)):
        suffix = '_' + node.hash + suffix
    if node.globalname == '::':
        filepath = './' + prefix + suffix.strip('_')
    else:
        if isinstance(node, ClassTemplateSpecializationProxy):
            filepath = flat_node_path(node.specialize, prefix, suffix, False)
        elif isinstance(node, (TypedefProxy, EnumConstantProxy)):
            filepath = flat_node_path(node.parent, prefix, suffix, update_suffix)
        else:
            filepath = flat_node_path(node.parent, prefix, '_' + camel_case_to_lower(node.localname) + suffix, False)
    return filepath

