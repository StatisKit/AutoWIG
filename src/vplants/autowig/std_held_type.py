from .asg import ClassProxy
from .boost_python_back_end import BoostPythonExportFileProxy

def none_held_type(node):
    if not isinstance(node, (ClassProxy, BoostPythonExportFileProxy)):
        raise TypeError('\'node\' parameter')

def ptr_held_type(node):
    if isinstance(node, ClassProxy):
        return node.globalname + '*'
    elif not isinstance(node, BoostPythonExportFileProxy):
        raise TypeError('\'node\' parameter')

def std_unique_ptr_held_type(node):
    if isinstance(node, ClassProxy):
        return 'std::unique_ptr< ' + node.globalname + ' >'
    elif isinstance(node, BoostPythonExportFileProxy):
        return '#include <memory>'
    else:
        raise TypeError('\'node\' parameter')

def std_shared_ptr_held_type(node):
    if isinstance(node, ClassProxy):
        return 'std::shared_ptr< ' + node.globalname + ' >'
    elif isinstance(node, BoostPythonExportFileProxy):
        return '#include <memory>'
    else:
        raise TypeError('\'node\' parameter')
