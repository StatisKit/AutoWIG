"""
"""

from pygments import highlight
from pygments.lexers import BashSessionLexer
from pygments.formatters import HtmlFormatter
import subprocess

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

def boost_python_emitter(target, source, env):
    if True:#'srcnode' in env:
        target = [target.srcnode() for target in target]
    env.SetDefaut('autowig_decorator_prefix', '_')
    env.SetDefaut('autowig_export_prefix', '_')
    env.SetDefaut('autowig_module_prefix', '__')
    return [env.File(target[0].abspath + '/' + env['autowig_decorator_prefix'] + env['autowig_libname'] + '.py'), env.File(target[1].abspath + '/' +env['autowig_module_prefix'] + env['autowig_libname'] + '.cpp')], source

def boost_python_action(target, source, env):

    from .autowig import  AbstractSemanticGraph, parser, controller, generator, boost_python_call_policy, boost_python_held_type, boost_python_export, boost_python_module, boost_python_decorator

    if 'autowig_controller' in env:
        controller.plugin_manager = env['autowig_controller']
    if 'autowig_bp_call_policy' in env:
        boost_python_call_policy.plugin_manager = env['autowig_bp_call_policy']
    if 'autowig_bp_held_type' in env:
        boost_python_held_type.plugin_manager = env['autowig_bp_held_type']
    if 'autowig_bp_export' in env:
        boost_python_export.plugin_manager = env['autowig_bp_export']
    if 'autowig_bp_module' in env:
        boost_python_module.plugin_manager = env['autowig_bp_module']
    if 'autowig_bp_decorator' in env:
        boost_python_decorator.plugin_manager = env['autowig_bp_decorator']

    generator.plugin_manager = 'boost_python'

    asg = AbstractSemanticGraph()

    kwargs = dict() # TODO

    print env['_CCCOMCOM']
    print env.subst('$CPPFLAGS $CFLAGS $CCFLAGS $CXXFLAGS')

    parser(asg,
            [str(src) for src in source[1:]],
            flags=env.subst('$CPPFLAGS $CFLAGS $CCFLAGS $CXXFLAGS').split(),
            **kwargs) # KWARGS
    controller(asg)
    generator(asg,
            target[1],
            target[0],
            **kwargs) # PATTERN, CLOSURE, PREFIX

    for export in asg.boost_python_exports(target[1].get_dir().abspath + '/.*' + target[1].get_suffix()):
        export.write(**kwargs) # DATABASE
    asg[target[0].abspath].write(**kwargs) # DATABASE

    return 0

def boost_python_builder(env):
    """
    """
    boost_python_builder = env.Builder(action=boost_python_action, emitter=boost_python_emitter, target_factory=env.fs.Dir)
    env.Append(BUILDERS = {'BoostPython' : boost_python_builder})
