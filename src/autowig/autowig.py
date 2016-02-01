from .asg import AbstractSemanticGraph
from .front_end import front_end
if 'pyclanglite' in front_end:
    front_end.plugin = 'pyclanglite'
else:
    front_end.plugin = 'libclang'
from .middle_end import middle_end
middle_end.plugin = 'default'
from .boost_python_call_policy import boost_python_call_policy
boost_python_call_policy.plugin = 'boost_python:default'
from .held_type import held_type
held_type.plugin = 'std:shared_ptr'
from .node_path import node_path
node_path.plugin = 'flat'
from .back_end import back_end
back_end.plugin = 'boost_python:export'
from .scons import *
