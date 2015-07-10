import time

from .ast import *
from .asg import *
from .tools import FactoryDocstring, subclasses
from .libclang_front_end import *
from .pyclang_front_end import *

__all__ = ['AbstractSyntaxTree', 'AbstractSemanticGraph']

class FrontEndDiagnostic(object):

    def __init__(self):
        self.preprocessing = 0.
        self.processing = None
        self.checking = 0.
        self.postprocessing = PostProcessingDiagnostic()

    @property
    def total(self):
        return self.preprocessing + self.processing.total + self.checking + sum(self.postprocessing)

    def __str__(self):
        string = "Front-end: " + str(self.total)
        string += "\n * Pre-processing: " + str(self.preprocessing)
        string += "\n * Processing: " + str(self.processing.total)
        string += "\n * Checking: " + str(self.checking) +"\n"
        string += "\n * Post-Processing: " + str(self.postprocessing.total)
        return string

class PostProcessingDiagnostic(object):

    def __init__(self):
        self.overloading = 0.
        self.purging = 0.

    @property
    def total(self):
        return self.overloading + self.purging

    def __str__(self):
        string = "Front-end post-processing: " + str(self.total)
        string += "\n * Overloading: " + str(self.overloading)
        string += "\n * Purging: " + str(self.purging)
        return string

def front_end(self, identifier, *args, **kwargs):
    diagnostic = FrontEndDiagnostic()
    prev = time.time()
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
        self._nodes[arg.node]['_parsed'] = True
    self._read_fundamentals()
    curr = time.time()
    diagnostic.preprocessing = curr - prev
    front_end = getattr(self, '_' + identifier + '_front_end')
    diagnostic.processing = front_end(content, flags=flags, **kwargs)
    prev = time.time()
    if kwargs.pop('check', True):
        pass
        #for node in self.nodes():
        #   if not node.node == ['/', '::'] and not node.node in self._syntax_edges[node.parent.node]:
        #       warnings.warn()

    curr = time.time()
    diagnostic.checking = curr - prev
    prev = time.time()
    self._compute_overloads()
    curr = time.time()
    diagnostic.postprocessing.overloading = curr - prev
    prev = time.time()
    self._remove_duplicates()
    curr = time.time()
    diagnostic.postprocessing.purging = curr - prev
    return diagnostic

AbstractSemanticGraph.front_end = front_end
del front_end
FactoryDocstring.as_factory(AbstractSemanticGraph.front_end)

def front_end(self, identifier, *args, **kwargs):
    args = [path(arg) for arg in args]
    if any(not arg.exists() for arg in args):
        raise ValueError('\'args\' parameters')
    if not 'flags' in kwargs:
        language = kwargs.pop('language')
        if not language in ['c', 'c++']:
            raise ValueError('\'language\' parameter')
        if language == 'c':
            flags = ['-x', 'c++', '-std=c++11', '-Wdocumentation']
        else:
            flags = ['-x', 'c', '-std=c11', '-Wdocumentation']
    else:
        flags = kwargs.pop('flags')
    content = ""
    for arg in args:
        content += "#include \"" + arg.abspath() + "\"\n"
    front_end = getattr(self, '_' + identifier + '_front_end')
    front_end(content, flags=flags, **kwargs)

AbstractSyntaxTree.front_end = front_end
del front_end
FactoryDocstring.as_factory(AbstractSyntaxTree.front_end)

def _read_fundamentals(self):

    if not '::' in self._nodes:
        self._nodes['::'] = dict(proxy = NamespaceProxy)
    if not '::' in self._syntax_edges:
        self._syntax_edges['::'] = []

    for fundamental in subclasses(FundamentalTypeProxy):
        if isinstance(fundamental.node, basestring):
            if not fundamental.node in self:
                self._nodes[fundamental.node] = dict(proxy = fundamental)
            if not fundamental.node in self._syntax_edges['::']:
                self._syntax_edges['::'].append(fundamental.node)

AbstractSemanticGraph._read_fundamentals = _read_fundamentals
del _read_fundamentals

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
    for cls in self.classes():
        parent = cls.parent
        duplicates = [pcl for pcl in parent.classes() if pcl.localname == cls.localname]
        completes, duplicates = [dcl for dcl in duplicates if dcl.is_complete], [dcl for dcl in duplicates if not dcl.is_complete]
        if len(completes) == 0:
            for duplicate in duplicates:
                duplicate._remove()
        elif len(completes) == 1 and len(duplicates) == 0:
            continue
        elif len(completes) == 1 and len(duplicates) > 0:
            complete = completes.pop().node
            duplicates = [dcls.node for dcls in duplicates]
            for node, edge in self._type_edges.iteritems():
                if edge['target'] in duplicates:
                    edge['target'] = complete
            for node, edges in self._base_edges.iteritems():
                for index, edge in enumerate(edges):
                    if edge['base'] in duplicates:
                        edges[index]['base'] = complete
            for node, edge in self._template_edges.iteritems():
                if edge['target'] in duplicates:
                    edge['target'] = complete
            for duplicate in duplicates:
                self._syntax_edges[parent.node].remove(duplicate)
                self._nodes.pop(duplicate)
                self._base_edges.pop(duplicate)
                self._syntax_edges.pop(duplicate)
        else:
            for complete in completes:
                duplicate._remove()
            for duplicate in duplicates:
                duplicate._remove()

AbstractSemanticGraph._remove_duplicates = _remove_duplicates
del _remove_duplicates
