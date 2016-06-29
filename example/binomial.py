from autowig import autowig
autowig.scons('test', '-c')

asg = autowig.AbstractSemanticGraph()
autowig.parser.plugin = 'pyclanglite'
autowig.parser(asg, ['./test/binomial/binomial.h'], ['-x', 'c++', '-std=c++11'])

autowig.controller.plugin = 'default'
autowig.controller(asg)

autowig.generator.plugin = 'boost_python_internal'
wrappers = autowig.generator(asg, module='./test/binomial/module.cpp',
        decorator=None,
        prefix='wrapper_')

for wrapper in wrappers:
    wrapper.write()

print autowig.scons('test')

import sys
import os

try:
    from test.binomial import *
except ImportError:
    import autowig
    from path import path
    libpath = path(autowig.__path__[0])
    while not libpath.basename() == 'src':
        libpath = libpath.parent
    libpath = libpath.parent
    libpath = libpath/'example'/'test'/'binomial'
    libpath = libpath.abspath()
    if sys.platform == 'win32':
        os.environ['PATH'] += ':' + libpath
    elif sys.platform == 'darwin':
        os.environ['DYLD_LIBRARY_PATH'] += ':' + libpath
    else:
        os.environ['LD_LIBRARY_PATH'] += ':' + libpath
    execmd = sys.executable
    argv = sys.argv + [os.environ]
    os.execle(execmd, execmd, *argv)

from test.binomial import *

binomial = BinomialDistribution(1, .5)
binomial.pmf(0)
binomial.pmf(1)
binomial.n = 0
binomial.pmf(0)
binomial.set_pi(1.1)
