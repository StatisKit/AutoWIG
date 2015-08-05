from pygments import highlight
from pygments.lexers import ShellSessionLexer
from pygments.formatters import HtmlFormatter
from abc import ABCMeta
import subprocess

from .asg import FileProxy, AbstractSemanticGraph
from .boost_python_back_end import BoostPythonModuleFileProxy

__all__ = []

class SConstructProxy(FileProxy):

    _language = 'py'

    def __call__(self, *args, **kwargs):
        s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=self.parent.globalname,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = s.communicate()
        session = ShellSession(out, err, **kwargs)
        return session

class ShellSession(object):

    def __init__(self, out, err, lexer=None):
        self.out = out
        self.err = err
        if lexer is None:
            self.lexer = ShellSessionLexer()
        else:
            self.lexer = lexer

    def __iadd__(self, session):
        self.out += session.out
        self.err += session.err
        return self

    @property
    def has_succeded(self):
        return self.err == ''

    def __str__(self):
        if self.has_succeded:
            return self.out
        else:
            return self.out + self.err

    def _repr_html_(self):
        return highlight(str(self), self.lexer, HtmlFormatter(full = True))

def add_sconstruct(self, directory):
    dirnode = self.add_directory(directory)
    return self.add_file(dirnode.globalname + 'SConstruct', proxy=SConstructProxy, _clean=False)

AbstractSemanticGraph.add_sconstruct = add_sconstruct
del add_sconstruct

def sconstructs(self, pattern=None):
    class _MetaClass(object):
        __metaclass__ = ABCMeta
    _MetaClass.register(SConstructProxy)
    metaclass = _MetaClass
    return self.nodes(pattern, metaclass=metaclass)

AbstractSemanticGraph.sconstructs = sconstructs
del sconstructs

class SConscriptProxy(FileProxy):

    _language = 'py'

def add_sconscript(self, **kwargs):
    pydir = kwargs.pop('pydir', '../' + self.localname.replace(self.suffix, ''))
    env = kwargs.pop('env', 'env')
    sconscript = self.asg.add_file(self.parent + 'SConscript')
    content = 'Import("' + env + ')\n' + env + ' = ' + env + '.Clone()\n'
    content += 'sources = [' + ',\n           '.join(export.localname for export in self.exports if not export.is_empty) + ']\n'
    content += 'target = _' + self.localname.replace(self.suffix, '')
    dirnode = self.add_directory(pydir)


def sconscripts(self, pattern=None):
    class _MetaClass(object):
        __metaclass__ = ABCMeta
    _MetaClass.register(SConscriptProxy)
    metaclass = _MetaClass
    return self.nodes(papydirttern, metaclass=metaclass)

AbstractSemanticGraph.sconscripts = sconscripts
del sconscripts

def scons(self, *args, **kwargs):
    session = ShellSession("", "")
    for node in self.files():
        if isinstance(node, SConstructProxy):
            session += node(*args)
            if not session.has_succeded:
                break
    return session

AbstractSemanticGraph.scons = scons
del scons
