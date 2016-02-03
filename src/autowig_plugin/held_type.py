class StdHeldTypePlugin(object):
    """
    """

    modulename = 'autowig.std_held_type'

class NoneHeldTypePlugin(StdHeldTypePlugin):
    """
    """

    name = 'none'
    objectname = 'non_held_type'

class PtrHeldTypePlugin(StdHeldTypePlugin):
    """
    """

    name = 'ptr'
    objectname = 'ptr_held_type'

class StdUniquePtrHeldTypePlugin(StdHeldTypePlugin):
    """
    """

    name = 'std:unique_ptr'
    objectname = 'std_unique_ptr_held_type'

class StdSharedPtrHeldTypePlugin(StdHeldTypePlugin):
    """
    """

    name = 'std:shared_ptr'
    objectname = 'std_shared_ptr_held_type'

class BoostHeldTypePlugin(object):
    """
    """

    modulename = 'vplants.autowig.boost_held_type'

class BoostSharedPtrHeldTypePlugin(BoostHeldTypePlugin):
    """
    """

    name = 'boost:shared_ptr'
    objectname = 'boost_shared_ptr_held_type'
