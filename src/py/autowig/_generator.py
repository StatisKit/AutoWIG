from pkgtk.plugin import PluginManager

generator = PluginManager('autowig.generator', brief="AutoWIG back-end plugin_managers",
        details="""AutoWIG back-end plugin_managers are responsible for C/C++ code generation from an Abstract Semantic Graph (ASG) interpretation.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")
