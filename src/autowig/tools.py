import pkg_resources

__all__ = ['Plugin', 'camel_case_to_lower', 'to_camel_case', 'camel_case_to_upper']

def build_plugin_doc(self):
    self.__doc__ = []
    if self._brief:
        self.__doc__.append(self._brief)
        self.__doc__.append('')
    if self._detailed:
        self.__doc__.append(self._detailed)
        self.__doc__.append('')
    self.__doc__.append(":Available Plugins:")
    self.__doc__.extend(" - \'" + plugin.name + '\'' for plugin in pkg_resources.iter_entry_points(self._group))
    self.__doc__.extend(" - \'" + plugin + '\'' for plugin in self._cache)
    self.__doc__ = '\n'.join(self.__doc__)

class PluginImplementationDescriptor(object):
    """A plugin descriptor that returns and sets plugin implementations
    """

    def __get__(self, obj, objtype):
        if hasattr(obj, '_plugin'):
            plugin = obj._plugin
            while plugin in obj._cache:
                plugin = obj._cache[plugin]
            if callable(plugin):
                return plugin
            else:
                return pkg_resources.iter_entry_points(obj._group, plugin).next().load()
        else:
            def __call__(*args, **kwargs):
                """No plugin implementation selected"""
                raise NotImplementedError("A plugin implementation must be selected using \'plugin\' field")
            return __call__

class PluginIdentificationDescriptor(object):
    """
    """

    def __get__(self, obj, cls):
        if not hasattr(obj, '_plugin'):
            raise ValueError('\'plugin\' identification not setted')
        return obj._plugin

    def __set__(self, obj, plugin):
        obj._plugin = plugin
        build_plugin_doc(obj)


class Plugin(object):

    __call__ = PluginImplementationDescriptor()

    plugin = PluginIdentificationDescriptor()

    def __init__(self, group, brief="", detailed=""):
        """Create a plugin"""
        self._group = group
        self._brief = brief
        self._detailed = detailed
        self._cache = dict()
        build_plugin_doc(self)

    def __contains__(self, plugin):
        """
        """
        return plugin in self._cache or len(list(pkg_resources.iter_entry_points(self._group, plugin))) > 0

    def __getitem__(self, plugin):
        """
        """
        plugin, self.plugin = self.plugin, plugin
        plugin, self.plugin = self.__call__, plugin
        return plugin

    def __setitem__(self, plugin, implementation):
        if not isinstance(plugin, basestring):
            raise TypeError('\'plugin\' parameter must be a basestring instance')
        if callable(implementation):
            self._cache[plugin] = implementation
        elif isinstance(implementation, basestring):
            if not implementation in self:
                raise ValueError('\'implementation\' parameter must be an existing plugin')
            if plugin == implementation:
                raise ValueError('\'plugin\' and \'implementation\' parameters cannot have the same value')
            self._cache[plugin] = implementation
        else:
            raise TypeError('must be callable or a basestring instance')
        build_plugin_doc(self)

def subclasses(cls, recursive=True):
    if recursive:
        subclasses = []
        front = [cls]
        while len(front) > 0:
            cls = front.pop()
            front.extend(cls.__subclasses__())
            subclasses.append(cls)
        return {subclass.__name__ : subclass for subclass in subclasses}.values()
    else:
        return cls.__subclasses__()

def camel_case_to_lower(name):
    """
    :Examples:
    >>> camel_case_to_lower('squareRoot')
    'square_root'
    >>> camel_case_to_lower('SquareRoot')
    'square_root'
    >>> camel_case_to_lower('ComputeSQRT')
    'compute_sqrt'
    >>> camel_case_to_lower('SQRTCompute')
    'sqrt_compute'
    """
    lowername = '_'
    index = 0
    while index < len(name):
        if name[index].islower():
            lowername += name[index]
            index += 1
        else:
            if not name[index] == '_':
                if not lowername[-1] == '_':
                    lowername += '_'
                lowername += name[index].lower()
                index += 1
                if index < len(name) and not name[index].islower():
                    while index < len(name) and not name[index].islower():
                        lowername += name[index].lower()
                        index += 1
                    if index < len(name):
                        lowername = lowername[:-1] + '_' + lowername[-1]
            else:
                if not lowername[-1] == '_':
                    lowername += '_'
                index += 1
    lowername = lowername.lstrip('_')
    return lowername

def camel_case_to_upper(name):
    """
    :Examples:
    >>> camel_case_to_upper('squareRoot')
    'SQUARE_ROOT'
    >>> camel_case_to_upper('SquareRoot')
    'SQUARE_ROOT'
    >>> camel_case_to_upper('ComputeSQRT')
    'COMPUTE_SQRT'
    >>> camel_case_to_upper('SQRTCompute')
    'SQRT_COMPUTE'
    >>> camel_case_to_upper('Char_U')
    """
    lowername = '_'
    index = 0
    while index < len(name):
        if name[index].islower():
            lowername += name[index].upper()
            index += 1
        else:
            if not name[index] == '_':
                if not lowername[-1] == '_':
                    lowername += '_'
                lowername += name[index].upper()
                index += 1
                if index < len(name) and not name[index].islower():
                    while index < len(name) and not name[index].islower():
                        lowername += name[index]
                        index += 1
                    if index < len(name):
                        lowername = lowername[:-1] + '_' + lowername[-1]
            else:
                if not lowername[-1] == '_':
                    lowername += '_'
                index += 1
    lowername = lowername.lstrip('_')
    return lowername

def to_camel_case(name):
    """
    :Examples:
    >>> lower_to_camel_case(camel_case_to_lower('squareRoot'))
    'SquareRoot'
    >>> lower_to_camel_case(camel_case_to_lower('SquareRoot'))
    'SquareRoot'
    >>> lower_to_camel_case(camel_case_to_lower('ComputeSQRT'))
    'ComputeSqrt'
    >>> lower_to_camel_case(camel_case_to_lower('SQRTCompute'))
    'SqrtCompute'
    """
    camelname = ''
    index = 0
    while index < len(name):
        if name[index] == '_':
            index += 1
            while index < len(name) and name[index] == '_':
                index += 1
            if index < len(name):
                camelname += name[index].upper()
        else:
            camelname += name[index]
        index += 1
    if camelname[0].islower():
       camelname  = camelname[0].upper() + camelname[1:]
    return camelname
