"""
"""

from pygments import highlight
from pygments.lexers import BashSessionLexer
from pygments.formatters import HtmlFormatter
import subprocess

from .asg import  AbstractSemanticGraph

__all__ = ['scons']

class ShellSession(object):

    def __init__(self, out, err, lexer=None):
        self.out = out
        self.err = err
        if lexer is None:
            self.lexer = BashSessionLexer()
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

def scons(directory, *args, **kwargs):
    s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=directory,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = s.communicate()
    session = ShellSession(out, err, **kwargs)
    return session

def boost_python_emitter(*args, **kwargs):
    pass

def boost_python_builder(*args, **kwargs):
    pass
