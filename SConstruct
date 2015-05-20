# vim: syntax=python

import os
from fnmatch import fnmatch

pj = os.path.join

from openalea.sconsx import config, environ

from SCons.Script.SConscript import DefaultEnvironmentCall
from SCons.Node.FS import Dir

#Alias = DefaultEnvironmentCall("Alias")

from path import path

def walkfiles(self, pattern=None, on_memory=True, on_disk=True):
    filenames = []
    if on_memory:
        def func(arg, dirname, fnames):
            filenames.extend([dirname.abspath+os.path.sep+fname for fname in fnames if not pattern or fnmatch(fname, pattern)])
        self.walk(func, None)
    if on_disk:
        dirpath = path(self.abspath)
        filenames += [str(filename) for filename in dirpath.walkfiles(pattern)]
    return sorted(set(filenames))

Dir.walkfiles = walkfiles

def walkdirs(self, pattern=None, on_memory=True, on_disk=True):
    dirnames = []
    if on_memory:
        def func(arg, dirname, fnames):
            if dirname.isdir() and not pattern or fnmatch(dirname, pattern):
                dirnames.append(dirname)
        self.walk(func, None)
    if on_disk:
        dirpath = path(self.abspath)
        dirnames += [self.Dir(dirname.replace(self.abspath+os.path.sep, '')) for dirname in dirpath.walkdirs(pattern)]
    return sorted(set(dirnames))

Dir.walkdirs = walkdirs

ALEASolution = config.ALEASolution

SConsignFile()

options = Variables(['../options.py', 'options.py'], ARGUMENTS)
options.Add(BoolVariable('with_headache', 'Add files header', False))

tools = ['boost_python']

env = ALEASolution(options, tools)

env.AppendUnique(CXXFLAGS=["-std=c++0x"])

#env['_LIBFLAGS'] = '-Wl,--start-group ' + env['_LIBFLAGS'] + ' -Wl,--end-group' 

env["libname"] = "autowig"
env["static"] = False

# Set build directory
prefix = env['build_prefix']
#SConscript(pj(prefix,"src/cpp/SConscript"), exports="env")
SConscript(pj(prefix,"src/boost_python/SConscript"), exports="env")
#SConscript(pj(prefix,"src/python/SConscript"), exports="env")

Default("build")
