from autowig import autowig
autowig.scons('test', '-c')

asg = autowig.AbstractSemanticGraph()
autowig.parser.plugin = 'pyclanglite'
autowig.parser(asg, ['./test/binomial/foo.h'], ['-x', 'c++', '-std=c++11'])

from autowig.doxygen2sphinx import doxygen_parser, doxygen2sphinx_documenter
doxygen_parser(asg.nodes('::BinomialDistribution::set_pi::.*').pop())

doxygen2sphinx_documenter(asg.nodes('::BinomialDistribution::set_pi::.*').pop())

autowig.controller.plugin = 'default'
autowig.controller(asg)

autowig.generator.plugin = 'boost_python'
autowig.generator(asg,'./test/binomial/bar.cpp',
                  None, prefix='bar_')

module = asg['./test/binomial/bar.cpp']
module.write()
for export in module.exports:
    export.write()

autowig.scons('test')

import sys
import os

from autowig import autowig
autowig.scons('test')

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

    python = sys.executable
    argv = sys.argv + [os.environ]
    os.execle(python, python, *argv)

from test.binomial import *
binomial = BinomialDistribution(1, .5)
binomial.pmf(0)
binomial.pmf(1)
binomial.n = 0
binomial.pmf(0)
binomial.set_pi(1.1)

print autowig.documenter(asg.nodes('::BinomialDistribution::set_pi::.*').pop(), False)
