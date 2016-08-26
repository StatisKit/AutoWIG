import os
import unittest
import sys 
from path import path
from SCons.Script.Main import AddOption, GetOption
from SCons.Environment import Environment
from SCons.Script import Variables, Main

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
            context['int'] = int
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
        cls.rootdir = path('.').abspath()
        cls.srcdir = cls.rootdir/'doc'/'examples'/'basic'

    def test_mapping_export(self):
        """Test `mapping` export"""

        for wrapper in self.srcdir.walkfiles('wrapper_*.cpp'):
            wrapper.unlink()
        wrapper = self.srcdir/'_module.cpp'
        if wrapper.exists():
            wrapper.unlink()
        wrapper = self.srcdir/'_module.py'
        if wrapper.exists():
            wrapper.unlink()

        asg = autowig.AbstractSemanticGraph()

        asg = autowig.parser(asg, [self.srcdir/'overload.h', self.srcdir/'binomial.h'],
                                  ['-x', 'c++', '-std=c++11', '-I' + str(self.srcdir)],
                                  silent = True)

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        module = autowig.generator(asg, module = self.srcdir/'_module.cpp',
                                     decorator = self.srcdir/'_module.py',
                                     prefix = 'wrapper_')

        module.write()
        autowig.scons(self.srcdir, 'build')

    def test_basic_export(self):
        """Test `basic` export"""
        proxy = autowig.boost_python_export.proxy
        autowig.boost_python_export.proxy = 'basic'
        self.test_mapping_export()
        autowig.boost_python_export.proxy = proxy

    def test_pyclanglite_parser(self):
        """Test `pyclanglite` parser"""
        plugin = autowig.parser.plugin
        autowig.parser.plugin = 'pyclanglite'
        self.test_mapping_export()
        autowig.parser.plugin = plugin

    def test_boost_python_pattern_generator(self):
        """Test `boost_python_pattern` generator"""
        plugin = autowig.generator.plugin
        autowig.generator.plugin = 'boost_python_pattern'
        self.test_mapping_export()
        autowig.generator.plugin = plugin
