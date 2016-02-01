def python_path(node):
    if isinstance(node, DirectoryProxy):
        parent = node
    elif isinstance(node, FileProxy):
        parent = node.parent
    else:
        raise TypeError('\'node\' parameter')
    if not parent.globalname + '__init__.py' in self.asg:
            initnode = self.asg.add_file(parent.globalname + '__init__.py')
            initnode.language = 'py'
        python_path = ''
        while parent.globalname + '__init__.py' in self.asg:
            python_path = parent.localname + python_path
            parent = parent.parent
            if not parent.globalname + '__init__.py' in self.asg and path(parent.globalname + '__init__.py').exists():
                initnode = self.asg.add_file(parent.globalname + '__init__.py')
                initnode.language = 'py'
        return python_path.replace('/', '.').rstrip('.')
