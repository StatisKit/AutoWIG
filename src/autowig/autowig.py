"""
"""

from .asg import AbstractSemanticGraph
from .plugin_manager import *
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
from .boost_python_generator import *
boost_python_call_policy.plugin = 'default'
boost_python_export.proxy = 'mapping'
boost_python_module.proxy = 'default'
boost_python_decorator.proxy = 'default'
from .scons import *
