from pygments import highlight
from pygments.lexers import ShellSessionLexer
from pygments.formatters import HtmlFormatter
import subprocess

from .asg import FileProxy, AbstractSemanticGraph

__all__ = []

class SConscriptProxy(FileProxy):

    language = 'py'

    def __call__(self, *args, **kwargs):
        s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=self.parent.globalname, stdout=subprocess.PIPE)
        return ShellSession(''.join(s.stdout.readlines()), **kwargs)

class ShellSession(object):

    def __init__(self, session, lexer=None):
        self.session = session
        if lexer is None:
            self.lexer = ShellSessionLexer()
        else:
            self.lexer = lexer

    def __str__(self):
        return self.session

    def _repr_html_(self):
        return highlight(str(self), self.lexer, HtmlFormatter(full = True))

def add_sconscript(self, directory):
    dirnode = self.add_directory(directory)
    return self.add_file(directory+'SConscript', proxy=SConscriptProxy)

AbstractSemanticGraph.add_sconscript = add_sconscript
del add_sconscript

def scons(self, *args, **kwargs):
    session = ""
    for node in self.files():
        if isinstance(node, SConscriptProxy):
            session += node(*args).session
    return ShellSession(session, **kwargs)

AbstractSemanticGraph.scons = scons
del scons
