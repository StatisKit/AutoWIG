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
    if kwargs.pop('out', True):
        kwargs['stdout'] = subprocess.PIPE
    if kwargs.pop('err', True):
        kwargs['stderr'] = subprocess.PIPE
    lexer = kwargs.pop('lexer', None)
    s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=directory, **kwargs)
    out, err = s.communicate()
    return ShellSession(out, err, lexer=lexer)

def boost_python_emitter(target, source, **kwargs):
    if kwargs.get('variantdir', False):
        target = [target.srcnode() for target in target]
    return target, source

def boost_python_action(target, source, env, **kwargs):

    from .autowig import  AbstractSemanticGraph, parser, controller, generator
    import time

    start = time.time()

    asg = AbstractSemanticGraph()

    if 'autowig_parser' in env:
        parser.plugin = env['autowig_parser']
    print env.subst('$CPPFLAGS $CFLAGS $CCFLAGS $CXXFLAGS').split() + ['-I' + cpppath.strip() for cpppath in env.subst('$CPPPATH').split()]
    parser(asg, [str(src) for src in source], flags=env.subst('$CPPFLAGS $CFLAGS $CCFLAGS $CXXFLAGS').split() + ['-I' + cpppath.strip() for cpppath in env.subst('$CPPPATH').split()], env=env) # KWARGS
    parsing = time.time()

    if 'autowig_controller' in env:
        controller.plugin = env['autowig_controller']
    controller(asg)
    controlling = time.time()

    if 'autowig_generator' in env:
        generator.plugin = env['autowig_generator']
    else:
        generator.plugin = 'boost_python_internal'
    wrappers = generator(asg, module=target[1], decorator=target[0], env=env)
    generating = time.time()

    for wrapper in wrappers: # PATTERN, CLOSURE, PREFIX
        wrapper.write(**kwargs) # DATABASE
    writing = time.time()

    if 'autowig_verbose' in env:
        verbose = env['autowig_verbose']
    else:
        verbose = True
    if verbose:
        counts = dict()
        from .asg import NodeProxy
        from .tools import subclasses, strdiff

        counts = {cls.__name__ : 0 for cls in subclasses(NodeProxy)}

        from .boost_python_generator import BoostPythonExportFileProxy

        for wrapper in wrappers:
            if isinstance(wrapper, BoostPythonExportFileProxy):
                for dcl in wrapper.declarations:
                    counts[dcl.__class__.__name__] += 1

        from .tools import camel_case_to_lower, strdiff
        summary = []
        for count in counts:
            if counts[count] > 0:
                summary.append(camel_case_to_lower(count).rstrip('_proxy').replace('_', ' ').capitalize() + ': ' + str(counts[count]))
        summary.append('Parsing: ' + strdiff(parsing - start))
        summary.append('Controlling: ' + strdiff(controlling - parsing))
        summary.append('Generating: ' + strdiff(generating - controlling))
        summary.append('Writing: ' + strdiff(writing - generating))
        summary.append('Total: ' + strdiff(writing - start) + 's')
        print 'autowig: Done generating Boost.Python wrappers\n         ' + '\n         '.join(summary)
    return 0

def boost_python_string(target, source, env):
    return "autowig: Generating Boost.Python wrappers"""

def boost_python_builder(env):
    """
    """
    boost_python_builder = env.Builder(action=env.Action(boost_python_action, boost_python_string), emitter=boost_python_emitter)
    env.Append(BUILDERS = {'BoostPython' : boost_python_builder})
