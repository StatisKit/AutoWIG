class FrontEndPlugin(object):
    """Plugin for the AutoWIG front-end based on the Libclang module"""

    modulename = 'vplants.autowig.libclang_front_end'
    objectname = 'front_end'

    implements = 'front-end'

    technology = 'libclang'
