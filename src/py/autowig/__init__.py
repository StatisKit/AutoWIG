##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (10)                       #
#                                                                                #
##################################################################################

"""
"""

from .asg import AbstractSemanticGraph, visitor
visitor.plugin = 'all'

from ._parser import parser
if 'clanglite' in parser:
    parser.plugin = 'clanglite'
else:
    parser.plugin = 'libclang'
    
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