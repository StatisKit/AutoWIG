from .ast import *
from .asg import *
from .tools import subclasses
from .libclang_front_end import set_libclang_front_end
#from .pyclang_front_end import set_pyclang_front_end

__all__ = ['AbstractSyntaxTree', 'AbstractSemanticGraph', 'set_front_end']

def set_front_end(front_end, *args, **kwargs):
    if front_end == 'libclang':
        set_libclang_front_end(*args, **kwargs)
    elif front_end == 'pyclang':
        set_pyclang_front_end()
    else:
        raise ValueError('\'front_end\' parameter')

def front_end(self, *args, **kwargs):
    args = [self.add_file(arg) if isinstance(arg, basestring) else arg for arg in args]
    if any(not arg.on_disk for arg in args):
        raise ValueError('\'args\' parameters')
    if not 'flags' in kwargs:
        if not 'language' in kwargs:
            languages = {arg.language for arg in args if hasattr(arg, 'language')}
            if not len(languages.difference({'c', 'c++'})) == 0:
                raise ValueError('')
            if len(languages) in [0, 2]:
                language = 'c++'
            else:
                language = languages.pop()
        else:
            language = kwargs.pop('language')
            if not language in ['c', 'c++']:
                raise ValueError('\'language\' parameter')
        self._language = language
        if language == 'c':
            flags = ['-x', 'c++', '-std=c++11', '-Wdocumentation']
        else:
            flags = ['-x', 'c', '-std=c11', '-Wdocumentation']
    else:
        flags = kwargs.pop('flags')
        if 'c' in flags:
            self._language = 'c'
        elif 'c++' in flags:
            self._language = 'c++'
        else:
            raise ValueError('\'flags\' parameter')
    content = ""
    for arg in args:
        if self._language == 'c++':
            if arg.language == 'c':
                content += "extern \"C\" { #include \"" + arg.globalname + "\" }\n"
            else:
                content += "#include \"" + arg.globalname + "\"\n"
                if arg.language is None:
                    arg.language = self._language
        else:
            if arg.language == 'c++':
                content += "extern \"C++\" { #include \"" + arg.globalname + "\" }\n"
            else:
                content += "extern \"C\" { #include \"" + arg.globalname + "\" }\n"
                if arg.language is None:
                    arg.language = self._language
        arg.clean = False
    self._cleaned = False
    self._read_fundamentals()
    ersatz = self._front_end(content, flags=flags, **kwargs)
    self._compute_overloads()
    self._remove_duplicates()
    return ersatz

AbstractSemanticGraph.front_end = front_end
del front_end

def _read_fundamentals(self):

    if not '::' in self._nodes:
        self._nodes['::'] = dict(proxy = NamespaceProxy)
    if not '::' in self._syntax_edges:
        self._syntax_edges['::'] = []

    for fundamental in subclasses(FundamentalTypeProxy):
        if hasattr(fundamental, '_node'):
            if not fundamental._node in self._nodes:
                self._nodes[fundamental._node] = dict(proxy = fundamental)
            if not fundamental._node in self._syntax_edges['::']:
                self._syntax_edges['::'].append(fundamental._node)

AbstractSemanticGraph._read_fundamentals = _read_fundamentals
del _read_fundamentals

def _clean(self, cleanbuffer):
    nodes = [node for node in self.nodes() if node.clean]
    for node in nodes:
        if not node.id in ['::', '/']:
            self._syntax_edges[node.parent.id].remove(node.id)
    for node in nodes:
        self._nodes.pop(node.id)
        self._syntax_edges.pop(node.id, None)
        self._base_edges.pop(node.id, None)
        self._type_edges.pop(node.id, None)
    for node in self.nodes():
        del node.clean
    for node, clean in cleanbuffer:
        if node.id in self:
            node.clean = clean

AbstractSemanticGraph._clean = _clean
del _clean

def _compute_overloads(self):
    for fct in self.functions(free=None):
        if hasattr(fct, '_is_overloaded') and not fct._is_overloaded:
            del fct.is_overloaded
    for fct in self.functions(free=None):
        overloads = fct.overloads
        if len(overloads) == 1:
            fct.is_overloaded = False
        else:
            for overload in overloads:
                overload.is_overloaded = True

AbstractSemanticGraph._compute_overloads = _compute_overloads
del _compute_overloads

def _remove_duplicates(self):
    cleanbuffer =  []
    for node in self.nodes():
        if hasattr(node, '_clean'):
            cleanbuffer.append((node, node._clean))
        node.clean = False
    scopes = [self['::']]
    while len(scopes) > 0:
        scope = scopes.pop()
        if isinstance(scope, NamespaceProxy):
            scopes.extend(scope.namespaces())
        for cls in scope.classes():
            classes = cls.localname
            classes = [cls for cls in scope.classes() if cls.localname == classes]
            if len(classes) > 1:
                complete = [cls for cls in classes if cls.is_complete]
                if len(complete) == 0:
                    warnings.warn('\'' + '\', \''.join(cls.id for cls in classes) + '\'', NoDefinitionWarning)
                    ids = [cls.id for cls in classes]
                    for fct in self.functions(free=False):
                        if fct.result_type.target.id in ids or any([parameter.type.target.id in ids for parameter in fct.parameters]):
                            fct.clean = True
                            warnings.warn('\'' + fct.globalname + '\'', SideEffectWarning)
                elif len(complete) == 1:
                    complete = complete.pop()
                    classes = [cls for cls in classes if not cls.is_complete]
                    ids = [cls.id for cls in classes]
                    for node, edge in self._type_edges.iteritems():
                        if edge['target'] in ids:
                            edge['target'] = complete.id
                    for node, edges in self._base_edges.iteritems():
                        for index, edge in enumerate(edges):
                            if edge['base'] in ids:
                                edges[index]['base'] = complete.id
                    scopes.append(complete)
                else:
                    warnings.warn('\'' + '\', \''.join(cls.id for cls in classes) + '\'', MultipleDefinitionWarning)
                    ids = [cls.id for cls in classes]
                    for fct in self.functions(free=False):
                        if fct.result_type.target.id in ids or any([parameter.type.target.id in ids for parameter in fct.parameters]):
                            fct.clean = True
                            warnings.warn('\'' + fct.globalname + '\'', SideEffectWarning)
                for cls in classes:
                    cls.clean = True
            elif len(classes) == 1:
                scopes.append(classes.pop())
    temp = [node for node in self.nodes() if node.clean]
    colored = set()
    while len(temp) > 0:
        node = temp.pop()
        node.clean = True
        if not node.id in colored:
            if isinstance(node, DirectoryProxy):
                temp.extend(node.glob())
            elif isinstance(node, FunctionProxy):
                temp.extend(node.parameters)
            elif isinstance(node, ConstructorProxy):
                temp.extend(node.parameters)
            elif isinstance(node, ClassProxy):
                temp.extend(node.declarations())
            elif isinstance(node, NamespaceProxy):
                temp.extend(node.declarations())
            colored.add(node.id)
    self._clean(cleanbuffer)

AbstractSemanticGraph._remove_duplicates = _remove_duplicates
del _remove_duplicates
