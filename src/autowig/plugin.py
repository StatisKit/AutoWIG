"""
"""

from .tools import Plugin

front_end = Plugin('autowig.front_end', brief="AutoWIG front-end plugins",
        detailed="""AutoWIG front-end plugins are responsible for Abstract Semantic Graph (ASG) completion from C/C++ parsing.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

middle_end = Plugin('autowig.middle_end', brief="AutoWIG middle-end plugins",
        detailed="""AutoWIG middle-end plugins are responsible for Abstract Semantic Graph (ASG) modification from Python semantic queries.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

back_end = Plugin('autowig.back_end', brief="AutoWIG back-end plugins",
        detailed="""AutoWIG back-end plugins are responsible for C/C++ code generation from an Abstract Semantic Graph (ASG) interpretation.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

node_rename = Plugin('autowig.node_rename', brief="",
        detailed="")

node_path = Plugin('autowig.node_path', brief="",
        detailed="")
