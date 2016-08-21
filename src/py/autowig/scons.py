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

    def _repr_html_(self):
        return highlight(str(self), self.lexer, HtmlFormatter(full = True))

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

def boost_python_action(target, source, env, **kwargs):

    from .autowig import  AbstractSemanticGraph, parser, controller, generator

    asg = AbstractSemanticGraph()

    if 'autowig_parser' in env:
        parser.plugin = env['autowig_parser']
    parser(asg, [str(src) for src in source],
           flags=env.subst('$CPPFLAGS $CFLAGS $CCFLAGS $CXXFLAGS').split() + ['-I' + cpppath.strip() for cpppath in env.subst('$CPPPATH').split()],
           env=env)

    if 'autowig_controller' in env:
        controller.plugin = env['autowig_controller']
    controller(asg,
               env=env)

    if 'autowig_generator' in env:
        generator.plugin = env['autowig_generator']
    else:
        generator.plugin = 'boost_python_internal'
    wrappers = generator(asg, module=target[1], decorator=target[0], env=env)

    for wrapper in wrappers:
        wrapper.write(**kwargs)

    print 'autowig: Done generating Boost.Python wrappers'
    return 0

def boost_python_string(target, source, env):
    return "autowig: Generating Boost.Python wrappers"""

def boost_python_builder(env):
    """
    """
    boost_python_builder = env.Builder(action=env.Action(boost_python_action, boost_python_string))
    env.Append(BUILDERS = {'BoostPython' : boost_python_builder})
