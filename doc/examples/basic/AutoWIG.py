import os
import autowig
import sys
import pickle
import itertools
import subprocess

asg = autowig.AbstractSemanticGraph()

asg = autowig.parser(asg, [os.path.join(sys.prefix, 'include', 'basic', 'binomial.h'),
                           os.path.join(sys.prefix, 'include', 'basic', 'overload.h')],
                     ['-x', 'c++', '-std=c++11', '-ferror-limit=0', '-I' + os.path.join(sys.prefix, 'include')],
                     bootstrap=1)

asg = autowig.controller(asg)

autowig.generator.plugin = 'boost_python_internal'
wrappers = autowig.generator(asg, module='src/py/_basic.cpp',
                                  decorator='src/py/basic/_basic.py',
                                  closure=False)
wrappers.write()