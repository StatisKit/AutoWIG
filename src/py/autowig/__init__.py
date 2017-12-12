## Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ##
##                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
## Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
##                                                                       ##
## This file is part of the AutoWIG project. More information can be     ##
## found at                                                              ##
##                                                                       ##
##     http://autowig.rtfd.io                                            ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

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
