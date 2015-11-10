from pygments import highlight
from pygments.lexers import ShellSessionLexer
from pygments.formatters import HtmlFormatter
from abc import ABCMeta
import subprocess
from mako.template import Template

from .asg import FileProxy, AbstractSemanticGraph
from .boost_python_back_end import BoostPythonModuleFileProxy

__all__ = ['scons']

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

def scons(self, pattern='.*', *args, **kwargs):
    session = ShellSession("", "")
    for node in self.sconstructs(pattern):
        session += node(*args)
        if not session.has_succeded:
            break
    return session

AbstractSemanticGraph.scons = scons
del scons

def scons(directory, *args, **kwargs):
    s = subprocess.Popen(['scons']+[arg for arg in args] , cwd=directory,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = s.communicate()
    session = ShellSession(out, err, **kwargs)
    return session

class BoostPythonSConscriptProxy(SConscriptProxy):
    """
    """

    # parent, env, prepend, append, module, target, alias
    CONTENT = Template(text=r"""\
# -*-python-*-

import os

Import("${env}")

local_${env} = ${env}.Clone()

% if not prepend is None:
local_${env}.Prepend(${(',\\n        ' + ' ' * len(env) + "        ").join(key + " = ['" + "', '".join(value for value in values) + "']" for key, values in prepend.iteritems())})
% endif
% if not append is None:
local_${env}.Append(${(',\\n        ' + ' ' * len(env) + "        ").join(key + " = ['" + "', '".join(value for value in values) + "']" for key, values in append.iteritems())})
% endif

sources = ["${'",\\n           "'.join(source.relativename(directory) for source in sources if not source.is_empty)}"]

target = str(local_${env}.Dir("${target.relativename(directory)}")\
% if not build:
.srcnode()\
% endif
)

kwargs = dict()

if os.name == 'nt':
    kwargs['SHLIBSUFFIX'] = '.pyd'
else:
    kwargs['SHLIBSUFFIX'] = '.so'

kwargs['SHLIBPREFIX'] = ''

if local_${env}['compiler'] == 'msvc' and '8.0' in local_${env}['MSVS_VERSION']:
    kwargs['SHLINKCOM'] = [local_${env}['SHLINKCOM'],
    'mt.exe -nologo -manifest ${'${'}TARGET${'}'}.manifest -outputresource:$TARGET;2']

if os.name == 'nt':
    # Fix bug with Scons 0.97, Solved in newer versions.
    alias = local_${env}.SharedLibrary(target, sources, **kwargs)
elif os.sys.platform == 'darwin':
    alias = local_${env}.LoadableModule(target, sources, LDMODULESUFFIX='.so',
                           FRAMEWORKSFLAGS = '-flat_namespace -undefined suppress', **kwargs)
else:
    alias = local_${env}.LoadableModule(target, sources, **kwargs)

Alias("${alias}", alias)
""")

def get_env(self):
    if not hasattr(self, '_env'):
        return 'env'
    else:
        return self._env

def set_env(self, env):
    self.asg._nodes[self.node]['_env'] = env

def del_env(self):
    self.asg._nodes[self.node].pop('_env', 'build')

BoostPythonSConscriptProxy.env = property(get_env, set_env, del_env)
del get_env, set_env, del_env

def get_build(self):
    if not hasattr(self, '_build'):
        return False
    else:
        return self._build

def set_build(self, build):
    self.asg._nodes[self.node]['_build'] = build

def del_build(self):
    self.asg._nodes[self.node].pop('_build', 'build')

BoostPythonSConscriptProxy.build = property(get_build, set_build, del_build)
del get_build, set_build, del_build

def get_prepend(self):
    if hasattr(self, '_prepend'):
        return self._prepend

def set_prepend(self, prepend):
    self.asg._nodes[self.node]['_prepend'] = prepend


def del_prepend(self):
    self.asg._nodes[self.node].pop('_prepend', None)

BoostPythonSConscriptProxy.prepend = property(get_prepend, set_prepend, del_prepend)
del get_prepend, set_prepend, del_prepend

def get_append(self):
    if hasattr(self, '_append'):
        return self._append

def set_append(self, append):
    self.asg._nodes[self.node]['_append'] = append


def del_append(self):
    self.asg._nodes[self.node].pop('_append', None)

BoostPythonSConscriptProxy.append = property(get_append, set_append, del_append)
del get_append, set_append, del_append

def get_alias(self):
    if not hasattr(self, '_alias'):
        return 'build'
    else:
        return self._alias

def set_alias(self, alias):
    self.asg._nodes[self.node]['_alias'] = alias

def del_alias(self):
    self.asg._nodes[self.node].pop('_alias', 'build')

BoostPythonSConscriptProxy.alias = property(get_alias, set_alias, del_alias)
del get_alias, set_alias, del_alias

#def get_sources(self):
#    if hasattr(self, '_sources'):
#        return self._sources
#    else:
#        return []
#
#def set_sources(self, sources):
#    self.asg._nodes[self.node]['_sources'] = sources
#
#def del_sources(self):
#    self.asg._nodes[self.node].pop('_sources', 'build')
#
#BoostPythonSConscriptProxy.sources = property(get_sources, set_sources, del_sources)
#del get_sources, set_sources, del_sources

def boost_python_back_end(asg, pattern='.*', proxy=BoostPythonSConscriptProxy):
    for bpm in asg.boost_python_modules(pattern=pattern):
        sconsscript = self.asg.add_file(bpm.parent.globalname + 'SConscript',
                proxy = proxy,
                module = bpm.node)
