"""
"""

import pkg_resources

def build_plugin_manager_doc(self):
    self.__doc__ = []
    if self._brief:
        self.__doc__.append(self._brief)
        self.__doc__.append('')
    if self._detailed:
        self.__doc__.append(self._detailed)
        self.__doc__.append('')
    self.__doc__.append(":Available Implementations:")
    self.__doc__.extend(" - \'" + plugin.name + '\'' for plugin in pkg_resources.iter_entry_points(self._group))
    self.__doc__.extend(" - \'" + plugin + '\'' for plugin in self._cache)
    self.__doc__ = '\n'.join(self.__doc__)

class PluginManagerImplementationDescriptor(object):
    """A plugin plugin manager descriptor that returns and sets plugin_manager implementations
    """

    def __get__(self, obj, objtype):
        if hasattr(obj, '_plugin'):
            plugin = obj._plugin
            while plugin in obj._cache:
                plugin = obj._cache[plugin]
            if callable(plugin):
                return plugin
            else:
                return pkg_resources.iter_entry_points(obj._group, plugin).next().load()
        else:
            def __call__(self, *args, **kwargs):
                """No plugin selected"""
                raise NotImplementedError("An plugin must be selected using \'plugin\' field")
            return __call__

class PluginManagerIdentificationDescriptor(object):
    """
    """

    def __get__(self, obj, cls):
        if not hasattr(obj, '_plugin'):
            raise ValueError('\'plugin\' identification not setted')
        return obj._plugin

    def __set__(self, obj, plugin):
        obj._plugin = plugin
        build_plugin_manager_doc(obj)


class PluginManager(object):

    __call__ = PluginManagerImplementationDescriptor()

    plugin = PluginManagerIdentificationDescriptor()

    def __init__(self, group, brief="", detailed=""):
        """Create a plugin manager"""
        self._group = group
        self._brief = brief
        self._detailed = detailed
        self._cache = dict()
        build_plugin_manager_doc(self)

    def __contains__(self, plugin):
        """
        """
        return plugin in self._cache or len(list(pkg_resources.iter_entry_points(self._group, plugin))) > 0

    def __getitem__(self, plugin):
        """
        """
        plugin, self.plugin = self.plugin, plugin
        plugin, self.plugin = self.__call__, plugin
        return plugin

    def __setitem__(self, plugin, implementation):
        if not isinstance(plugin, basestring):
            raise TypeError('\'plugin\' parameter must be a basestring instance')
        if callable(implementation):
            self._cache[plugin] = implementation
        elif isinstance(implementation, basestring):
            if not implementation in self:
                raise ValueError('\'implementation\' parameter must be an existing plugin')
            if plugin == implementation:
                raise ValueError('\'plugin\' and \'implementation\' parameters cannot have the same value')
            self._cache[plugin] = implementation
        else:
            raise TypeError('must be callable or a basestring instance')
        build_plugin_manager_doc(self)

parser = PluginManager('autowig.parser', brief="AutoWIG front-end plugin_managers",
        detailed="""AutoWIG front-end plugin_managers are responsible for Abstract Semantic Graph (ASG) completion from C/C++ parsing.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

controller = PluginManager('autowig.controller', brief="AutoWIG middle-end plugin_managers",
        detailed="""AutoWIG middle-end plugin_managers are responsible for Abstract Semantic Graph (ASG) modification from Python semantic queries.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

generator = PluginManager('autowig.generator', brief="AutoWIG back-end plugin_managers",
        detailed="""AutoWIG back-end plugin_managers are responsible for C/C++ code generation from an Abstract Semantic Graph (ASG) interpretation.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

node_rename = PluginManager('autowig.node_rename', brief="",
        detailed="")

node_path = PluginManager('autowig.node_path', brief="",
        detailed="")
