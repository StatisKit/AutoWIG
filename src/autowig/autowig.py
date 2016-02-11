"""
"""

from .asg import AbstractSemanticGraph
from .plugin import *
if 'pyclanglite' in parser:
    parser.plugin = 'pyclanglite'
else:
    parser.plugin = 'libclang'
node_rename.plugin = 'PEP8'
node_path.plugin = 'flat'
from .boost_python_generator import *
boost_python_export.plugin = 'mapping'
boost_python_module.plugin = 'default'
boost_python_decorator.plugin = 'default'
from .scons import *
