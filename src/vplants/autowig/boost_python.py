"""
"""
from openalea.core.path import path
from vplants.autowig.interface import AccessSpecifier, InterfaceModel, EnumInterfaceModel, FunctionInterfaceModel, UserDefinedTypeInterfaceModel, TemplateClassInterfaceModel, ScopeInterfaceModel
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.display import HTML
from mako.template import Template
__makopath__ = path(__file__)
while len(__makopath__) > 0 and not str(__makopath__.name) == 'src':
    __makopath__ = __makopath__.parent
__makopath__ = __makopath__.parent/'mako'

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
        if not isinstance(model, UserDefinedTypeInterfaceModel):
            raise TypeError('`model` parameter')
        BoostPythonModel.__init__(self, scope)
        self.spelling = model.spelling
        self.bases = model.bases
        self.pure_virtual = model.pure_virtual
        self.file = model.file
        if not self.pure_virtual:
            self.constructors = [c for c in model.constructors if c.access is AccessSpecifier.PUBLIC]
        self.methods = []
        self.overloaded_methods = []
        black = []
        white = range(len(model.methods))
        while len(white) > 0:
            gray = [white.pop()]
            if model.methods[gray[0]].access is AccessSpecifier.PUBLIC:
                for w in white:
                    if model.methods[gray[0]].spelling == model.methods[w].spelling:
                        gray.append(w)
            if len(gray) == 1:
                self.methods.append(model.methods[gray[0]])
            else:
                self.overloaded_methods.append([model.methods[g] for g in gray])
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
        if any([not isinstance(model, ScopeInterfaceModel) for model in models]):
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
        self.classes = []
        self.enums = []
        black = []
        white = range(len(declarations))
        while len(white) > 0:
            gray = [white.pop()]
            if isinstance(declarations[gray[0]], UserDefinedTypeInterfaceModel) and not isinstance(declarations[gray[0]], TemplateClassInterfaceModel):
                self.classes.append(ClassBoostPythonModel(declarations[gray[0]], scope=self.scope+self.spelling))
            elif isinstance(declarations[gray[0]], EnumInterfaceModel):
                self.enums.append(declarations[gray[0]])
            elif isinstance(declarations[gray[0]], (FunctionInterfaceModel, ScopeInterfaceModel)):
                for w in white:
                    if isinstance(declarations[w], (FunctionInterfaceModel, ScopeInterfaceModel)) and declarations[gray[0]].spelling == declarations[w].spelling:
                        gray.append(w)
                if isinstance(declarations[gray[0]], FunctionInterfaceModel):
                    if len(gray) == 1:
                        self.methods.append(declarations[gray[0]])
                    else:
                        self.overloaded_methods.append([declarations[g] for g in gray])
                else:
                    if len(gray) == 1:
                        self.scopes.append(ScopeBoostPythonModel(declarations[gray[0]], scope=self.scope+declarations[gray[0]].spelling))
                    else:
                        self.scopes.append(ScopeBoostPythonModel(*[declarations[g] for g in gray], scope=self.scope+declarations[gray[0]].spelling))
            white = [w for w in white if not w in gray]
            black.extend(gray)

def read_boost_python(*models, **kwargs):
    """
    """
    return ScopeBoostPythonModel(*models, **kwargs)

def write_boost_python(wrapperpath, model, **kwargs):
    """
    """
    if not isinstance(wrapperpath, basestring):
        raise TypeError('`wrapperpath` parameter')
    if not isinstance(wrapperpath, path):
        wrapperpath = path(wrapperpath)
    if not isinstance(model, ScopeBoostPythonModel):
        raise TypeError('`model` parameter')
    if not wrapperpath.exists():
        wrapperpath.makedirs()
    for m in model.methods:
        template = Template(filename=str(__makopath__/'function.mako'))
        f = open(wrapperpath/m.spelling+'.cpp', 'w')
        f.write(template.render(model=m, scope=model.scope))
        f.close()
    for m in model.overloaded_methods:
        template = Template(filename=str(__makopath__/'functions.mako'))
        f = open(wrapperpath/m[0].spelling+'.cpp', 'w')
        f.write(template.render(models=m, scope=model.scope))
        f.close()
    for e in model.enums:
        template = Template(filename=str(__makopath__/'enums.mako'))
        f = open(wrapperpath/e.spelling+'.cpp', 'w')
        f.write(template.render(model=e, scope=model.scope))
        f.close()
    for c in model.classes:
        template = Template(filename=str(__makopath__/'class.mako'))
        f = open(wrapperpath/''.join('_' + char.lower() if char.isupper() else char for char in c.spelling).lstrip('_')+'.cpp', 'w')
        f.write(template.render(model=c))
        f.close()
    for s in model.scopes:
        write_boost_python(wrapperpath/model.scope, s)

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
