class BoostPythonBackEndPlugin(object):
    """Boost.Python plugin for the AutoWIG back-end"""

    modulename = 'vplants.autowig.boost_python_back_end'
    objectname = 'back_end'

    implements = 'back-end'

class CharPointerBackEndPlugin(object):
    """Boost.Python plugin for the AutoWIG back-end considering functions, methods and constructors with character pointers as inputs or output"""

    modulename = 'vplants.autowig.boost_python_back_end'
    objectname = 'char_pointer'

    implements = 'back-end'
