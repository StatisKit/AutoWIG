import os
import unittest

from autowig import autowig

class TestBasic(unittest.TestCase):
    """Test the wrapping of a basic library"""

    @classmethod
    def setUpClass(cls):
        autowig.parser.plugin = 'libclang'
        autowig.generator.plugin = 'boost_python_internal'
        cls.directory = os.path.abspath(os.path.join('doc', 'basic'))

    def test_mapping_export(self):
        """Test `mapping` export"""
        asg = autowig.AbstractSemanticGraph()

        asg = autowig.parser(asg, [os.path.join(self.directory, 'binomial.h')],
                                  ['-x', 'c++', '-std=c++11', '-I' + os.path.abspath(self.directory)],
                                  silent = True)

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        wrappers = autowig.generator(asg, module=os.path.join(self.directory, 'module.cpp'),
                        decorator=None,
                        prefix='wrapper_')

        # wrappers = sorted(wrappers, key=lambda wrapper: wrapper.globalname)
        # for wrapper in wrappers:
        #     with open(wrapper.globalname, 'r') as filehandler:
        #         self.assertEqual(wrapper.content, filehandler.read())

    def test_basic_export(self):
        """Test `basic` export"""
        proxy = autowig.boost_python_export.proxy
        autowig.boost_python_export.proxy = 'basic'
        self.test_mapping_export()
        autowig.boost_python_export.proxy = proxy

    def test_libclang_parser(self):
        """Test `libclang` parser"""
        plugin = autowig.parser.plugin
        autowig.parser.plugin = 'libclang'
        self.test_mapping_export()
        autowig.parser.plugin = plugin

    def test_boost_python_pattern_generator(self):
        """Test `boost_python_pattern` generator"""
        plugin = autowig.generator.plugin
        autowig.generator.plugin = 'boost_python_pattern'
        self.test_mapping_export()
        autowig.generator.plugin = plugin