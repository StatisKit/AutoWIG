"""
"""

from .asg import AbstractSemanticGraph
from .plugin import *
if 'pyclanglite' in front_end:
    front_end.plugin = 'pyclanglite'
else:
    front_end.plugin = 'libclang'
node_rename.plugin = 'PEP8'
node_path.plugin = 'flat'
from .boost_python_back_end import *
from .scons import *
