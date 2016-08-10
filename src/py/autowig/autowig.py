"""
"""

from .asg import AbstractSemanticGraph
from .plugin_manager import parser, visitor, documenter, controller, feedback, node_rename, node_path
if 'pyclanglite' in parser:
    parser.plugin = 'pyclanglite'
else:
    parser.plugin = 'libclang'
visitor.plugin = 'all'
documenter.plugin = 'doxygen2sphinx'
controller.plugin = 'default'
feedback.plugin = 'gcc-5'
node_rename.plugin = 'PEP8'
node_path.plugin = 'hash'
from .boost_python_generator import boost_python_call_policy, boost_python_export_factory, boost_python_module_factory, boost_python_decorator_factory
boost_python_call_policy.plugin = 'default'
boost_python_export_factory.proxy = 'mapping'
boost_python_module_factory.proxy = 'default'
boost_python_decorator_factory.proxy = 'default'
from .scons import *
