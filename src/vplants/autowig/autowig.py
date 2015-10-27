from .asg import AbstractSemanticGraph
from .front_end import front_end
if 'pyclanglite' in front_end:
    front_end.plugin = 'pyclanglite'
else:
    front_end.plugin = 'libclang'
from .middle_end import middle_end
middle_end.plugin = 'default'
from .back_end import back_end
back_end.plugin = 'boost_python:in_memory'
from .scons import *
