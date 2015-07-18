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
        self.postprocessing = PostProcessingDiagnostic()

    @property
    def total(self):
        return self.preprocessing + self.processing.total + self.postprocessing.total

    def __str__(self):
        string = "Front-end: " + str(self.total)
        string += "\n * Pre-processing: " + str(self.preprocessing)
        string += "\n * Processing: " + str(self.processing.total)
        string += "\n * Post-Processing: " + str(self.postprocessing.total)
        return string

class PostProcessingDiagnostic(object):

    def __init__(self):
        self.overloading = 0.
        self.discarding = 0.

    @property
    def total(self):
        return self.overloading + self.discarding

    def __str__(self):
        string = "Front-end post-processing: " + str(self.total)
        string += "\n * Overloading: " + str(self.overloading)
        string += "\n * Discarding: " + str(self.discarding)
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
    self._compute_overloads()
    curr = time.time()
    diagnostic.postprocessing.overloading = curr - prev
    prev = time.time()
    self._discard_forward_declarations()
    curr = time.time()
    diagnostic.postprocessing.discarding = curr - prev
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
        content += "#include \"" + str(arg.abspath()) + "\"\n"
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
        if not fct.is_overloaded:
            overloads = fct.overloads
            if len(overloads) > 1:
                for overload in overloads:
                    overload.is_overloaded = True

AbstractSemanticGraph._compute_overloads = _compute_overloads
del _compute_overloads

def _discard_forward_declarations(self):
    black = set()
    for cls in self.classes(templated=False):
        if not cls.node in black and not cls.node.startswith('union '):
            if cls.is_complete:
                complete = cls
                if cls.node.startswith('class '):
                    try:
                        duplicate = self[cls.node.replace('class ', 'struct ', 1)]
                    except:
                        duplicate = None
                elif cls.node.startswith('struct '):
                    try:
                        duplicate = self[cls.node.replace('struct ', 'class ', 1)]
                    except:
                        duplicate = None
                else:
                    duplicate = None
            else:
                duplicate = cls
                if cls.node.startswith('class '):
                    try:
                        complete = self[cls.node.replace('class ', 'struct ', 1)]
                    except:
                        complete = None
                elif cls.node.startswith('struct '):
                    try:
                        complete = self[cls.node.replace('struct ', 'class ', 1)]
                    except:
                        complete = None
                else:
                    complete = None
            if not duplicate is None:
                if isinstance(duplicate, ClassTemplateProxy) and not complete is None:
                    black.add(complete.node)
                    if complete.is_complete:
                        if isinstance(complete, ClassProxy):
                            for enm in complete.enums():
                                black.add(enm.node)
                            for nlcs in complete.classes(recursive=True):
                                black.add(ncls.node)
                                if isinstance(ncls, ClassProxy):
                                    for enm in nlcs.enums():
                                        black.add(enm.node)
                elif complete is None or not complete.is_complete or duplicate.is_complete:
                    black.add(duplicate.node)
                    if duplicate.is_complete:
                        if isinstance(duplicate, ClassProxy):
                            for enm in duplicate.enums():
                                black.add(enm.node)
                            for nlcs in duplicate.classes(recursive=True):
                                black.add(ncls.node)
                                if isinstance(ncls, ClassProxy):
                                    for enm in nlcs.enums():
                                        black.add(enm.node)
                    if not complete is None:
                        black.add(complete.node)
                        if complete.is_complete:
                            if isinstance(complete, ClassProxy):
                                for enm in complete.enums():
                                    black.add(enm.node)
                                for nlcs in complete.classes(recursive=True):
                                    black.add(ncls.node)
                                    if isinstance(ncls, ClassProxy):
                                        for enm in nlcs.enums():
                                            black.add(enm.node)
                else:
                    complete = complete.node
                    duplicate = duplicate.node
                    for node, edge in self._type_edges.iteritems():
                        if edge['target'] == duplicate:
                            edge['target'] = complete
                    for node, edges in self._base_edges.iteritems():
                        for index, edge in enumerate(edges):
                            if edge['base'] == duplicate:
                                edges[index]['base'] = complete
                    for node, edges in self._template_edges.iteritems():
                        for index, edge in enumerate(edges):
                            if edge['target'] == duplicate:
                                edges[index]['target'] = complete
                    black.add(duplicate)
        #if not cls.node in black:
        #    parent = cls.parent
        #    duplicates = [pcl for pcl in parent.classes() if pcl.localname == cls.localname]
        #    completes, duplicates = [dcl for dcl in duplicates if dcl.is_complete], [dcl for dcl in duplicates if not dcl.is_complete]
        #    if len(completes) == 0:
        #        for duplicate in duplicates:
        #            black.add(duplicate.node)
        #    elif len(completes) == 1 and len(duplicates) == 0:
        #        continue
        #    elif len(completes) == 1 and len(duplicates) > 0:
        #        complete = completes.pop().node
        #        duplicates = [dcls.node for dcls in duplicates]
        #        for node, edge in self._type_edges.iteritems():
        #            if edge['target'] in duplicates:
        #                edge['target'] = complete
        #        for node, edges in self._base_edges.iteritems():
        #            for index, edge in enumerate(edges):
        #                if edge['base'] in duplicates:
        #                    edges[index]['base'] = complete
        #        for node, edges in self._template_edges.iteritems():
        #            for index, edge in enumerate(edges):
        #                if edge['target'] in duplicates:
        #                    edges[index]['target'] = complete
        #        for duplicate in duplicates:
        #            black.add(duplicate)
        #    else:
        #        for complete in completes:
        #            black.add(complete.node)
        #            for enm in complete.enums():
        #                black.add(enm.node)
        #            for cls in complete.classes(recursive=True):
        #                black.add(cls.node)
        #                if isinstance(cls, ClassProxy):
        #                    for enm in cls.enums():
        #                        black.add(enm.node)
        #        for duplicate in duplicates:
        #            black.add(duplicate.node)
    print 'done!'
    change = True
    nb = 0
    while change:
        print nb,
        change = False
        for cls in self.classes(specialized=True, templated=False):
            # TODO templated=None
            if not cls.node in black:
                templates = [tpl.target for tpl in cls.templates]
                while not(len(templates) == 0 or any(tpl.node in black for tpl in templates)):
                    _templates = templates
                    templates = []
                    for _tpl in _templates:
                        if isinstance(_tpl, ClassTemplateSpecializationProxy):
                            templates.extend([tpl.target for tpl in _tpl.templates])
                if not len(templates) == 0:
                    change = True
                    black.add(cls.node)
                    for enm in cls.enums():
                        black.add(enm.node)
                    for ncls in cls.classes(recursive=True):
                        black.add(ncls.node)
                        if isinstance(ncls, ClassProxy):
                            for enm in ncls.enums():
                                black.add(enm.node)
        nb += 1
    print 'done!'
    gray = set(black)
    for tdf in self.typedefs():
        if tdf.type.target.node in black or tdf.parent.node in black:
            gray.add(tdf.node)
            self._type_edges.pop(tdf.node)
            self._nodes.pop(tdf.node)
    for var in self.variables():
        if var.type.target.node in black or var.parent.node in black:
            gray.add(var.node)
            self._type_edges.pop(var.node)
            self._nodes.pop(var.node)
    for fct in self.functions():
        if fct.parent.node in black or fct.result_type.target.node in black or any(prm.type.target.node in black for prm in fct.parameters):
            gray.add(fct.node)
            for prm in fct.parameters:
                self._type_edges.pop(prm.node)
                self._nodes.pop(prm.node)
            self._syntax_edges.pop(fct.node)
            self._type_edges.pop(fct.node)
            self._nodes.pop(fct.node)
    for parent, children in self._syntax_edges.items():
        self._syntax_edges[parent] = [child for child in children if not child in gray]
    gray = set()
    for cls in self.classes(templated=False):
        if not cls.node in black:
            for ctr in cls.constructors:
                if any(prm.type.target.node in black for prm in ctr.parameters):
                    gray.add(ctr.node)
                    for prm in ctr.parameters:
                        self._type_edges.pop(prm.node)
                        self._nodes.pop(prm.node)
                    self._syntax_edges.pop(ctr.node)
                    self._nodes.pop(ctr.node)
            self._base_edges[cls.node] = [dict(base = base['base'], access = base['access'], is_virtual = base['is_virtual']) for base in self._base_edges[cls.node] if not base['base'] in black]
        else:
            enum_constants = cls.enum_constants()
            dtr = cls.destructor
            constructors = cls.constructors
            for cst in enum_constants:
                gray.add(cst.node)
                self._nodes.pop(cst.node)
            if not dtr is None:
                self._nodes.pop(dtr.node)
            for ctr in constructors:
                gray.add(ctr.node)
                for prm in ctr.parameters:
                    self._type_edges.pop(prm.node)
                    self._nodes.pop(prm.node)
                self._nodes.pop(ctr.node)
                self._syntax_edges.pop(ctr.node)
    for parent, children in self._syntax_edges.items():
        self._syntax_edges[parent] = [child for child in children if not child in gray]
    for cls in self.classes(templated=True, specialized=False):
        self._specialization_edges[cls.node] = [spec for spec in self._specialization_edges[cls.node] if not spec in black]
    for cls in black:
        self._nodes.pop(cls)
        self._syntax_edges.pop(cls, None)
        self._base_edges.pop(cls, None)
        self._template_edges.pop(cls, None)
        self._specialization_edges.pop(cls, None)

AbstractSemanticGraph._discard_forward_declarations = _discard_forward_declarations
del _discard_forward_declarations
