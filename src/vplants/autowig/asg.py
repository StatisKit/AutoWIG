from pygments import highlight
from pygments.lexers import CppLexer, PythonLexer
from pygments.formatters import HtmlFormatter
from clang.cindex import Cursor, CursorKind, Type, TypeKind
import uuid
from mako.template import Template
from path import path
from matplotlib import pyplot
import networkx
from IPython.core import pylabtools
from IPython.html.widgets import interact
import itertools
import os
from abc import ABCMeta

from .ast import AbstractSyntaxTree

class Proxy(object):
    """
    """

    def __init__(self, asg, node):
        self._asg = asg
        self._node = node

    def __dir__(self):
        return self._asg._nodes[self._node].keys()

    def __getattr__(self, attr):
        try:
            try:
                return self.__dict__[attr]
            except:
                return self._asg._nodes[self._node][attr]
        except:
            raise
            raise AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')

class FileProxy(Proxy):
    """
    """

    def __str__(self):
        filepath = path(self.abspath)
        if not filepath.exists():
            if hasattr(self, '_template'):
                return self.template.render(obj=self)
            else: return ""
        else:
            return "".join(filepath.lines())

    @property
    def abspath(self):
        return self._node

    @property
    def relpath(self):
        if not hasattr(self, 'rootdir'):
            return self.abspath[self.abspath.rfind(os.sep)+1:]
        else:
            return self.abspath.replace(self.rootdir, '')

class CxxFileProxy(FileProxy):
    """
    """

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

class CxxProxy(Proxy):
    """
    """

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

    @property
    def globalname(self):
        if '-' in self._node:
            globalname = []
            for name in self._node.split('::'):
                if not '-' in name:
                    globalname.append(name)
            return '::'+'::'.join(globalname)
        else:
            return self._node

    @property
    def localname(self):
        if hasattr(self, 'scope'):
            localname = self.globalname.replace(self.scope, '')
        else:
            localname = self.globalname[self.globalname.rfind(':')+1:]
        if localname == '':
            if hasattr(self, '_noname'):
                return self._noname
            return ''
        else:
            return localname

    def __str__(self):
        return self.globalname

class CxxTypeProxy(CxxProxy):
    """
    """

class CxxLValueReferenceProxy(CxxProxy):
    """
    """

    @property
    def type(self):
        return self._asg[self._asg._typeedges[self._node]]

class CxxPointerProxy(CxxProxy):
    """
    """

    @property
    def pointee(self):
        return self._asg[self._asg._typeedges[self._node]]

class CxxEnumConstantProxy(CxxProxy):
    """
    """


class CxxParameterProxy(CxxProxy):
    """
    """

    @property
    def type(self):
        return self._asg[self._asg._typeedges[self._node]]

    def __str__(self):
        return str(self.type) + " " + self.localname

class CxxDeclarationProxy(CxxProxy):
    """
    """

    def __str__(self):
        return self._template.render(obj=self)

class CxxEnumProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""enum\
% if not obj.anonymous:
 ${obj.localname}\
% endif

{
% for value in obj.values[:-1]:
    ${value.localname},
% endfor
    ${obj.values[-1].localname}
};""")

    _noname = 'enum'

    @property
    def values(self):
        return [self._asg[node] for node in self._asg._declarationedges[self._node]]

    @property
    def anonymous(self):
        return '-' in self._node

class CxxTypedefProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
typedef ${obj.localname} ${str(obj.type)};
""")

    @property
    def type(self):
        return self._asg[self._asg._typeedges[self._node]]

class CxxVariableProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
% if obj.static:
static \
% endif
${str(obj.type)} ${obj.localname};
""")

    @property
    def type(self):
        return self._asg[self._asg._typeedges[self._node]]

class CxxFieldProxy(CxxVariableProxy):
    """
    """

    _template =  Template(text=r"""\
% if obj.mutable:
mutable \
% elif obj.static:
static \
% endif
${str(obj.type)} ${obj.localname};
""")

class CxxFunctionProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
${str(obj.result_type)} ${obj.localname}(${", ".join(str(parameter) for parameter in obj.parameters)});
""")

    @property
    def result_type(self):
        return self._asg[self._asg._typeedges[self._node]]

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._declarationedges[self._node]]

    @property
    def overloaded(self):
        return '-' in self._node

    @property
    def signature(self):
        return str(self.result_type) + " " + self.localname + "(" + ", ".join(str(parameter.type) for parameter in self.parameters)+ ")"

class CxxMethodProxy(CxxFunctionProxy):
    """
    """

    _template = Template(text=r"""\
% if obj.static:
static \
% elif obj.virtual:
virtual \
%endif
${str(obj.result_type)} ${obj.localname}(${", ".join(str(parameter) for parameter in obj.parameters)})\
% if obj.const:
 const\
% endif
% if obj.pure_virtual:
 = 0\
% endif
;
""")

class CxxConstructorProxy(CxxProxy):
    """
    """

    _template = Template(text=r"""\
${obj.localname}(${", ".join(str(parameter) for parameter in obj.parameters)});
""")

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._declarationedges[self._node]]

    @property
    def overloaded(self):
        return '-' in self._node

class CxxDestructorProxy(CxxProxy):
    """
    """

class CxxClassProxy(CxxDeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/class>_`
    """

    def bases(self, inherited=False):
        bases = []
        for base in self._asg._baseedges[self._node]:
            bases.append(self._asg[base['base']])
            bases[-1].access = base['access']
        if not inherited:
            return bases
        else:
            inheritedbases = []
            for base in bases:
                basebases = base.bases(True)
                if base.access == 'protected':
                    for basebase in basebases:
                        if basebase.access == 'public':
                            basebase.access = 'protected'
                elif base.access == 'private':
                    for basebase in basebases:
                        basebase.access = 'private'
                inheritedbases += basebases
            return bases+inheritedbases

    def declarations(self, inherited=False, local=True):
        if not local:
            if hasattr(self, scope):
                scope = self.scope
            else:
                scope = self.globalname.replace(self.localname, '')
        declarations = [self._asg[node] for node in self._asg._declarationedges[self._node]]
        if not local:
            for declaration in declarations:
                declaration.scope = scope
        if not inherited:
            return declarations
        else:
            for base in self.bases(True):
                basedeclarations = [basedeclaration for basedeclaration in base.declarations(False, True) if not basedeclaration.access == 'private']
                if base.access == 'protected':
                    for basedeclaration in basedeclarations:
                        if basedeclaration.access == 'public':
                            basedeclaration.access = 'protected'
                elif base.access == 'private':
                   for basedeclaration in basedeclarations:
                        basedeclaration.access = 'private'
                if not local:
                    for basedeclaration in basedeclations:
                        basedeclaration.scope = scope
                declarations += basedeclarations
            return declarations

    def enums(self, inherited=False, local=True):
        return [enum for enum in self.declarations(inherited, local) if isinstance(enum, CxxEnumProxy)]

    def fields(self, inherited=False, local=True):
        return [field for field in self.declarations(inherited, local) if isinstance(field, CxxFieldProxy)]

    def methods(self, inherited=False, local=True):
        return [method for method in self.declarations(inherited, local) if isinstance(method, CxxMethodProxy)]

    def classes(self, inherited=False, local=True):
        return [klass for klass in self.declarations(inherited, local) if isinstance(klass, CxxClassProxy)]

    def constructors(self, local=True):
        return [contructor for contructor in self.declarations(False, local) if isinstance(contructor, CxxConstructorProxy)]

    def destructor(self, local=True):
        try:
            return [detructor for detructor in self.declarations(False, local) if isinstance(detructor, CxxDestructorProxy)].pop()
        except:
            return None

    @property
    def pure_virtual(self):
        blackmethods = set()
        whitemethofs = set()
        for method in self.methods(True):
            if method.virtual:
                if method.pure_virtual:
                    blackmethods.add(method.signature)
                else:
                    whitemethods.add(method.signature)
        return len(blackmethods-whitemethods) == 0

class CxxNamespaceProxy(CxxDeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/namespace>_`
    """

    @property
    def _noname(self):
        if self._node == '::':
            return self._node
        else:
            return 'namespace'

    @property
    def anonymous(self):
        return '-' in self._node

    def declarations(self, nested=False, local=True):
        if not local:
            if hasattr(self, scope):
                scope = self.scope
            else:
                scope = self.globalname.replace(self.localname, '')
        declarations = [self._asg[node] for node in self._asg._declarationedges[self._node]]
        if not local:
            for declaration in declarations:
                declaration.scope = scope
        if not nested:
            return declarations
        else:
            declarations = [declaration for declaration in declarations if not isinstance(declaration, CxxNamespaceProxy)]
            for nestednamespace in self.namespaces(False):
                for nesteddeclaration in nestednamespace.declarations(True, local):
                    declarations.append(nesteddeclaration)
            return declarations

    def enums(self, nested=False, local=True):
        return [enum for enum in self.declarations(nested, local) if isinstance(enum, CxxEnumProxy)]

    def variables(self, nested=False, local=True):
        return [variable for variable in self.declarations(nested, local) if isinstance(variable, CxxVariableProxy)]

    def functions(self, nested=False, local=True):
        return [function for function in self.declarations(nested, local) if isinstance(function, CxxFunctionProxy)]

    def classes(self, nested=False, local=True):
        return [klass for klass in self.declarations(nested, local) if isinstance(klass, CxxClassProxy)]

    def namespaces(self, nested=False, local=True):
        if not nested:
            return [namespace for namespace in self.declarations(nested, local) if isinstance(namespace, CxxNamespacePRoxy)]
        else:
            nestednamespaces = []
            namespaces = self.namespaces(False)
            while len(namespaces):
                namespace = namespaces.pop()
                nestednamespaces.append(namespace)
                namespaces.extend(namespace.namespaces(False))
            return nestednamespaces

class AbstractSemanticGraph(object):

    def __init__(self, ast, **kwargs):
        if not isinstance(ast, AbstractSyntaxTree):
            raise TypeError('`ast` parameter')
        self._nodes = dict()
        self._declarationedges = dict()
        self._headeredges = dict()
        self._baseedges = dict()
        self._typeedges = dict()
        self._frozen = False
        self._read_ast(ast.translation_unit.cursor, **kwargs)
        self._frozen = True

    def _read_ast(self, node, scope='',
            file_proxy=CxxFileProxy,
            enum_proxy=CxxEnumProxy,
            enum_constant_proxy=CxxEnumConstantProxy,
            variable_proxy=CxxVariableProxy,
            field_proxy=CxxFieldProxy,
            parameter_proxy=CxxParameterProxy,
            function_proxy=CxxFunctionProxy,
            method_proxy=CxxMethodProxy,
            lvaluereference_proxy=CxxLValueReferenceProxy,
            pointer_proxy=CxxPointerProxy,
            type_proxy=CxxTypeProxy,
            constructor_proxy=CxxConstructorProxy,
            destructor_proxy=CxxDestructorProxy,
            class_proxy=CxxClassProxy,
            struct_proxy=CxxClassProxy,
            namespace_proxy=CxxNamespaceProxy):
        if self._frozen:
            raise Exception('`AbstractSemanticGraph` instance is frozen')
        if isinstance(node, Cursor):
            if node.kind is CursorKind.TRANSLATION_UNIT:
                self._nodes['::'] = dict(proxy = namespace_proxy)
                self._declarationedges['::'] = []
                for child in node.get_children():
                    childscope = self._read_ast(child, scope=scope)
                    if not childscope is None and not childscope in self._declarationedges['::']:
                        self._declarationedges['::'].append(childscope)
            else:
                scope += '::'+node.spelling
                if node.kind is CursorKind.TYPEDEF_DECL:
                    return
                    #properties = dict(type = 'typedef')
                    #self._declarations.append(TypedefCursor(node))
                    #elif node.kind is CursorKind.TYPE_REF:
                    #self._nodes[scope] = dict(proxy = parameter_proxy)
                    #    self._read_ast(node.type, scope)
                    #    return scope
                elif node.kind is CursorKind.TYPE_ALIAS_DECL:
                    return
                    #self._declarations.append(TypeAliasCursor(node))
                elif node.kind is CursorKind.ENUM_DECL:
                    if node.spelling == '':
                        scope += str(uuid.uuid4())
                    self._declarationedges[scope] = []
                    for child in node.get_children():
                        self._declarationedges[scope].append(self._read_ast(child, scope))
                    self._nodes[scope] = dict(proxy = enum_proxy)
                    self._add_header(scope, node.location, file_proxy=file_proxy)
                    return scope
                elif node.kind is CursorKind.ENUM_CONSTANT_DECL:
                    self._nodes[scope] = dict(proxy = enum_constant_proxy)
                    return scope
                elif node.kind in [CursorKind.VAR_DECL, CursorKind.FIELD_DECL]:
                    self._read_ast(node.type, scope)
                    if node.kind is CursorKind.VAR_DECL:
                        self._nodes[scope] = dict(proxy = variable_proxy,
                                static=False) # TODO
                        self._add_header(scope, node.location, file_proxy=file_proxy)
                    else:
                        self._nodes[scope] = dict(proxy = field_proxy,
                                mutable=False, # TODO
                                static=False) # TODO
                    return scope
                elif node.kind is CursorKind.PARM_DECL:
                    self._nodes[scope] = dict(proxy = parameter_proxy)
                    self._read_ast(node.type, scope)
                    return scope
                elif node.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD, CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
                    if scope in self._nodes:
                        newscope = scope+'::'+str(uuid.uuid4())
                        self._nodes[newscope] = self._nodes.pop(scope)
                        for source, targets in self._declarationedges.items():
                            self._declarationedges[source] = [target if not target == scope else newscope for target in targets]
                        if node.kind is CursorKind.FUNCTION_DECL:
                            self._headeredges[newscope] = self._headeredges.pop(scope)
                        self._declarationedges[newscope] = []
                        for child in self._declarationedges.pop(scope):
                            childscope = child.replace(scope, newscope)
                            self._nodes[childscope] = self._nodes.pop(child)
                            self._typeedges[childscope] = self._typeedges.pop(child)
                            self._declarationedges[newscope].append(childscope)
                        if scope in self._typeedges:
                            self._typeedges[newscope] = self._typeedges.pop(scope)
                        newscope = scope+'::'+str(uuid.uuid4())
                        if node.kind is CursorKind.FUNCTION_DECL:
                            self._nodes[newscope] = dict(proxy = function_proxy)
                            self._add_header(newscope, node.location, file_proxy=file_proxy)
                        elif node.kind is CursorKind.CXX_METHOD:
                            self._nodes[newscope] = dict(proxy = method_proxy,
                                    static = node.is_static_method(),
                                    virtual = node.is_virtual_method(),
                                    const = node.type.is_const_qualified(),
                                    pure_virtual = node.is_pure_virtual_method())
                        elif node.kind is CursorKind.CONSTRUCTOR:
                            self._nodes[newscope] = dict(proxy = constructor_proxy)
                        else:
                            self._nodes[newscope] = dict(proxy = destructor_proxy)
                        self._declarationedges[newscope] = []
                        for child in node.get_children():
                            if child.kind is CursorKind.PARM_DECL:
                                self._declarationedges[newscope].append(self._read_ast(child, newscope))
                        if not node.kind in [CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:
                            self._read_ast(node.result_type, newscope)
                        return newscope
                    else:
                        if node.kind is CursorKind.FUNCTION_DECL:
                            self._nodes[scope] = dict(proxy = function_proxy)
                            self._add_header(scope, node.location, file_proxy=file_proxy)
                        elif node.kind is CursorKind.CXX_METHOD:
                            self._nodes[scope] = dict(proxy = method_proxy,
                                    static = node.is_static_method(),
                                    virtual = node.is_virtual_method(),
                                    const = node.type.is_const_qualified(),
                                    pure_virtual = node.is_pure_virtual_method())
                        elif node.kind is CursorKind.CONSTRUCTOR:
                            self._nodes[scope] = dict(proxy = constructor_proxy)
                        else:
                            self._nodes[scope] = dict(proxy = destructor_proxy)
                        self._declarationedges[scope] = []
                        for child in node.get_children():
                            if child.kind is CursorKind.PARM_DECL:
                                self._declarationedges[scope].append(self._read_ast(child, scope))
                        if not node.kind in [CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:
                            self._read_ast(node.result_type, scope)
                        return scope
                elif node.kind in [CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL]:
                    if not scope in self._nodes:
                        self._declarationedges[scope] = []
                        self._baseedges[scope] = []
                        if node.kind is CursorKind.STRUCT_DECL:
                            self._nodes[scope] = dict(proxy = struct_proxy)
                        else:
                            self._nodes[scope] = dict(proxy = class_proxy)
                    for child in node.get_children():
                        if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                            self._baseedges[scope].append(dict(
                                base = [c for c in child.get_children() if c.kind in [CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF]].pop().type.spelling,
                                access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()))
                        elif not child.kind is CursorKind.CXX_ACCESS_SPEC_DECL:
                            childscope = self._read_ast(child, scope)
                            if not childscope is None:
                                self._declarationedges[scope].append(childscope)
                                self._nodes[childscope]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                    if len(self._declarationedges[scope])+len(self._baseedges[scope]) > 0 and not scope in self._headeredges:
                        self._add_header(scope, node.location, file_proxy=file_proxy)
                    return scope
                elif node.kind is CursorKind.NAMESPACE:
                    if not scope in self._nodes:
                        self._nodes[scope] = dict(proxy = namespace_proxy)
                        self._declarationedges[scope] = []
                    for child in node.get_children():
                        childscope = self._read_ast(child, scope)
                        if not childscope is None:
                            self._declarationedges[scope].append(childscope)
                    return scope
        elif isinstance(node, Type):
            if not node.spelling in self._nodes:
                if node.kind is TypeKind.LVALUEREFERENCE:
                    self._read_ast(node.get_pointee(), scope=node.spelling)
                    self._nodes[node.spelling] = dict(proxy = lvaluereference_proxy, const=node.is_const_qualified())
                elif node.kind is TypeKind.POINTER:
                    self._read_ast(node.get_pointee(), scope=node.spelling)
                    self._nodes[node.spelling] = dict(proxy = pointer_proxy, const=node.is_const_qualified())
                elif node.kind is TypeKind.TYPEDEF:
                    pass
                else:
                    self._nodes[node.spelling] = dict(proxy = type_proxy, const=node.is_const_qualified())
            self._typeedges[scope] = node.spelling

    def _add_header(self, scope, location, file_proxy):
        if self._frozen:
            raise Exception('`AbstractSemanticGraph` instance is frozen')
        if not location is None:
            filename = str(location.file)
            if not filename in self._nodes:
                self._nodes[filename] = dict(proxy = file_proxy)
            self._headeredges[scope] = filename

    @property
    def nodes(self):
        return self._nodes.keys()

    def __getitem__(self, node):
        if not node in self._nodes:
            raise KeyError('`node` parameter: ' + str(node))
        else:
            return self._nodes[node]["proxy"](self, node)

    def _ipython_display_(self):
        global __asg__
        __asg__ = self
        nodes = ['file', 'class', 'method', 'field', 'type', 'enum', 'enum_cst', 'variable', 'parameter', 'function', 'dispatch', 'lvaluereference', 'pointer', 'type']
        nodes = [",".join(combination) for r in range(1, len(nodes)+1) for combination in itertools.combinations(nodes, r)]
        #nodes.remove(['file,enum,enum_cst,variable,parameter,function'])
        nodes = ['class,constructor,destructor,method,field,enum,enum_cst,variable,parameter,function,namespace']+nodes
        interact(plot,
                layout=('graphviz', 'circular', 'random', 'spring', 'spectral'),
                size=(0., 60., .5),
                aspect=(0., 1., .01),
                nodes=nodes)

def plot(layout='graphviz', size=16, aspect=.5, invert=False, nodes='class,constructor,destructor,method,field,enum,enum_cst,variable,parameter,function,namespace', **kwargs):
    global __asg__
    graph = networkx.DiGraph()
    for node in __asg__._nodes:
        graph.add_node(node)
    for source, targets in __asg__._declarationedges.iteritems():
        for target in targets: graph.add_edge(source, target)
    for source, target in __asg__._headeredges.iteritems():
        graph.add_edge(source, target)
    for source, target in __asg__._typeedges.iteritems():
        graph.add_edge(source, target)
    for source, targets in __asg__._baseedges.iteritems():
        for target in targets: graph.add_edge(source, target['base'])

    class NodeFilter(object):

        __metaclass__ = ABCMeta

    for node in nodes.split(','):
        if node == 'file':
            NodeFilter.register(FileProxy)
        elif node == 'class':
            NodeFilter.register(CxxClassProxy)
        elif node == 'constructor':
            NodeFilter.register(CxxConstructorProxy)
        elif node == 'destructor':
            NodeFilter.register(CxxDestructorProxy)
        elif node == 'method':
            NodeFilter.register(CxxMethodProxy)
        elif node == 'field':
            NodeFilter.register(CxxFieldProxy)
        elif node == 'enum':
            NodeFilter.register(CxxEnumProxy)
        elif node == 'enum_cst':
            NodeFilter.register(CxxEnumConstantProxy)
        elif node == 'variable':
            NodeFilter.register(CxxVariableProxy)
        elif node == 'parameter':
            NodeFilter.register(CxxParameterProxy)
        elif node == 'function':
            NodeFilter.register(CxxFunctionProxy)
        elif node == 'lvaluereference':
            NodeFilter.register(CxxLValueReferenceProxy)
        elif node == 'pointer':
            NodeFilter.register(CxxPointerProxy)
        elif node == 'type':
            NodeFilter.register(CxxTypeProxy)
        elif node == 'namespace':
            NodeFilter.register(CxxNamespaceProxy)

    graph = graph.subgraph([node for node in graph.nodes() if isinstance(__asg__[node], NodeFilter)])
    mapping = {j : i for i, j in enumerate(graph.nodes())}
    graph = networkx.relabel_nodes(graph, mapping)
    if not '|' in layout:
        layout = getattr(networkx, layout+'_layout')
        nodes = layout(graph)
    else:
        layout = getattr(networkx, layout.replace('|', '')+'_layout')
        nodes = layout(graph)
        nodes = networkx.spring_layout(graph, pos=nodes)
    if invert:
        fig = pyplot.figure(figsize=(size*aspect, size))
    else:
        fig = pyplot.figure(figsize=(size, size*aspect))
    axes = fig.add_subplot(1,1,1)
    axes.set_axis_off()
    mapping = {j : i for i, j in mapping.iteritems()}
    xmin = float("Inf")
    xmax = -float("Inf")
    ymin = float("Inf")
    ymax = -float("Inf")
    for node in graph.nodes():
        xmin = min(xmin, nodes[node][0])
        xmax = max(xmax, nodes[node][0])
        ymin = min(ymin, nodes[node][1])
        ymax = max(ymax, nodes[node][1])
        asgnode = __asg__[mapping[node]]
        if hasattr(asgnode, 'relpath'):
            asgnode = asgnode.relpath
        elif hasattr(asgnode, 'localname'):
            asgnode = asgnode.localname
        nodes[node] = axes.annotate(asgnode, nodes[node],
                xycoords = "data",
                color = 'k',
                bbox = dict(
                    boxstyle = 'round',
                    fc = 'w',
                    lw = 2.,
                    alpha = 1.,
                    ec = 'k'))
        nodes[node].draggable()
    for source, target in graph.edges():
        axes.annotate(" ",
                xy=(.5, .5),
                xytext=(.5, .5),
                ha="center",
                va="center",
                xycoords=nodes[target],
                textcoords=nodes[source],
                color="k",
                arrowprops=dict(
                    patchA = nodes[source].get_bbox_patch(),
                    patchB = nodes[target].get_bbox_patch(),
                    arrowstyle = '->',
                    connectionstyle = 'arc3,rad=0.',
                    lw=2.,
                    fc='k',
                    ec='k',
                    alpha=1.))
    axes.set_xlim(xmin, xmax)
    axes.set_ylim(ymin, ymax)
    return axes
