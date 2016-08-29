import unittest
from path import path
import __builtin__

import autowig

class TestFeedBack(unittest.TestCase):
    """Test the feedback of a SCons results"""

    @classmethod
    def setUpClass(cls):
        with open('test.h', 'w') as filehandler:
            filehandler.write("""
#include <utility>

namespace test
{
    typedef std::pair< const double, double > Point;
}""")

        with open('SConstruct', 'w') as filehandler:
            filehandler.write("""
from distutils import sysconfig
import sys

variables = Variables()

env = Environment()
variables.Update(env)

env.AppendUnique(LIBS = ['boost_python', 'python' + sysconfig.get_python_version()])
env.AppendUnique(CPPPATH = [sysconfig.get_python_inc()])
env.AppendUnique(CPPDEFINES = ['BOOST_PYTHON_DYNAMIC_LIB'])

env.Prepend(CPPPATH=sys.prefix + '/include')
env.Prepend(CPPPATH='.')
env.Prepend(LIBPATH=sys.prefix + '/lib')

env.AppendUnique(CXXFLAGS = ['-x', 'c++',
                             '-std=c++0x',
                             '-Wwrite-strings'])

pyenv = env.Clone()
#pyenv.AppendUnique(LIBS = ['basic'])
pyenv.AppendUnique(CXXFLAGS = ['-ftemplate-depth-100'])

wrap = pyenv.LoadableModule('_module', pyenv.Glob('wrapper_*.cpp') + ['_module.cpp'],
                            LDMODULESUFFIX = '.so',
                            FRAMEWORKSFLAGS = '-flat_namespace -undefined suppress')
Alias("py", wrap)
Alias("build", wrap)

Default("build")
""")
        autowig.parser.plugin = 'pyclanglite'
        autowig.generator.plugin = 'boost_python_internal'
        autowig.feedback.plugin = 'gcc-5'
        cls.srcdir = path('.').abspath()

    def test_feedback_export(self):
        """Test `feedback` export"""

        for wrapper in self.srcdir.walkfiles('wrapper_*.cpp'):
            wrapper.unlink()
        wrapper = self.srcdir/'_module.h'
        if wrapper.exists():
            wrapper.unlink()
        wrapper = self.srcdir/'_module.py'
        if wrapper.exists():
            wrapper.unlink()
        wrapper = self.srcdir/'_module.cpp'
        if wrapper.exists():
            wrapper.unlink()

        asg = autowig.AbstractSemanticGraph()

        asg = autowig.parser(asg, [self.srcdir/'test.h'],
                                  ['-x', 'c++', '-std=c++11', '-I' + str(self.srcdir)],
                                  silent = True)

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        module = autowig.generator(asg, module = self.srcdir/'_module.cpp',
                                     decorator = self.srcdir/'_module.py',
                                     prefix = 'wrapper_')

        module.write()
        compilation = autowig.scons(self.srcdir, 'build')

        err = ''

        #import pdb
        #pdb.set_trace()

        while not err == compilation.err:
            err = compilation.err
            code = autowig.feedback(err, '.', asg)
            if code:
                exec(code, locals())
