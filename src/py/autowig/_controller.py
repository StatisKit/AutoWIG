from pkgtk.plugin import PluginManager

controller = PluginManager('autowig.controller', brief="AutoWIG middle-end plugin_managers",
        details="""AutoWIG middle-end plugin_managers are responsible for Abstract Semantic Graph (ASG) modification from Python semantic queries.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")
