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
from .boost_python_generatorer import *
from .scons import *
