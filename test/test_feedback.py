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
## file except in compliance with the License.You should have received a ##
## copy of the Apache License, Version 2.0 along with this file; see the ##
## file LICENSE. If not, you may obtain a copy of the License at         ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

import autowig
import six

import unittest
from nose.plugins.attrib import attr

import subprocess
from path import Path

@attr(linux=True,
      osx=False,
      win=False,
      level=1)
class TestFeedback(unittest.TestCase):
    """Test the feedback of a SCons results"""

    @classmethod
    def setUpClass(cls):
        with open('test.h', 'w') as filehandler:
            filehandler.write("""
#include <string>

namespace test
{
    template<class T, class U>
    class Pair
    {
        public:
            Pair(const std::string& first, const std::string& second)
            { 
                this->first = first;
                this->second = second;
            };

            void swap(const Pair< T, U >& pair)
            { this->first = pair.first; this->second = pair.second; }

        protected:
            T first;
            U second;
    };

    typedef Pair< const double, double > Point;

    enum {
        RED,
        GREEN,
        BLUE
    };

    int color;
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
        autowig.parser.plugin = 'clanglite'
        autowig.generator.plugin = 'boost_python_internal'
        autowig.feedback.plugin = 'edit'
        cls.srcdir = Path('.').abspath()

    def test_with_none_overload_export(self, overload="none"):
        """Test `feedback` with 'none' overload"""

        asg = autowig.AbstractSemanticGraph()

        asg = autowig.parser(asg, [self.srcdir/'test.h'],
                                  ['-x', 'c++', '-std=c++11', '-I' + str(self.srcdir)],
                                  silent = True)

        autowig.controller.plugin = 'default'
        autowig.controller(asg, overload=overload)

        module = autowig.generator(asg, module = self.srcdir/'_module.cpp',
                                     decorator = self.srcdir/'_module.py',
                                     prefix = 'wrapper_')

        from autowig._controller import cleaning
        cleaning(asg)

        module.write()


        s = subprocess.Popen(['scons', 'py'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prev, curr = s.communicate()

        while curr and not prev == curr:
            prev = curr
            if six.PY3:
                curr = curr.decode('ascii', 'ignore')
            code = autowig.feedback(curr, '.', asg)
            if code:
                exec(code, locals())
            s = subprocess.Popen(['scons', 'py'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, curr = s.communicate()

        for filepath in (self.srcdir/'src'/'py').walkfiles():
            if filepath.exists() and filepath.basename().startswith('wrapper_') or filepath.startswith('_module'):
                filepath.remove()

    @attr(level=2)
    def test_with_all_overload_export(self):
        """Test `feedback` with 'all' overload"""
        self.test_with_none_overload_export(overload="all")

    @attr(level=2)
    def test_with_class_overload_export(self):
        """Test `feedback` with 'class' overload"""
        self.test_with_none_overload_export(overload="class")

    @attr(level=2)
    def test_with_namespace_overload_export(self):
        """Test `feedback` with 'namespace' overload"""
        self.test_with_none_overload_export(overload="namespace")
