from openalea.core.plugin.functor import PluginFunctor
from openalea.core.util import camel_case_to_lower

__all__ = ['node_path']

node_path = PluginFunctor.factory('autowig', implements='path')
#node_path.__class__.__doc__ = """Node path functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""

class FlatNodePathPlugin(object):
    """Plugin for the flat path computation of a node"""

    implements = 'path'

    def implementation(self, node, prefix, suffix, update_suffix=True):
        from vplants.autowig.asg import CodeNodeProxy, ClassTemplateSpecializationProxy
        if not isinstance(node, CodeNodeProxy):
            raise TypeError('\'node\' parameter is not \'vplants.autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
        if update_suffix and (any(isinstance(ancestor, ClassTemplateSpecializationProxy) for ancestor in node.ancestors) or isinstance(node, ClassTemplateSpecializationProxy)):
            suffix = '_' + node.hash + suffix
        if node.globalname == '::':
            filepath = './' + prefix + suffix
        else:
            if isinstance(node, ClassTemplateSpecializationProxy):
                filepath = self.implementation(node.specialize, prefix, suffix, False)
            else:
                filepath = self.implementation(node.parent, prefix, '', False) + '_' + camel_case_to_lower(node.localname) + suffix
        filepath = filepath.strip('_')
        return filepath

node_path['flat'] = FlatNodePathPlugin
node_path.plugin = 'flat'

class NestedNodePathPlugin(object):
    """Plugin for the nested path computation of a node"""

    implements = 'path'

    def implementation(self, node, prefix, suffix, camel_case=False):
        from vplants.autowig.asg import CodeNodeProxy, ClassTemplateSpecializationProxy
        if not isinstance(node, CodeNodeProxy):
            raise TypeError('\'node\' parameter is not \'vplants.autowig.asg.CodeNodeProxy\' instance but a \'' + node.__class__.__name__ + '\' instance')
        if node.globalname == '::':
            filepath = '.' + prefix + suffix
        else:
            if isinstance(node, ClassTemplateSpecializationProxy):
                filepath = self.implementation(node.specialize, prefix=prefix, suffix=suffix, camel_case=camel_case)
            else:
                if camel_case:
                    filepath = prefix + node.localname + suffix
                else:
                    filepath = prefix + camel_case_to_lower(node.localname) + suffix
                filepath = self.implementation(node.parent, prefix='', suffix='', camel_case=True) + '/' + filepath
        return filepath

node_path['nested'] = NestedNodePathPlugin
