"""
"""

class Proxy(object):
    """
    """

    def __init__(self, scope):
        """
        """
        self.scope = scope

class InterfaceProxy(Proxy):
    """
    """

    def __init__(self, scope, interface):
        """
        """
        Proxy.__init__(self, scope)
        self.interface = interface

    def __str__(self):
        """
        """
        if self.scope == "":
            return self.interface.spelling
        else:
            return self.scope+"::"+self.interface.spelling

class ConstructorInterfacesProxy(Proxy):
    """
    """

    def __init__(self, scope, interface):
        """
        """
        if not isinstance(interface, UserDefinedTypeInterfaceModel):
            raise TypeError('`interface` parameter')
        Proxy.__init__(self, scope)
        if not self.scope == "":
            self.scope+interface.spelling
        self.interfaces = interface.constructors

    def __len__(self):
        return len(self.interfaces)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [self[i] for i in xrange(*item.indices(len(self)))]
        elif not isinstance(item. int):
            raise TypeError('`item` parameter')
        if item < 0: item += len(self)
        if not item < len(self):
            raise IndexError('`item` parameter')

    def __str__(self):
        """
        """
        self.scope+" contructors"

    @property
    def inputs(self):
        return [interface.inputs for interface in self.interfaces]

    @property
    def accesses(self):
        return [interface.access for interface in self.interfaces]

class Library(object):
    """
    """

    def __init__(self, spelling, *interfaces):
        """
        """
        if not isinstance(spelling, basestring):
            raise TypeError('`spelling` parameter')
        self.spelling = spelling
        self.files = set()
        self.nonoverloaded_functions = []
        self.overloaded_functions = []
        self.namespaces = []
        self.classes = []
        self.enums = []

    def _extract_files(self, *interfaces):
        for interface in interfaces:
            self.files.add(interface.file)

    def _extract_functions(self, *interfaces):
        for interface in interfaces:
            for declaration in self.declarations:
                if isinstance(declaration, FunctionInterface):
                    self.nonoverloaded_functions.append(declaration)

    def _resolve_overloaded_functions(self):



    def __str__(self):
        return self.name+" library"

    @property
    def namespaces(self):
        result = set()
        def get_namespaces(currentscope, namespace):

        for i in self.interfaces:


