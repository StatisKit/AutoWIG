"""
"""
from vplants import autowig
from openalea.core.path import path
from clang import cindex
from ConfigParser import ConfigParser

__path__ = path(autowig.__path__[0])
while len(__path__) > 0 and not str(__path__.name) == 'src':
    __path__ = __path__.parent
__path__ = __path__.parent

configparser = ConfigParser()
configparser.read(__path__/'metainfo.ini')
config = dict(configparser.items('libclang'))

if 'path' in config:
    cindex.Config.set_library_path(config['path'])
elif 'file' in config:
    cindex.Config.set_library_file(config['file'])
index = cindex.Index.create()
