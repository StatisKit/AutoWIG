import os
import unittest

from autowig import autowig

class TestBasic(unittest.TestCase):
    """Test the wrapping of a basic library"""

    @classmethod
    def setUpClass(cls):
        cls.directory = os.path.abspath(os.path.join('doc', 'basic'))

    def test_wrappers(self):
        asg = autowig.AbstractSemanticGraph()
        autowig.parser.plugin = 'pyclanglite'
        autowig.parser(asg, [os.path.join(self.directory, 'binomial.h')], ['-x', 'c++', '-std=c++11', '-I' + os.path.abspath(self.directory)])

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        autowig.generator.plugin = 'boost_python_internal'
        wrappers = autowig.generator(asg, module=os.path.join(self.directory, 'module.cpp'),
                        decorator=None,
                        prefix='wrapper_')

        wrappers = sorted(wrappers, key=lambda wrapper: wrapper.globalname)
        for wrapper in wrappers:
            with open(wrapper.globalname, 'r') as filehandler:
                self.assertEqual(wrapper.content, filehandler.readlines())
