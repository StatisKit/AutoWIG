"""
"""
from openalea.core.path import path
from vplants.autowig.interface import AccessSpecifier, InterfaceCursor, EnumInterfaceCursor, FunctionInterfaceCursor, UserDefinedTypeInterfaceCursor, TemplateClassInterfaceCursor, ScopeInterfaceCursor
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.display import HTML
import os, stat
import itertools
from mako.template import Template
from mako.lookup import TemplateLookup

__dir__ = path(__file__)
__dir__ = __dir__.parent
lookup = TemplateLookup(directories=[str(__dir__)])

def openfile(filepath):
    if not isinstance(filepath, basestring):
        raise TypeError('`filepath` parameter')
    if not isinstance(filepath, path):
        filepath = path(filepath)
    if filepath.exists():
        os.chmod(filepath, stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    else:
        dirpath = filepath.parent
        if not dirpath.exists():
            dirpath.makedirs()
    return open(filepath, 'w')

def closefile(fileobj):
    if not isinstance(fileobj, file):
        raise TypeError('`filehandler` parameter')
    os.chmod(fileobj.name, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    fileobj.close()

def BoostPython(obj):
    """
    """
    return HTML(highlight(obj._repr_boost_python_(), CppLexer(), HtmlFormatter(full = True)))

class BoostPythonModel(object):
    """
    """

    def __init__(self, scope):
        self.scope = scope

class ClassBoostPythonModel(BoostPythonModel):

    def __init__(self, model, scope=""):
        if not isinstance(model, UserDefinedTypeInterfaceCursor):
            raise TypeError('`model` parameter')
        BoostPythonModel.__init__(self, scope)
        self.spelling = model.spelling
        self.bases = model.bases
        self.pure_virtual = model.pure_virtual
        self.file = model.file
        self.constructors = [c for c in model.constructors if c.access is AccessSpecifier.PUBLIC and not 'hidden' in c.annotations]
        self.methods = []
        self.overloaded_methods = []
        self.fields = model.fields
        black = []
        white = range(len(model.methods))
        while len(white) > 0:
            gray = [white.pop()]
            if model.methods[gray[0]].access is AccessSpecifier.PUBLIC:
                    for w in white:
                        if model.methods[gray[0]].spelling == model.methods[w].spelling:
                            gray.append(w)
                    if len(gray) == 1 and not 'hidden' in model.methods[gray[0]].annotations:
                        self.methods.append(model.methods[gray[0]])
                    else:
                        self.overloaded_methods.append([model.methods[g] for g in gray if not 'hidden' in model.methods[g].annotations])
            white = [w for w in white if not w in gray]
            black.extend(gray)

    def _repr_boost_python_(self):
        _path_ = path(__file__)
        while len(_path_) > 0 and not str(_path_.name) == 'src':
            _path_ = _path_.parent
        _path_ = _path_.parent
        mako = Template(filename=str(_path_/'mako'/'class.mako'))
        return mako.render(model=self)

class ScopeBoostPythonModel(BoostPythonModel):

    def __init__(self, *models, **kwargs):
        if any([not isinstance(model, ScopeInterfaceCursor) for model in models]):
                raise TypeError('`models` parameter')
        BoostPythonModel.__init__(self, scope=dict.pop(kwargs, 'scope', ''))
        if not self.scope == '':
            self.scope += '::'
        self.spelling = models[0].spelling
        if len(models) == 1:
            declarations = models[0].declarations
        else:
            if any([not model.spelling == self.spelling for model in models]):
                raise ValueError('`models` parameter')
            declarations = list(itertools.chain(*[model.declarations for model in models]))
        self.methods = []
        self.overloaded_methods = []
        self.scopes = []
        self.user_defined_types = []
        self.enums = []
        black = []
        white = range(len(declarations))
        while len(white) > 0:
            gray = [white.pop()]
            if isinstance(declarations[gray[0]], UserDefinedTypeInterfaceCursor) and not isinstance(declarations[gray[0]], TemplateClassInterfaceCursor):
                if not 'hidden' in declarations[gray[0]].annotations and not declarations[gray[0]].empty:
                    self.user_defined_types.append(ClassBoostPythonModel(declarations[gray[0]], scope=self.scope))
            elif isinstance(declarations[gray[0]], EnumInterfaceCursor):
                if not 'hidden' in declarations[gray[0]].annotations:
                    self.enums.append(declarations[gray[0]])
            elif isinstance(declarations[gray[0]], (FunctionInterfaceCursor, ScopeInterfaceCursor)):
                for w in white:
                    if isinstance(declarations[w], (FunctionInterfaceCursor, ScopeInterfaceCursor)) and declarations[gray[0]].spelling == declarations[w].spelling:
                            gray.append(w)
                if isinstance(declarations[gray[0]], FunctionInterfaceCursor):
                    if len(gray) == 1 and not 'hidden' in declarations[gray[0]].annotations:
                        self.methods.append(declarations[gray[0]])
                    else:
                        self.overloaded_methods.append([declarations[g] for g in gray if not 'hidden' in declarations[g].annotations])
                        if len(self.overloaded_methods[-1]) == 0:
                            self.overloaded_methods.pop()
                else:
                    if len(gray) == 1 and not 'hidden' in declarations[gray[0]].annotations:
                        self.scopes.append(ScopeBoostPythonModel(declarations[gray[0]], scope=self.scope+declarations[gray[0]].spelling))
                    else:
                        self.scopes.append(ScopeBoostPythonModel(*[declarations[g] for g in gray if not 'hidden' in declarations[g].annotations], scope=self.scope+declarations[gray[0]].spelling))
            white = [w for w in white if not w in gray]
            black.extend(gray)

def read_boost_python(*models, **kwargs):
    """
    """
    return ScopeBoostPythonModel(*models, **kwargs)

def expose_library(library, wrapperpath, *interfaces, **kwargs):
    if not isinstance(library, basestring):
        raise TypeError('`library` parameter')
    if not isinstance(wrapperpath, basestring):
        raise TypeError('`wrapperpath` parameter')
    if not isinstance(wrapperpath, path):
        wrapperpath = path(wrapperpath)
    if not 'pythonpath' in kwargs:
        pythonpath = path(wrapperpath.replace('wrapper/', ''))
    else:
        pythonpath = dict.pop(kwargs, 'pythonpath')
        if not isinstance(pythonpath, basestring):
            raise TypeError('`pythonpath` parameter')
        if not isinstance(pythonpath, path):
            pythonpath = path(pythonpath)
    for namespace in namespaces("", *interfaces).iterkeys():
        namespacepath = path(wrapperpath)
        for directory in namespace.lstrip(library+'::').split('::'):
            namespacepath /= directory
        if not namespacepath.exists():
            namespacepath.makedirs()
    for spelling, functions in functions("", *interfaces).iteritems():
        functionpath = path(wrapperpath)
        for directory in spelling.lstrip(library+'::').split('::'):
            functionpath /= directory
        fileobj = open(functionpath, 'w')
        template = Template(filename=str(__dir__/'functions.mako'), lookup=lookup)
        fileobj.write(template.render(functions=functions, spelling=spelling, library=library))
        fileobj.close()
    for spelling, classobj in classes("", *interfaces).iteritems():
        classpath = path(wrapperpath)
        for directory in spelling.lstrip(library+'::').split('::'):
            classpath /= directory
        fileobj = open(classpath, 'w')
        template = Template(filename=str(__dir__/'class.mako'), lookup=lookup)
        fileobj.write(template.render(
            constructors = constructors(spelling, classobj),
            enums = enums(spelling, classobj),
            methods = methods(spelling, classobj),
            spelling=spelling, library=library))
        fileobj.close()



def write_boost_python(wrapperpath, model, library, **kwargs):
    """
    """
    if not isinstance(wrapperpath, basestring):
        raise TypeError('`wrapperpath` parameter')
    if not isinstance(wrapperpath, path):
        wrapperpath = path(wrapperpath)
    if not 'pythonpath' in kwargs:
        pythonpath = path(wrapperpath.replace('wrapper/', ''))
    else:
        pythonpath = dict.pop(kwargs, 'pythonpath')
        if not isinstance(pythonpath, basestring):
            raise TypeError('`pythonpath` parameter')
        if not isinstance(pythonpath, path):
            pythonpath = path(pythonpath)
    if not isinstance(model, ScopeBoostPythonModel):
        raise TypeError('`model` parameter')
    if not isinstance(library, basestring):
        raise TypeError('`library` parameter')
    if not wrapperpath.exists():
        wrapperpath.makedirs()
    if not pythonpath.exists():
        pythonpath.makedirs()
    for m in model.methods:
        template = Template(filename=str(__dir__/'function-cpp.mako'), lookup=lookup)
        f = openfile(wrapperpath/m.spelling+'.cpp')
        f.write(template.render(model=m, scope=model.scope, library=library))
        closefile(f)
        template = Template(filename=str(__dir__/'function-py.mako'), lookup=lookup)
        scopepath = path(pythonpath)
        for s in model.scope.split('::'):
            scopepath /= ''.join('_' + c.lower() if c.isupper() else c for c in s).lstrip('_')
        f = openfile(scopepath/'__'+m.spelling+'.py')
        f.write(template.render(model=m, library=library))
        closefile(f)
    for m in model.overloaded_methods:
        template = Template(filename=str(__dir__/'functions-cpp.mako'), lookup=lookup)
        f = openfile(wrapperpath/m[0].spelling+'.cpp')
        f.write(template.render(models=m, scope=model.scope, library=library))
        closefile(f)
    for e in model.enums:
        template = Template(filename=str(__dir__/'enums-cpp.mako'), lookup=lookup)
        f = openfile(wrapperpath/e.spelling+'.cpp')
        f.write(template.render(model=e, scope=model.scope, library=library))
        closefile(f)
        template = Template(filename=str(__dir__/'enums-py.mako'), lookup=lookup)
        scopepath = path(pythonpath)
        for s in model.scope.split('::'):
            scopepath /= ''.join('_' + c.lower() if c.isupper() else c for c in s).lstrip('_')
        f = openfile(scopepath/'__'+e.spelling+'.py')
        f.write(template.render(model=e))
        closefile(f)
    for c in model.user_defined_types:
        template = Template(filename=str(__dir__/'class-cpp.mako'), lookup=lookup)
        f = openfile(wrapperpath/''.join('_' + char.lower() if char.isupper() else char for char in c.spelling).lstrip('_')+'.cpp')
        f.write(template.render(model=c, library=library))
        closefile(f)
        template = Template(filename=str(__dir__/'class-py.mako'), lookup=lookup)
        scopepath = path(pythonpath)
        for s in model.scope.split('::'):
            scopepath /= ''.join('_' + c.lower() if c.isupper() else c for c in s).lstrip('_')
        f = openfile(scopepath/'__'+''.join('_' + char.lower() if char.isupper() else char for char in c.spelling).lstrip('_')+'.py')
        f.write(template.render(model=c, library=library))
        closefile(f)
    for s in model.scopes:
        write_boost_python(wrapperpath/model.scope, s, library=library)
    if 'stl_containers' in kwargs:
        template = Template(filename=str(__dir__/'stl_containers-cpp.mako'))
        f = openfile(wrapperpath/'stl_containers.cpp')
        f.write(template.render(library=library, **dict.pop(kwargs, 'stl_containers')))
        closefile(f)

#def boost_python(filepath, dirpath, **kwargs):
#    """
#    """
#    if not isinstance(dirpath, basestring):
#        raise TypeError('`dirpath` parameter')
#    dirpath = path(dirpath)
#    if not dirpath.exists:
#        dirpath.mkdir()
#    return visit_declarations(interface_model(filepath, **kwargs).declarations, dirpath, "::")
#
#def visit_declarations(declarations, namespace):
#    files =
#    if not dirpath.exists:
#        dirpath.mkdir()
#    for declaration in declarations:
#        if isinstance(declaration, FunctionModel):
#            pass
#        elif isinstance(declaration, ClassModel):
#            pass
#        elif isinstance(declaration, EnumModel):
#            pass
#        elif isinstance(declaration, NamespaceModel):
#            visit_declarations(declaration.declarations, namespace/declaration.name)
#
#def expose_function(declaration, dirpath):
#    filepath = dirpath/declaration.name
#    filehandler = open(filepath, 'w')
#    filehandler.file.write('#include <boost/python.hpp>\n')
#    filehandler.file.write('#include <>\n\n')
#    filehandler.file.write('boost::python::BOOST_PYTHON_MODULE(_'+declaration.name+')\n{\n')
#    filehandler.file.write('\tboost::python::def(\"'+declaration.name+'\", '+declaration.name+');\n')
#    filehandler.file.write('}\n\nvoid init_bindings()\n{\n\tPy_initialize();\n\tinit_'+declaration.name+'();\n}')
#    filehandler.close()
