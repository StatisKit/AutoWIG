"""
"""

import warnings

from .asg import AbstractSemanticGraph, visitor
visitor.plugin = 'all'

from ._parser import parser
if 'clanglite' in parser:
    parser.plugin = 'clanglite'
elif 'libclang' in parser:
    parser.plugin = 'libclang'
else:
    warnings.warn("no parser available", RuntimeWarning)
    
from ._documenter import documenter
documenter.plugin = 'doxygen2sphinx'

from ._controller import controller
controller.plugin = 'default'

from ._feedback import feedback
feedback.plugin = 'edit'

from ._node_rename import node_rename
node_rename.plugin = 'PEP8'

from ._node_path import node_path
node_path.plugin = 'hash'

from .boost_python_generator import boost_python_call_policy, boost_python_export, boost_python_module, boost_python_decorator
boost_python_call_policy.plugin = 'default'
boost_python_export.proxy = 'default'
boost_python_module.proxy = 'default'
boost_python_decorator.proxy = 'default'

from ._generator import generator
generator.plugin = 'boost_python'
