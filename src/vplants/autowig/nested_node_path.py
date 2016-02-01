from openalea.core.util import camel_case_to_lower
from autowig.asg import CodeNodeProxy, ClassTemplateSpecializationProxy

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
