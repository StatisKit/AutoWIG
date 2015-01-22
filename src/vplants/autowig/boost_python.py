"""
"""
from openalea.core.path import path
from vplants.autowig.interface_model import interface_model, VariableModel, FunctionModel, ClassModel

def boost_python(filepath, dirpath, **kwargs):
    """
    """
    if not isinstance(dirpath, basestring):
        raise TypeError('`dirpath` parameter')
    dirpath = path(dirpath)
    if not dirpath.exists:
        dirpath.mkdir()
    return visit_declarations(interface_model(filepath, **kwargs).declarations, dirpath, "::")

def visit_declarations(declarations, namespace):
    files =
    if not dirpath.exists:
        dirpath.mkdir()
    for declaration in declarations:
        if isinstance(declaration, FunctionModel):
            pass
        elif isinstance(declaration, ClassModel):
            pass
        elif isinstance(declaration, EnumModel):
            pass
        elif isinstance(declaration, NamespaceModel):
            visit_declarations(declaration.declarations, namespace/declaration.name)

def expose_function(declaration, dirpath):
    filepath = dirpath/declaration.name
    filehandler = open(filepath, 'w')
    filehandler.file.write('#include <boost/python.hpp>\n')
    filehandler.file.write('#include <>\n\n')
    filehandler.file.write('boost::python::BOOST_PYTHON_MODULE(_'+declaration.name+')\n{\n')
    filehandler.file.write('\tboost::python::def(\"'+declaration.name+'\", '+declaration.name+');\n')
    filehandler.file.write('}\n\nvoid init_bindings()\n{\n\tPy_initialize();\n\tinit_'+declaration.name+'();\n}')
    filehandler.close()
