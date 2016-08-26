"""
"""

from .asg import AbstractSemanticGraph, visitor
visitor.plugin = 'all'

from ._parser import parser
if 'pyclanglite' in parser:
    parser.plugin = 'pyclanglite'
else:
    parser.plugin = 'libclang'
    
from ._documenter import documenter
documenter.plugin = 'doxygen2sphinx'

from ._controller import controller
controller.plugin = 'default'

from ._feedback import feedback
feedback.plugin = 'gcc-5'

from ._node_rename import node_rename
node_rename.plugin = 'PEP8'

from ._node_path import node_path
node_path.plugin = 'hash'

from .boost_python_generator import boost_python_call_policy, boost_python_export, boost_python_module, boost_python_decorator
boost_python_call_policy.plugin = 'default'
boost_python_export.proxy = 'mapping'
boost_python_module.proxy = 'default'
boost_python_decorator.proxy = 'default'

from ._scons import scons
