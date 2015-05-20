from path import path
from ConfigParser import ConfigParser
from clang.cindex import Config, conf, Cursor

if not Config.loaded:
    configpath = path(__file__)
    while len(configpath) > 0 and not str(configpath.name) == 'src':
        configpath = configpath.parent
    configpath = configpath.parent
    configparser = ConfigParser()
    configparser.read(configpath/'metainfo.ini')
    config = dict(configparser.items('libclang'))
    if 'path' in config:
            Config.set_library_path(config['path'])
    elif 'file' in config:
        Config.set_library_file(config['file'])
    else:
        raise IOError('cannot find libclang path or file')

    def is_virtual_method(self):
        """Returns True if the cursor refers to a C++ member function that
        is declared 'virtual'.
        """
        return conf.lib.clang_CXXMethod_isVirtual(self)

    Cursor.is_virtual_method = is_virtual_method
    del is_virtual_method

    def is_pure_virtual_method(self):
        """Returns True if the cursor refers to a C++ member function that
        is declared pure 'virtual'.
        """
        return conf.lib.clang_CXXMethod_isPureVirtual(self)

    Cursor.is_pure_virtual_method = is_pure_virtual_method
    del is_pure_virtual_method

    def is_abstract_record(self):
        """Returns True if the cursor refers to a C++ member function that
        is declared pure 'virtual'.
        """
        return conf.lib.clang_CXXRecord_isAbstract(self)

    Cursor.is_abstract_record = is_abstract_record
    del is_abstract_record

    def is_copyable_record(self):
        """Returns True if the cursor refers to a C++ member function that
        is declared pure 'virtual'.
        """
        return conf.lib.clang_CXXRecord_isCopyable(self)

    Cursor.is_copyable_record = is_copyable_record
    del is_copyable_record
