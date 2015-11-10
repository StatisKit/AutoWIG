from openalea.core.plugin.functor import PluginFunctor
from openalea.core.util import camel_case_to_lower
from vplants.autowig.asg import CodeNodeProxy, ClassTemplateSpecializationProxy

__all__ = ['node_path']

node_path = PluginFunctor.factory('autowig.node_path')
#node_path.__class__.__doc__ = """Node path functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""
