"""
"""

import pkg_resources

def build_proxy_manager_doc(self):
    self.__doc__ = []
    if self._brief:
        self.__doc__.append(self._brief)
        self.__doc__.append('')
    if self._detailed:
        self.__doc__.append(self._detailed)
        self.__doc__.append('')
    self.__doc__.append(":Available Proxies:")
    self.__doc__.extend(" - \'" + proxy.name + '\'' for proxy in pkg_resources.iter_entry_points(self._group))
    self.__doc__.extend(" - \'" + proxy + '\'' for proxy in self._cache)
    self.__doc__ = '\n'.join(self.__doc__)

class ProxyManagerIdentificationDescriptor(object):
    """
    """

    def __get__(self, obj, cls):
        if not hasattr(obj, '_proxy'):
            raise ValueError('\'proxy\' identification not setted')
        return obj._proxy

    def __set__(self, obj, proxy):
        current = proxy
        while current in obj._cache:
            current = obj._cache[current]
        if isinstance(current, basestring):
            current = pkg_resources.iter_entry_points(obj._group, current).next().load()
        if not issubclass(current, obj._base):
            raise ValueError("Proxy class is not a subclass of " + obj._base.__name__)
        obj._proxy = proxy
        obj._current = current
        build_proxy_manager_doc(obj)

class ProxyManager(object):

    proxy = ProxyManagerIdentificationDescriptor()

    def __init__(self, group, base, brief="", detailed=""):
        """Create a proxy"""
        self._group = group
        self._base = base
        self._brief = brief
        self._detailed = detailed
        self._cache = dict()
        build_proxy_manager_doc(self)

    def __call__(self):
        if hasattr(self, '_current'):
            return self._current
        else:
            raise NotImplementedError("A proxy class must be selected using \'proxy\' field")

    def __contains__(self, proxy):
        """
        """
        return proxy in self._cache or len(list(pkg_resources.iter_entry_points(self._group, proxy))) > 0

    def __getitem__(self, proxy):
        """
        """
        proxy, self.proxy = self.proxy, proxy
        proxy, self.proxy = self.__call__(), proxy
        return proxy

    def __setitem__(self, proxy, cls):
        if not isinstance(proxy, basestring):
            raise TypeError('\'proxy\' parameter must be a basestring instance')
        if issubclass(cls, self._base):
            self._cache[proxy] = cls
        elif isinstance(cls, basestring):
            if not cls in self:
                raise ValueError('\'cls\' parameter must be an existing proxy')
            if proxy == cls:
                raise ValueError('\'proxy\' and \'cls\' parameters cannot have the same value')
            self._cache[proxy] = cls
        else:
            raise TypeError('must be a subclass of ' + self._base.__name__)
        build_proxy_manager_doc(self)
