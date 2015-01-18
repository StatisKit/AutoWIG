"""
"""

from openalea.core.path import path
from index import index
from ConfigParser import ConfigParser
from types import ModuleType

def parse(mod):
    """
    """
    if not isinstance(mod, ModuleType):
        raise TypeError('`mod` parameter')
    __path__ = mod.__path__
    if isinstance(__path__, Sequence):
        if len(__path__) > 1:
            raise ValueError('`mod` parameter')
        __path__ = __path__[0]
    if not isinstance(__path__, basestring):
        raise ValueError('`mod` parameter')
    __path__ = path(__path__)

    clang = ['-x', 'c++']

    configparser = ConfigParser()
    configparser.read(__path__/'metainfo.ini')
    try:
        config = dict(configparser.items('CXXFLAGS'))

        if 'std' in config:
            clang.append('-std='+config['std'])
    except:
        pass

    clang.append('-D__CODE_GENERATOR__')
    for i in (__path__/'src'/'cpp').walkfiles('*.h'):
        yield index.parse(str(i), clang)

