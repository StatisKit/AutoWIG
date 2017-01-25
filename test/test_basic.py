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
# File authors: Pierre Fernique <pfernique@gmail.com> (27)                       #
#                                                                                #
##################################################################################

import os
import unittest
import sys
import subprocess
import shutil
from path import path
import __builtin__ as builtins

import autowig

class TemplateRender(object):

    def __get__(self, obj, objtype, **kwargs):
        code = obj.code
        code = code.replace('\n    __M_caller = context.caller_stack._push_frame()', '', 1)
        code = code.replace('\n    __M_caller = context.caller_stack._push_frame()', '', 1)
        code = code.replace("        return ''\n    finally:\n        context.caller_stack._pop_frame()\n", "        return __M_string\n    except:\n        return ''", 1)
        code = code.replace("context,**pageargs", "**context", 1)
        code = code.replace("\n        __M_locals = __M_dict_builtin(pageargs=pageargs)", "", 1)
        code = code.replace("__M_writer = context.writer()", "__M_string = u''")
        code = code.replace("__M_writer(", "__M_string = operator.add(__M_string, ")
        code = "import operator\n" + code
        exec code in globals()
        def __call__(**context):
            for builtin in dir(builtins):
                if not builtin in context:
                    context[builtin] = getattr(builtins, builtin)
            return globals()["render_body"](**context)
        return __call__

from autowig.boost_python_generator import Template

Template.render = TemplateRender()

class TestBasic(unittest.TestCase):
    """Test the wrapping of a basic library"""

    @classmethod
    def setUpClass(cls):
        autowig.parser.plugin = 'libclang'
        autowig.generator.plugin = 'boost_python_internal'
        cls.tgt = path('.').abspath()/'doc'/'examples'/'basic'/'src'/'py'
        cls.src = path(sys.prefix).abspath()/'include'/'basic'

    def test_mapping_export(self):
        """Test `mapping` export"""

        import sys
        prefix = sys.prefix

        build = self.tgt.parent.parent/'build'
        print build
        if build.exists():
            shutil.rmtree(build)
        for wrapper in self.tgt.walkfiles('wrapper_*.cpp'):
            wrapper.unlink()
        wrapper = self.tgt/'_module.h'
        if wrapper.exists():
            wrapper.unlink()
        wrapper = self.tgt/'_module.py'
        if wrapper.exists():
            wrapper.unlink()
        wrapper = self.tgt/'_module.cpp'
        if wrapper.exists():
            wrapper.unlink()
            
        subprocess.check_call(['scons', 'cpp', '--prefix=' + prefix],
                              cwd=self.tgt.parent.parent,
                              shell=True)

        asg = autowig.AbstractSemanticGraph()

        asg = autowig.parser(asg, self.src.files('*.h'),
                                  ['-x', 'c++', '-std=c++11', '-I' + str(self.src.parent)],
                                  silent = True)

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        wrappers = autowig.generator(asg, module = self.tgt/'_module.cpp',
                                        decorator = self.tgt/'basic'/'_module.py',
                                        prefix = 'wrapper_')
        wrappers.write()
        
        subprocess.check_call(['scons', 'py', '--prefix=' + prefix],
                              cwd=self.tgt.parent.parent,
                              shell=True)

    def test_boost_python_pattern_generator(self):
        """Test `boost_python_pattern` generator"""
        plugin = autowig.generator.plugin
        autowig.generator.plugin = 'boost_python_pattern'
        self.test_mapping_export()
        autowig.generator.plugin = plugin
