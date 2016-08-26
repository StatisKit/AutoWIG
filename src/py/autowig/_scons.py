"""
"""

from pygments import highlight
from pygments.lexers import BashSessionLexer
from pygments.formatters import HtmlFormatter
from path import path
import subprocess

__all__ = ['scons']

class ShellSession(object):

    def __init__(self, out, err, lexer=BashSessionLexer()):
        self.out = out
        self.err = str(err)
        self.lexer = lexer

    def __str__(self):
        return self.out + self.err

def scons(directory, *args, **kwargs):
    if not isinstance(directory, path):
        directory = path(directory)
    directory = directory.abspath()
    if kwargs.pop('out', True):
        kwargs['stdout'] = subprocess.PIPE
    if kwargs.pop('err', True):
        kwargs['stderr'] = subprocess.PIPE
    lexer = kwargs.pop('lexer', None)
    s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=directory, **kwargs)
    out, err = s.communicate()
    return ShellSession(out, err, lexer=lexer)
