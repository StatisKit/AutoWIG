from .asg import ClassProxy
from .boost_python_back_end import BoostPythonExportFileProxy

def boost_shared_ptr_held_type(node):
    if isinstance(node, ClassProxy):
        return 'boost::shared_ptr< ' + node.globalname + ' >'
    elif isinstance(node, BoostPythonExportFileProxy):
        return '#include <boost/shared_ptr>'
    else:
        raise TypeError('\'node\' parameter')
