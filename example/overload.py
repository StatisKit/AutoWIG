from autowig import autowig
autowig.scons('test', '-c')

asg = autowig.AbstractSemanticGraph()
autowig.parser.plugin = 'pyclanglite'
autowig.parser(asg, ['./test/overload/foo.h'], ['-x', 'c++', '-std=c++11'])

#print autowig.documenter(asg['struct ::Overload'], False)

autowig.controller.plugin = 'default'
autowig.controller(asg)

autowig.generator.plugin = 'boost_python'
autowig.generator(asg,'./test/overload/bar.cpp',
                  None, prefix='bar_')

#print autowig.documenter(asg['struct ::Overload'], False)

module = asg['./test/overload/bar.cpp']
module.write()
for export in module.exports:
    export.write()

autowig.scons('test')

import sys
import os

try:
    from test.overload import *
except ImportError:
    import autowig
    from path import path
    libpath = path(autowig.__path__[0])
    while not libpath.basename() == 'src':
        libpath = libpath.parent
    libpath = libpath.parent
    libpath = libpath/'example'/'test'/'overload'
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

from test.overload import *
overload = Overload()
overload.staticness(overload)
Overload.staticness(overload, 0)
overload.staticness(overload, 0)
overload.constness()
overload.nonconstness()
overload?
