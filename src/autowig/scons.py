"""
"""

from pygments import highlight
from pygments.lexers import BashSessionLexer
from pygments.formatters import HtmlFormatter
from path import path
import os
import subprocess
import parse

__all__ = ['scons']

class ShellSession(object):

    def __init__(self, out, err, lexer=None):
        self.out = out
        self.err = str(err)
        if lexer is None:
            self.lexer = BashSessionLexer()
        else:
            self.lexer = lexer

    def __iadd__(self, session):
        self.out += session.out
        self.err += str(session.err)
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
    if not isinstance(directory, path):
        directory = path(directory)
    directory = directory.abspath()
    s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=directory,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = s.communicate()
    return ShellSession(out, err, **kwargs)

def boost_python_emitter(target, source, env):
    if True:#'srcnode' in env:
        target = [target.srcnode() for target in target]
    return target, source

def boost_python_action(target, source, env):

    from .autowig import  AbstractSemanticGraph, parser, controller, generator

    asg = AbstractSemanticGraph()

    kwargs = dict() # TODO

    if 'autowig_parser' in env:
        parser.plugin = env['autowig_parser']
    parser(asg, [str(src) for src in source], flags=env.subst('$CPPFLAGS $CFLAGS $CCFLAGS $CXXFLAGS').split(), **kwargs) # KWARGS

    if 'autowig_controller' in env:
        controller.plugin = env['autowig_controller']
    controller(asg)

    if 'autowig_generator' in env:
        generator.plugin = env['autowig_generator']
    else:
        generator.plugin = 'boost_python_internal'
    wrappers = generator(asg, module=target[1], decorator=target[0], **kwargs)

    for wrapper in wrappers: # PATTERN, CLOSURE, PREFIX
        wrapper.write(**kwargs) # DATABASE

    return 0

def boost_python_string(target, source, env):
    return "autowig: Generating Boost.Python wrappers"""

def boost_python_builder(env):
    """
    """
    boost_python_builder = env.Builder(action= env.Action(boost_python_action, boost_python_string), emitter=boost_python_emitter)#, target_factory=env.fs.Dir)
    env.Append(BUILDERS = {'BoostPython' : boost_python_builder})
