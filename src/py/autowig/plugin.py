## Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ##
##                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
## Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
##                                                                       ##
## This file is part of the AutoWIG project. More information can be     ##
## found at                                                              ##
##                                                                       ##
##     http://autowig.rtfd.io                                            ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

import pkg_resources

class ProxyManager(object):

    def __call__ (self):
        proxy = self.proxy
        if proxy:
            return self[proxy]
        else:
            raise NotImplementedError("A proxy must be selected using \'proxy\' field")

    def __init__(self, group, brief="", details=""):
        """Create a proxy manager"""
        self._group = group
        self._brief = brief
        self._details = details
        self._cache = dict()

    def __iter__(self):
        def listing():
            for key in self._cache.keys():
                yield key
            for proxy in pkg_resources.iter_entry_points(self._group):
                yield proxy.name
        return sorted(listing()).__iter__()

    def __contains__(self, proxy):
        """
        """
        return proxy in self._cache or len(list(pkg_resources.iter_entry_points(self._group, proxy))) > 0

    def __getitem__(self, proxy):
        """
        """
        while proxy in self._cache:
            proxy = self._cache[proxy]
        if callable(proxy):
            return proxy
        else:
            return list(pkg_resources.iter_entry_points(self._group, proxy)).pop().load()

    def __setitem__(self, proxy, implementation):
        if not isinstance(proxy, basestring):
            raise TypeError('\'proxy\' parameter must be a basestring instance')
        if callable(implementation):
            self._cache[proxy] = implementation
        elif isinstance(implementation, basestring):
            if implementation not in self:
                raise ValueError('\'implementation\' parameter must be one of ' + ', '.join('\'' + proxy + '\'' for proxy in self))
            if proxy == implementation:
                raise ValueError('\'proxy\' and \'implementation\' parameters cannot have the same value')
            self._cache[proxy] = implementation
        else:
            raise TypeError('must be callable or a basestring instance')

    @property
    def __doc__(self):
        doc = []
        if self._brief:
            doc.append(self._brief)
            doc.append('')
        if self._details:
            doc.append(self._details)
            doc.append('')
        doc.append(":Available Implementations:")
        doc.extend(" - '" + proxy + "'" for proxy in self)
        return '\n'.join(doc)

    @property
    def proxy(self):
        return getattr(self, '_proxy', None)

    @proxy.setter
    def proxy(self, proxy):
        if proxy not in self:
            raise ValueError('\'proxy\' parameter should be one of ' + ', '.join('\'' + proxy + '\'' for proxy in self))
        else:
            self._proxy = proxy

    @proxy.deleter
    def proxy(self):
        self._proxy = None

class PluginManagerDescriptor(object):
    """A plugin plugin manager descriptor that returns and sets plugin_manager implementations
    """

    def __get__(self, obj, objtype):
        plugin = obj.plugin
        if plugin:
            return obj[plugin]
        else:
            def __call__():
                """No plugin selected"""
                raise NotImplementedError("A plugin must be selected using \'plugin\' field")
            return __call__


class PluginManager(object):

    __call__ = PluginManagerDescriptor()

    def __init__(self, group, brief="", details=""):
        """Create a plugin manager"""
        self._group = group
        self._brief = brief
        self._details = details
        self._cache = dict()

    def __iter__(self):
        def listing():
            for key in self._cache.keys():
                yield key
            for plugin in pkg_resources.iter_entry_points(self._group):
                yield plugin.name
        return sorted(listing()).__iter__()

    def __contains__(self, plugin):
        """
        """
        return plugin in self._cache or len(list(pkg_resources.iter_entry_points(self._group, plugin))) > 0

    def __getitem__(self, plugin):
        """
        """
        while plugin in self._cache:
            plugin = self._cache[plugin]
        if callable(plugin):
            return plugin
        else:
            return list(pkg_resources.iter_entry_points(self._group, plugin)).pop().load()

    def __setitem__(self, plugin, implementation):
        if not isinstance(plugin, basestring):
            raise TypeError('\'plugin\' parameter must be a basestring instance')
        if callable(implementation):
            self._cache[plugin] = implementation
        elif isinstance(implementation, basestring):
            if implementation not in self:
                raise ValueError('\'implementation\' parameter must be one of ' + ', '.join('\'' + plugin + '\'' for plugin in self))
            if plugin == implementation:
                raise ValueError('\'plugin\' and \'implementation\' parameters cannot have the same value')
            self._cache[plugin] = implementation
        else:
            raise TypeError('must be callable or a basestring instance')

    @property
    def __doc__(self):
        doc = []
        if self._brief:
            doc.append(self._brief)
            doc.append('')
        if self._details:
            doc.append(self._details)
            doc.append('')
        doc.append(":Available Implementations:")
        doc.extend(" - '" + plugin + "'" for plugin in self)
        return '\n'.join(doc)

    @property
    def plugin(self):
        return getattr(self, '_plugin', None)

    @plugin.setter
    def plugin(self, plugin):
        if plugin not in self:
            raise ValueError('\'plugin\' parameter should be one of ' + ', '.join('\'' + plugin + '\'' for plugin in self))
        else:
            self._plugin = plugin

    @plugin.deleter
    def plugin(self):
        self._plugin = None
