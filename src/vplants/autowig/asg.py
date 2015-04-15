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
from fnmatch import fnmatch
import re
from .ast import AbstractSyntaxTree

class NodeProxy(object):
    """
    """

    def __init__(self, asg, node):
        self._asg = asg
        self._node = node

    def __repr__(self):
        return self._node

    def __dir__(self):
        return self._asg._nodes[self._node].keys()

    def __getattr__(self, attr):
        try:
            attr = self._asg._nodes[self._node][attr]
        except:
            raise AttributeError('\'' + self.__class__.__name__ + '\' object has no attribute \'' + attr + '\'')
        else:
            if isinstance(attr, basestring) and attr in self._asg:
                return self._asg[attr]
            else:
                return attr

    @property
    def hashname(self):
        return self.localname.replace(' ', '_') + '_' + str(uuid.uuid5(uuid.NAMESPACE_X500, self._node)).replace('-', '_')

class EdgeProxy(object):
    """
    """

class DirectoryProxy(NodeProxy):
    """
    """


    @property
    def globalname(self):
        return self._node

    @property
    def localname(self):
        return self.globalname[self.globalname.rfind(os.sep, 0, -1)+1:]

    def glob(self, pattern='*', on_disk=False):
        if on_disk:
            dirpath = path(self.globalname)
            if dirpath.exists():
                nodes = dirpath.glob(pattern)
            for node in nodes:
                nodepath = node.asbpath()
                if node.isdir():
                    self._asg._nodes[nodepath] = dict(proxy = DirectoryProxy)
                else:
                    self._asg._nodes[nodepath] = dict(proxy = FileProxy)
                self._asg._diredges[self._nodes].append(nodepath)
        return [self._asg[node] for node in self._asg._diredges[self._node] if fnmatch(node, pattern)]

    def walkdirs(self, pattern='*', on_disk=False):
        nodes = [node for node in self.glob(pattern=pattern, on_disk=on_disk) if isinstance(node, DirectoryProxy)]
        return nodes+list(itertools.chain(*[node.walkdirs(pattern, on_disk=on_disk) for node in nodes]))

    def walkfiles(self, pattern='*'):
        nodes = itertools.chain(*[node.glob(pattern) for node in self.walkdirs(on_disk=on_disk)])
        return [node for node in nodes if isinstance(node, FileProxy) and fnmatch(node.globalname, pattern)]

class FileProxy(NodeProxy):
    """
    """

    @property
    def globalname(self):
        return self._node

    @property
    def localname(self):
        return self.globalname[self.globalname.rfind(os.sep)+1:]

    def __str__(self):
        filepath = path(self.globalname)
        if not filepath.exists():
            if hasattr(self, '_template'):
                return self._template.render(obj=self)
            else: return ""
        else:
            return "".join(filepath.lines())

    @property
    def parent(self):
        return self._asg[self.globalname.replace(self.localname, '')]

class CxxFileProxy(FileProxy):
    """
    """

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

class CxxFundamentalTypeProxy(NodeProxy):
    """
    http://www.cplusplus.com/doc/tutorial/variables/
    """

    @property
    def globalname(self):
        return self._node

    @property
    def localname(self):
        return self._node

    def __str__(self):
        return self._node

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

    @property
    def ignore(self):
        return True

class CxxCharacterFundamentalTypeProxy(CxxFundamentalTypeProxy):
    """
    """

class CxxCharTypeProxy(CxxCharacterFundamentalTypeProxy):
    """
    """

    _node = 'char'

class CxxChar16TypeProxy(CxxCharacterFundamentalTypeProxy):
    """
    """

    _node = "char16_t"

class CxxChar32TypeProxy(CxxCharacterFundamentalTypeProxy):
    """
    """

    _node = "char32_t"

class CxxWCharTypeProxy(CxxCharacterFundamentalTypeProxy):
    """
    """

    _node = "wchar_t"

class CxxSignedIntegerTypeProxy(CxxFundamentalTypeProxy):
    """
    """

class CxxSignedShortIntegerTypeProxy(CxxSignedIntegerTypeProxy):
    """
    """

    _node = "short"

class CxxSignedIntegerTypeProxy(CxxSignedIntegerTypeProxy):
    """
    """

    _node = "int"

class CxxSignedLongIntegerTypeProxy(CxxSignedIntegerTypeProxy):
    """
    """

    _node = "long int"

class CxxSignedLongLongIntegerTypeProxy(CxxSignedIntegerTypeProxy):
    """
    """

    _node = "long long int"

class CxxUnsignedIntegerTypeProxy(CxxFundamentalTypeProxy):
    """
    """

class CxxUnsignedShortIntegerTypeProxy(CxxUnsignedIntegerTypeProxy):
    """
    """

    _node = "unsigned short"

class CxxUnsignedIntegerTypeProxy(CxxUnsignedIntegerTypeProxy):
    """
    """

    _node = "unsigned int"

class CxxUnsignedLongIntegerTypeProxy(CxxUnsignedIntegerTypeProxy):
    """
    """

    _node = "unsigned long int"

class CxxUnsignedLongLongIntegerTypeProxy(CxxUnsignedIntegerTypeProxy):
    """
    """

    _node = "unsigned long long int"

class CxxSignedFloatingPointTypeProxy(CxxFundamentalTypeProxy):
    """
    """

class CxxSignedFloatTypeProxy(CxxSignedFloatingPointTypeProxy):
    """
    """

    _node = "float"

class CxxSignedDoubleTypeProxy(CxxSignedFloatingPointTypeProxy):
    """
    """

    _node = "double"

class CxxSignedLongDoubleTypeProxy(CxxSignedFloatingPointTypeProxy):
    """
    """

    _node = "long double"

class CxxBoolTypeProxy(CxxFundamentalTypeProxy):
    """
    """

    _node = "bool"


class CxxVoidTypeProxy(CxxFundamentalTypeProxy):
    """
    """

    _node = "void"

class CxxTypeSpecifiersProxy(EdgeProxy):
    """
    http://en.cppreference.com/w/cpp/language/declarations
    """

    def __init__(self, asg, source):
        self._asg = asg
        self._source = source

    @property
    def type(self):
        return self._asg[self._asg._typeedges[self._source]["target"]]

    @property
    def specifiers(self):
        return self._asg._typeedges[self._source]["specifiers"]

    @property
    def globalname(self):
        return self.type.globalname + self.specifiers

    @property
    def localname(self):
        return self.type.localname + self.specifiers

    def __str__(self):
        return self.globalname

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

class CxxDeclarationProxy(NodeProxy):
    """
    """

    @property
    def globalname(self):
        if '-' in self._node:
            globalname = []
            for name in self._node.split('::'):
                if not '-' in name and not name == '':
                    globalname.append(name)
            return '::'+'::'.join(globalname)
        else:
            return self._node

    @property
    def localname(self):
        localname = self.globalname[self.globalname.rfind(':')+1:]
        if localname == '':
            return self._noname
        else:
            return localname

    @property
    def scope(self):
        scope = self._node[:self._node.rfind(':')-1]
        if scope == '':
            scope = '::'
        return self._asg[scope]

    def __contains__(self, node):
        return any(node == contained.replace(self._node, '').lstrip('::') for contained in self._asg._declarationedges.get(self._node, [])+self._asg._templateedges.get(self._node, []))

    def __getitem__(self, node):
        try:
            if self.globalname == '::':
                try:
                    return self._asg._nodes[node]["proxy"](self._asg, node)
                except:
                    return self._asg._nodes['::' + node]["proxy"](self._asg, '::' + node)
            else:
                if node.startswith('::'):
                    return self._asg._nodes[node]["proxy"](self._asg, node)
                else:
                    scope = self
                    while not node in scope and not scope.globalname == '::':
                        scope = scope.scope
                    if scope._node.endswith('::'):
                        nodescope = scope._node + node
                    else:
                        nodescope = scope._node + '::' + node
                    return self._asg._nodes[nodescope]["proxy"](self._asg, nodescope)
        except:
            if re.match('(.*)<(.*)>$', node):
                if node.startswith('::'):
                    pattern = re.sub('(.*)<(.*)>$', r'^\1<(.*)>$', node)
                else:
                    pattern = re.sub('(.*)<(.*)>$', r'(.*)::\1<(.*)>$', node)
                candidates = self._asg[pattern]
                if len(candidates) == 0:
                    raise NotImplementedError()
                else:
                    max = -1*float('INFINITY')
                    argmax = None
                    scopes = self.scope.globalname.split('::')
                    templates = [template.strip() for template in re.sub('(.*)<(.*)>$', r'\2', node).split(',')]
                    nb_templates = len(templates)
                    pattern = '(' + "|".join('::'.join(scopes[:scope+1]) for scope in reversed(range(len(scopes)))) + '::)(.*)'
                    for candidate in candidates:
                        if isinstance(candidate, CxxClassTemplateProxy):
                            match = re.match(pattern, candidate.globalname)
                            if match and candidate.nb_templates == nb_templates and candidate.primary:
                                max = len(match.group(1))
                                argmax = candidate
                    templates = []
                    for template in re.sub('(.*)<(.*)>$', r'\2', node).split(','):
                        try:
                            templates.append(self[template.strip()])
                        except:
                            templates.append(template.strip())
                    globalname = re.sub('(.*)::<(.*)>$', r'\1< ' + ', '.join(template.globalname if not isinstance(template, basestring) else template for template in templates) + ' >',argmax.globalname)
                    if argmax.specialized:
                        max = argmax.match(globalname)
                        for specialization in argmax.specializations:
                            if isinstance(specialization, CxxClassTemplateProxy):
                                current = specialization.match(globalname)
                                if current > max:
                                    max = current
                                    argmax = specialization
                    return argmax.instantiate(False, *templates)
            else:
                raise ValueError('\'node\' parameter')

    def _repr_html_(self):
        return highlight(str(self), CppLexer(), HtmlFormatter(full = True))

    def __str__(self):
        if hasattr(self, '_template'):
            return self._template.render(obj=self)
        else:
            return self.globalname

    @property
    def ignore(self):
        return False

class CxxEnumConstantProxy(CxxDeclarationProxy):
    """
    """

class CxxParameterProxy(CxxDeclarationProxy):
    """
    """

    @property
    def type(self):
        return CxxTypeSpecifiersProxy(self._asg, self._node)

    def __str__(self):
        return self.type.globalname + " " + self.localname

class CxxTemplateParameterProxy(CxxDeclarationProxy):
    """
    """

    def __str__(self):
        return 'class ' + self.localname

class CxxTemplateNonTypeParameterProxy(CxxTemplateParameterProxy):
    """
    """

    @property
    def type(self):
        return CxxTypeSpecifiersProxy(self._asg, self._node)

    def __str__(self):
        return self.type.globalname + ' ' + self.localname

class CxxDeclarationProxy(CxxDeclarationProxy):
    """
    """

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
typedef ${obj.localname} ${obj.type.globalname};
""")

    @property
    def type(self):
        return CxxTypeSpecifiersProxy(self._asg, self._node)

class CxxVariableProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
% if obj.static:
static \
% endif
${obj.type.globalname} ${obj.localname};""")

    @property
    def type(self):
        return CxxTypeSpecifiersProxy(self._asg, self._node)

class CxxFieldProxy(CxxVariableProxy):
    """
    """

    _template =  Template(text=r"""\
% if obj.mutable:
mutable \
% elif obj.static:
static \
% endif
${obj.type.globalname} ${obj.localname};""")

class CxxFunctionProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
${obj.result_type.globalname} ${obj.localname}(${", ".join(parameter.type.globalname + ' ' + parameter.localname for parameter in obj.parameters)});""")

    @property
    def result_type(self):
        return CxxTypeSpecifiersProxy(self._asg, self._node)

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._declarationedges[self._node]]

    @property
    def scope(self):
        scope = self.globalname[:self.globalname.rfind(':')-1]
        if scope == '':
            scope = '::'
        return self._asg[scope]

    @property
    def overloaded(self):
        if not self._asg._frozen:
            raise ValueError('')
        if not overloaded in self._asg[node]:
            overloads = self._asg["^" + self.scope._node + "(.*)-(.*)-(.*)-(.*)-(.*)" + self.localname + "$"]
            if len(overloads) == 1:
                self._asg[node]["overloaded"] = False
            else:
                for overload in overloads:
                    self._nodes[overload._node]["overloaded"] = True
        return self._asg[self._node]["overloaded"]

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
${obj.result_type.globalname} ${obj.localname}(${", ".join(parameter.type.globalname + ' ' + parameter.localname for parameter in obj.parameters)})\
% if obj.const:
 const\
% endif
% if obj.pure_virtual:
 = 0\
% endif
;""")

class CxxConstructorProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
${obj.localname}(${", ".join(parameter.type.globalname + ' ' + parameter.localname for parameter in obj.parameters)});""")

    @property
    def parameters(self):
        return [self._asg[node] for node in self._asg._declarationedges[self._node]]

    @property
    def scope(self):
        scope = self.globalname[:self.globalname.rfind(':')-1]
        if scope == '':
            scope = '::'
        return self._asg[scope]

    @property
    def overloaded(self):
        if not self._asg._frozen:
            raise ValueError('')
        if not overloaded in self._asg[node]:
            overloads = self._asg[self.scope._node + "(.*)-(.*)-(.*)-(.*)-(.*)" + self.localname + "$"]
            if len(overloads) == 1:
                self._asg[node]["overloaded"] = False
            else:
                for overload in overloads:
                    self._nodes[overload._node]["overloaded"] = True
        return self._asg[self._node]["overloaded"]

class CxxDestructorProxy(CxxDeclarationProxy):
    """
    """

    _template = Template(text=r"""\
% if obj.virtual:
virtual \
% endif
${obj.localname}();""")

class CxxClassProxy(CxxDeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/class>_`
    """

    _template = Template(text=r"""<% access = obj.default_access %>\
class ${obj.localname}\
% if obj.derived:
 : ${", ".join(base.access + " " + base.globalname for base in obj.bases())}
% else:

% endif
{
% for declaration in obj.declarations():
    % if not access == declaration.access:
        ${declaration.access}:
<% access = declaration.access %>\
    % endif
            ${str(declaration)}
% endfor
};""")

    def __init__(self, asg, node):
        super(CxxDeclarationProxy, self).__init__(asg, node)
        #if self.forward_declaration and hasattr(self, 'instantiation'):
        #    pass # TODO build nodes corresponding to methods etc.

    @property
    def forward_declaration(self):
        return len(self.bases()) + len(self.declarations()) == 0

    @property
    def derived(self):
        return len(self._asg._baseedges[self._node]) > 0

    @property
    def localname(self):
        match = re.match('(.*)<(.*)>$', self._node)
        if match:
            localname = match.group(1)
            localname = localname[localname.rindex(':')+1:]
            return localname + '< ' + match.group(2) + ' >'
        else:
            return super(CxxDeclarationProxy, self).localname

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
                if isinstance(base, CxxClassSpecializationProxy):
                    basebases = base.specialize.bases(True)
                else:
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

    def declarations(self, inherited=False):
        declarations = [self._asg[node] for node in self._asg._declarationedges[self._node]]
        if not inherited:
            return declarations
        else:
            for base in self.bases(True):
                if isinstance(base, CxxClassSpecializationProxy):
                    basedeclarations = [basedeclaration for basedeclaration in base.specialize.declarations(False) if not basedeclaration.access == 'private']
                else:
                    basedeclarations = [basedeclaration for basedeclaration in base.declarations(False) if not basedeclaration.access == 'private']
                if base.access == 'protected':
                    for basedeclaration in basedeclarations:
                        if basedeclaration.access == 'public':
                            basedeclaration.access = 'protected'
                elif base.access == 'private':
                   for basedeclaration in basedeclarations:
                        basedeclaration.access = 'private'
                declarations += basedeclarations
            return declarations

    def enums(self, inherited=False):
        return [enum for enum in self.declarations(inherited) if isinstance(enum, CxxEnumProxy)]

    def fields(self, inherited=False):
        return [field for field in self.declarations(inherited) if isinstance(field, CxxFieldProxy)]

    def methods(self, inherited=False):
        return [method for method in self.declarations(inherited) if isinstance(method, CxxMethodProxy)]

    def classes(self, inherited=False):
        return [klass for klass in self.declarations(inherited) if isinstance(klass, CxxClassProxy)]

    @property
    def constructors(self):
        return [constructor for constructor in self.declarations(False) if isinstance(constructor, CxxConstructorProxy)]

    @property
    def destructor(self):
        try:
            return [destructor for destructor in self.declarations(False) if isinstance(destructor, CxxDestructorProxy)].pop()
        except:
            return None

    @property
    def pure_virtual(self):
        if not hasattr(self, '_pure_virtual'):
            blackmethods = set()
            whitemethods = set()
            for method in self.methods(True):
                if method.virtual:
                    if method.pure_virtual:
                        blackmethods.add(method.signature)
                    else:
                        whitemethods.add(method.signature)
            self._pure_virtual = len(blackmethods-whitemethods) > 0
        return self._pure_virtual

class CxxClassTemplateProxy(CxxClassProxy):
    """
    """

    _template = Template(text=r"""<% access = obj.default_access %>\
template< ${', '.join(str(template) for template in obj.templates)} >
class ${obj.localname}\
% if obj.derived:
 : ${", ".join(base.access + " " + base.globalname for base in obj.bases())}
% else:

% endif
{
};""")

    @property
    def templates(self):
        return [self._asg[template] for template in self._asg._templateedges[self._node]]

    @property
    def nb_templates(self):
        return len(self._asg._templateedges[self._node])

    def match(self, spelling):
        pattern = self.globalname
        for template in self.templates:
            pattern = pattern.replace(' ' + template.localname, ' (.*)')
        match = re.match(pattern, spelling)
        if match is None:
            return 0
        else:
            return len(match.groups())

    @property
    def specializations(self):
        return [self._asg[node] for node in self._asg._specializationedges.get(self._node, [])]

    @property
    def specialized(self):
        return len(self._asg._specializationedges.get(self._node, [])) > 0

    def instantiate(self, default, *templates):
        if len(templates) == 0:
            raise ValueError('`templates` parameter')
        if not default and not len(templates) == self.nb_templates :
            raise ValueError('`globalname` parameter')
        elif default:# and len(templates) =< self.nb_templates:
            raise ValueError('`globalname` parameter')
        if any(isinstance(template, CxxTemplateParameterProxy) for template in templates):
            node = re.sub('(.*)<(.*)>$', r'\1'+ '< ' + ', '.join(template.localname if not isinstance(template, CxxTemplateParameterProxy) else template.localname if not isinstance(template, basestring) else template for template in templates) + ' >', self._node)
            if not node in self._asg._nodes:
                self._asg._nodes[node] = dict(proxy = CxxClassTemplateProxy, default_access = self.default_access, primary=False, instantiation=self._node)
                self._asg._declarationedges[node] = []
                self._asg._baseedges[node] = []
                self._asg._templateedges[node] = []
                for template in templates:
                    if isinstance(template, CxxTemplateParameterProxy):
                        templatenode = node + '::' + template.localname
                        self._asg._nodes[templatenode] = self._asg._nodes[template._node]
                        if isinstance(template, CxxTemplateNonTypeParameterProxy):
                            self._asg._typeedges[templatenode] = self._asg._typeedges[template._node]
                        self._asg._templateedges[node].append(templatenode)
                self._asg._declarationedges[self.scope._node].append(node)
            return self._asg[node]
        else:
            node = re.sub('(.*)<(.*)>$', r'\1'+ '< ' + ', '.join(template.globalname if not isinstance(template, basestring) else template for template in templates) + ' >', self._node)
            if not node in self._asg._nodes:
                self._asg._nodes[node] = dict(proxy = CxxClassProxy, default_access = self.default_access, primary=False, instantiation=self._node)
                self._asg._declarationedges[node] = []
                self._asg._baseedges[node] = []
                self._asg._declarationedges[self.scope._node].append(node)
            return self._asg[node]

    #def specialize(self, *args):
    #    if not len(args) == len(self._asg._templateedges[self._node]):
    #        raise NotImplementedError('partial specialization of \'' + self.__class__.__name__ + '\' is not implemented')
    #    if any(isinstance(base, CxxClassTemplateProxy) for base in self.bases()):
    #        raise NotImplementedError('specialization of \'' + self.__class__.__name__ + '\' with template base classes is not implemented')
    #    scope = re.sub('<(.*)>',  '<' + ', '.join(arg.globalname for arg in args) + '>', self._node)
    #    self._asg._nodes[scope] = dict(proxy = CxxClassProxy)
    #    self._asg._declarationedges[scope] = []
    #    self._asg._baseedges[scope] = self._asg._baseedges[self._node]
    #    for declaration in self.declarations():
    #        if isinstance(declaration, CxxMethodProxy):
    #            methodscope = declaration._node.replace(self._node, scope)
    #            self._asg._nodes[methodscope] = self._asg._nodes[declaration._node]
    #            self._asg._typeedges[methodscope] = self._asg._typeedges[declaration._node]
    #            for arg in args:
    #                match = re.match('((.*)\s|^)' + arg.localname + '(\s(.*)|$)', declaration.result_type.localname)
    #                if match:
    #                    newscope = match.group(1)
    #                    if not newscope == '':
    #                        newnode += ' '
    #                    newscope += arg.globalname
    #                    if not match.group(4) == '':
    #                        newscope += ' ' + match.group(4)
    #                    if not newscope in self._asg._nodes:
    #                        raise NotImplementedError()
    #                    self._asg._typedges[methodscope] = self._asg[newscope]._node
    #                    break
    #            self._asg._declarationedges[methodscope] = []
    #            for parameter in declaration.parameters:
    #                self._asg._declarationedges[methodscope].append(parameter._node)
    #                for arg in args:
    #                    match = re.match('((.*)\s|^)' + arg.localname + '(\s(.*)|$)', parameter.localname)
    #                    if match:
    #                        newscope = match.group(1)
    #                        if not newscope == '':
    #                            newnode += ' '
    #                        newscope += arg.globalname
    #                        if not match.group(4) == '':
    #                            newscope += ' ' + match.group(4)
    #                        if not newscope in self._asg._nodes:
    #                            raise NotImplementedError()
    #                        self._asg._declarationedges[methodscope][-1] = self._asg[newscope]._node
    #                        break
    #            self._asg._declarationedges[scope].append(methodscope)
    #        elif isinstance(declaration, CxxFieldProxy):
    #            fieldscope = declaration._node.replace(self._node, scope)
    #            self._asg._nodes[fieldscope] = self._asg._nodes[declaration._node]
    #            self._asg._typeedges[fieldscope] = self._asg._typeedges[declaration._node]
    #            for template, specialization in zip(self.templates, args):
    #                if self._asg._typeedges[fieldscope] == template._node:
    #                    self._asg._typeedges[fieldscope] = specialization._node
    #                    break
    #        elif isinstance(declaration, (CxxConstructorProxy, CxxDestructorProxy)):
    #            continue
    #        else:
    #            raise NotImplementedError('specialization of \'' + self.__class__.__name__ + '\' with enumerations or nested classes is not implemented')
    #    return scope

class CxxNamespaceProxy(CxxDeclarationProxy):
    """

    .. see:: `<http://en.cppreference.com/w/cpp/language/namespace>_`
    """

    def __init__(self, asg, node):
        super(CxxDeclarationProxy, self).__init__(asg, node)
        if node == '::':
            self._noname = '::'
        else:
            self._noname = 'namespace'

    @property
    def anonymous(self):
        return '-' in self._node

    def declarations(self, nested=False):
        declarations = [self._asg[node] for node in self._asg._declarationedges[self._node]]
        if not nested:
            return declarations
        else:
            declarations = [declaration for declaration in declarations if not isinstance(declaration, CxxNamespaceProxy)]
            for nestednamespace in self.namespaces(False):
                for nesteddeclaration in nestednamespace.declarations(True):
                    declarations.append(nesteddeclaration)
            return declarations

    def enums(self, nested=False):
        return [enum for enum in self.declarations(nested) if isinstance(enum, CxxEnumProxy)]

    def variables(self, nested=False):
        return [variable for variable in self.declarations(nested) if isinstance(variable, CxxVariableProxy)]

    def functions(self, nested=False):
        return [function for function in self.declarations(nested) if isinstance(function, CxxFunctionProxy)]

    def classes(self, nested=False):
        return [klass for klass in self.declarations(nested) if isinstance(klass, CxxClassProxy)]

    def namespaces(self, nested=False):
        if not nested:
            return [namespace for namespace in self.declarations(nested) if isinstance(namespace, CxxNamespacePRoxy)]
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
        self._baseedges = dict()
        self._templateedges = dict()
        self._specializationedges = dict()
        self._typeedges = dict()
        self._diredges = dict()
        self._frozen = False
        self._filepaths = ast.filepaths
        #try:
        self._read_ast(ast.translation_unit.cursor, **kwargs)
        #except Exception as e:
        #    raise e
        del self._filepaths
        self._frozen = True

    def _read_ast(self, node, scope='::', **kwargs):
        if self._frozen:
            raise Exception('`AbstractSemanticGraph` instance is frozen')
        if isinstance(node, Cursor):
            if node.kind is CursorKind.TRANSLATION_UNIT:
                self._nodes['::'] = dict(proxy = CxxNamespaceProxy)
                self._declarationedges['::'] = []
                for child in node.get_children():
                    childscope = self._read_ast(child, scope='::')
                    #if not childscope is None and not childscope in self._declarationedges['::']:
                    #    self._declarationedges['::'].append(childscope)
            elif str(node.location.file) in self._filepaths:
                if not scope.endswith('::'):
                    spelling = scope + "::" + node.spelling
                else:
                    spelling = scope + node.spelling
                if node.kind is CursorKind.ENUM_DECL:
                    if node.spelling == '':
                        spelling += str(uuid.uuid4())
                    self._declarationedges[spelling] = []
                    self._nodes[spelling] = dict(proxy = CxxEnumProxy)
                    self._declarationedges[scope].append(spelling)
                    for child in node.get_children():
                        self._read_ast(child, spelling)
                    filename = str(node.location.file)
                    self._add_file(filename, file_proxy=CxxFileProxy)
                    self._nodes[spelling]['header'] = filename
                    return spelling
                elif node.kind is CursorKind.ENUM_CONSTANT_DECL:
                    self._nodes[spelling] = dict(proxy = CxxEnumConstantProxy)
                    self._declarationedges[scope].append(spelling)
                    return spelling
                elif node.kind in [CursorKind.VAR_DECL, CursorKind.FIELD_DECL]:
                    if node.kind is CursorKind.VAR_DECL:
                        self._nodes[spelling] = dict(proxy = CxxVariableProxy,
                                static=False) # TODO
                        filename = str(node.location.file)
                        self._add_file(filename, file_proxy=CxxFileProxy)
                        self._nodes[spelling]['header'] = filename
                    else:
                        self._nodes[spelling] = dict(proxy = CxxFieldProxy,
                                mutable=False, # TODO
                                static=False) # TODO
                    self._declarationedges[scope].append(spelling)
                    self._read_ast(node.type, spelling)
                    return spelling
                elif node.kind is CursorKind.PARM_DECL:
                    self._nodes[spelling] = dict(proxy = CxxParameterProxy)
                    self._declarationedges[scope].append(spelling)
                    self._read_ast(node.type, spelling)
                    return spelling
                elif node.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD, CursorKind.DESTRUCTOR, CursorKind.CONSTRUCTOR]:
                    if not node.kind is CursorKind.DESTRUCTOR:
                        spelling = spelling + '::' + str(uuid.uuid4())
                    if node.kind is CursorKind.FUNCTION_DECL:
                        self._nodes[spelling] = dict(proxy = CxxFunctionProxy)
                        if not node.location is None:
                            filename = str(node.location.file)
                            self._add_file(filename, file_proxy=CxxFileProxy)
                            self._nodes[spelling]['header'] = filename
                    elif node.kind is CursorKind.CXX_METHOD:
                            self._nodes[spelling] = dict(proxy = CxxMethodProxy,
                                    static = node.is_static_method(),
                                    virtual = node.is_virtual_method(),
                                    const = node.type.is_const_qualified(),
                                    pure_virtual = node.is_pure_virtual_method())
                    elif node.kind is CursorKind.CONSTRUCTOR:
                            self._nodes[spelling] = dict(proxy = CxxConstructorProxy)
                    else:
                        self._nodes[spelling] = dict(proxy = CxxDestructorProxy, virtual=node.is_virtual_method())
                    self._declarationedges[spelling] = []
                    self._declarationedges[scope].append(spelling)
                    for child in node.get_children():
                        if child.kind is CursorKind.PARM_DECL:
                            self._read_ast(child, spelling)
                    if not node.kind in [CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR]:
                        self._read_ast(node.result_type, spelling)
                    return spelling
                elif node.kind in [CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL, CursorKind.CLASS_TEMPLATE, CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION]:
                    primary = True
                    if re.match('(.*)<(.*)>$', node.displayname):
                        primary = node.kind is CursorKind.CLASS_TEMPLATE
                        templates = [template.strip() for template in re.sub('(.*)<(.*)>$', r'\2', node.displayname).split(',')]
                        spelling += '< ' + ', '.join(templates) + ' >'
                    if not spelling in self._nodes:
                        if node.kind is CursorKind.STRUCT_DECL:
                            self._nodes[spelling] = dict(proxy = CxxClassProxy, default_access = 'public', primary=primary)
                        elif node.kind is CursorKind.CLASS_DECL:
                            self._nodes[spelling] = dict(proxy = CxxClassProxy, default_access = 'private', primary=primary)
                        elif node.kind is CursorKind.CLASS_TEMPLATE:
                            self._nodes[spelling] = dict(proxy = CxxClassTemplateProxy, default_access = 'private', primary=primary)
                            self._templateedges[spelling] = []
                            self._specializationedges[spelling] = []
                        elif node.kind is CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                            self._nodes[spelling] = dict(proxy = CxxClassTemplateProxy, default_access = 'private', primary=primary)
                            self._templateedges[spelling] = []
                            primary = None
                        self._declarationedges[spelling] = []
                        self._baseedges[spelling] = []
                    if spelling in self._declarationedges[scope] and self[spelling].forward_declaration:
                        self._declarationedges[scope].remove(spelling)
                    if not spelling in self._declarationedges[scope]:
                        self._declarationedges[scope].append(spelling)
                    if len(self._templateedges.get(spelling, [])) > 0:
                        self._templateedges[spelling] = []
                        #raise NotImplementedError('forward declaration of template classes')
                    if not primary:
                        for klass in self[re.sub('(.*)<(.*)>$', r'^\1<(.*)>$', spelling)]:
                            if isinstance(klass, CxxClassTemplateProxy) and klass.primary and klass.nb_templates == len(templates):
                                primary = klass._node
                        if not spelling in self._specializationedges[primary]:
                            self._specializationedges[primary].append(spelling)
                    for child in node.get_children():
                        if child.kind is CursorKind.CXX_BASE_SPECIFIER:
                            base = self[spelling][child.type.spelling]._node
                            access = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                            self._baseedges[spelling].append(dict(
                                base = base,
                                access = access))
                        elif child.kind is CursorKind.TEMPLATE_TYPE_PARAMETER:
                            childspelling = spelling + "::" + child.spelling
                            self._nodes[childspelling] = dict(proxy = CxxTemplateParameterProxy)
                            self._templateedges[spelling].append(childspelling)
                        elif child.kind is CursorKind.TEMPLATE_NON_TYPE_PARAMETER:
                            childspelling = spelling + "::" + child.spelling
                            self._nodes[childspelling] = dict(proxy = CxxTemplateNonTypeParameterProxy)
                            self._templateedges[spelling].append(childspelling)
                            self._read_ast(child.type, childspelling)
                        elif child.kind in [CursorKind.ENUM_DECL, CursorKind.CXX_METHOD, CursorKind.FIELD_DECL, CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR, CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL, CursorKind.CLASS_TEMPLATE]:
                            childspelling = self._read_ast(child, spelling)
                            if not childspelling is None:
                                self._nodes[childspelling]["access"] = str(child.access_specifier)[str(child.access_specifier).index('.')+1:].lower()
                    if len(self._declarationedges[spelling])+len(self._baseedges[spelling]) > 0 and not 'header' in self._nodes[spelling]:
                        filename = str(node.location.file)
                        self._add_file(filename, file_proxy=CxxFileProxy)
                        self._nodes[spelling]['header'] = filename
                    return spelling
                elif node.kind is CursorKind.NAMESPACE:
                    if not spelling in self._nodes:
                        self._nodes[spelling] = dict(proxy = CxxNamespaceProxy)
                        self._declarationedges[spelling] = []
                    for child in node.get_children():
                        self._read_ast(child, spelling)
                    return spelling
                else:
                    raise NotImplementedError("(" + scope + ")" + node.spelling + ': ' + str(node.kind))
        elif isinstance(node, Type):
            specifiers = ''
            done = False
            while not done:
                if node.kind is TypeKind.LVALUEREFERENCE:
                    specifiers = ' &' + specifiers
                    node = node.get_pointee()
                elif node.kind is TypeKind.POINTER:
                    specifiers = ' *' + ' const'*node.is_const_qualified() + specifiers
                    node = node.get_pointee()
                elif node.kind is TypeKind.RECORD:
                    spelling = node.spelling
                    if node.is_const_qualified():
                        spelling = spelling.replace('const' ,'')
                        specifiers = ' const' + specifiers
                    spelling = spelling.replace(' ', '')
                    node = self[scope][spelling]._node
                    self._typeedges[scope] = dict(target=node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.UNEXPOSED:
                    spelling = node.spelling
                    if node.is_const_qualified():
                        spelling = spelling.replace('const' ,'')
                        specifiers = ' const' + specifiers
                    spelling = spelling.replace(' ', '')
                    node = self[scope][spelling]._node
                    self._typeedges[scope] = dict(target=node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.CHAR16: # TODO CHAR
                    if not CxxChar16TypeProxy._node in self._nodes:
                        self._nodes[CxxChar16TypeProxy._node] = dict(proxy = CxxChar16TypeProxy)
                        self._declarationedges['::'].append(CxxChar16TypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxChar16TypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.CHAR32:
                    if not CxxChar32TypeProxy._node in self._nodes:
                        self._nodes[CxxChar32TypeProxy._node] = dict(proxy = CxxChar32TypeProxy)
                        self._declarationedges['::'].append(CxxChar32TypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxChar32TypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.WCHAR:
                    if not CxxWCharTypeProxy._node in self._nodes:
                        self._nodes[CxxWCharTypeProxy._node] = dict(proxy = CxxWCharTypeProxy)
                        self._declarationedges['::'].append(CxxWCharTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxWCharTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.SHORT:
                    if not CxxSignedShortIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedShortIntegerTypeProxy._node] = dict(proxy = CxxSignedShortIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxSignedShortIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedShortIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.INT:
                    if not CxxSignedIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedIntegerTypeProxy._node] = dict(proxy = CxxSignedIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxSignedIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.LONG:
                    if not CxxSignedLongIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedLongIntegerTypeProxy._node] = dict(proxy = CxxSignedLongIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxSignedLongIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedLongIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.LONGLONG:
                    if not CxxSignedLongLongIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedLongLongIntegerTypeProxy._node] = dict(proxy = CxxSignedLongLongIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxSignedLongLongIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedLongLongIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.USHORT:
                    if not CxxUnsignedShortIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxUnsignedShortIntegerTypeProxy._node] = dict(proxy = CxxUnsignedShortIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxUnsignedShortIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxUnsignedShortIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.UINT:
                    if not CxxUnsignedIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxUnsignedIntegerTypeProxy._node] = dict(proxy = CxxUnsignedIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxUnsignedIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxUnsignedIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.ULONG:
                    if not CxxUnsignedLongIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxUnsignedLongIntegerTypeProxy._node] = dict(proxy = CxxUnsignedLongIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxUnsignedLongIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxUnsignedLongIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.ULONGLONG:
                    if not CxxUnsignedLongLongIntegerTypeProxy._node in self._nodes:
                        self._nodes[CxxUnsignedLongLongIntegerTypeProxy._node] = dict(proxy = CxxUnsignedLongLongIntegerTypeProxy)
                        self._declarationedges['::'].append(CxxUnsignedLongLongIntegerTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxUnsignedLongLongIntegerTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.FLOAT:
                    if not CxxSignedFloatTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedFloatTypeProxy._node] = dict(proxy = CxxSignedFloatTypeProxy)
                        self._declarationedges['::'].append(CxxSignedFloatTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedFloatTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.DOUBLE:
                    if not CxxSignedDoubleTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedDoubleTypeProxy._node] = dict(proxy = CxxSignedDoubleTypeProxy)
                        self._declarationedges['::'].append(CxxSignedDoubleTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedDoubleTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.LONGDOUBLE:
                    if not CxxSignedLongDoubleTypeProxy._node in self._nodes:
                        self._nodes[CxxSignedLongDoubleTypeProxy._node] = dict(proxy = CxxSignedLongDoubleTypeProxy)
                        self._declarationedges['::'].append(CxxSignedLongDoubleTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxSignedLongDoubleTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.BOOL:
                    if not CxxBoolTypeProxy._node in self._nodes:
                        self._nodes[CxxBoolTypeProxy._node] = dict(proxy = CxxBoolTypeProxy)
                        self._declarationedges['::'].append(CxxBoolTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxBoolTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                elif node.kind is TypeKind.VOID:
                    if not CxxVoidTypeProxy._node in self._nodes:
                        self._nodes[CxxVoidTypeProxy._node] = dict(proxy = CxxVoidTypeProxy)
                        self._declarationedges['::'].append(CxxVoidTypeProxy._node)
                    if node.is_const_qualified():
                        specifiers = ' const' + specifiers
                    self._typeedges[scope] = dict(target=CxxVoidTypeProxy._node,
                            specifiers=specifiers)
                    done = True
                else:
                    raise NotImplementedError("(" + scope + ")" + node.spelling + ': ' + str(node.kind))

    def _add_file(self, filename, file_proxy):
        if not filename in self._nodes:
            self._nodes[filename] = dict(proxy = file_proxy)
            dirname = filename[:filename.rfind(os.sep)+1]
            if not dirname in self._nodes:
                while not dirname == '' and not dirname in self._nodes:
                    self._nodes[dirname] = dict(proxy = DirectoryProxy)
                    self._diredges[dirname] = [filename]
                    filename = dirname
                    dirname = filename[:filename.rfind(os.sep, 0, -1)+1]
                if not dirname == '':
                    self._diredges[dirname].append(filename)
            else:
                self._diredges[dirname].append(filename)

    @property
    def nodes(self):
        return [self[node] for node in self._nodes.keys()]

    def __contains__(self, node):
        return node in self._nodes

    def __getitem__(self, node):
        if not isinstance(node, basestring):
            raise TypeError('`node` parameter')
        if not node in self._nodes:
            try:
                pattern = re.compile(node)
                return [self[_node] for _node in self._nodes if pattern.match(_node)]
            except:
                raise
                #ValueError('`node` parameter is not a valid regex pattern')
        else:
            return self._nodes[node]["proxy"](self, node)

    def _ipython_display_(self):
        global __asg__
        __asg__ = self
        interact(plot,
                layout=('graphviz', 'circular', 'random', 'spring', 'spectral'),
                size=(0., 60., .5),
                aspect=(0., 1., .01),
                pattern='(.*)')

def plot(layout='graphviz', size=16, aspect=.5, invert=False, pattern='(.*)', **kwargs):
    global __asg__
    graph = networkx.DiGraph()
    for node in __asg__._nodes:
        if not isinstance(node, CxxFundamentalTypeProxy):
            graph.add_node(node)
    for source, targets in __asg__._declarationedges.iteritems():
        for target in targets: graph.add_edge(source, target, color='k', linestyle='solid')
    for source, targets in __asg__._templateedges.iteritems():
        for target in targets: graph.add_edge(source, target, color='g', linestyle='solid')
    for target, sources in __asg__._specializationedges.iteritems():
        for source in sources: graph.add_edge(source, target, color='y', linestyle='dashed')
    for source, target in __asg__._typeedges.iteritems():
        graph.add_edge(source, target['target'], color='r', linestyle='solid')
    for source, properties in __asg__._nodes.iteritems():
        if 'instantiation' in properties:
            graph.add_edge(source, properties['instantiation'], color='y', linestyle='solid')
    for source, targets in __asg__._diredges.iteritems():
        for target in targets: graph.add_edge(source, target, color='k', linestyle='solid')
    for source, targets in __asg__._baseedges.iteritems():
        for target in targets: graph.add_edge(source, target['base'], color='m', linestyle='solid')

    graph = graph.subgraph([node for node in graph.nodes() if re.match(pattern, node)])
    mapping = {j : i for i, j in enumerate(graph.nodes())}
    graph = networkx.relabel_nodes(graph, mapping)
    layout = getattr(networkx, layout+'_layout')
    nodes = layout(graph)
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
        nodes[node] = axes.annotate(asgnode.localname, nodes[node],
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
                    linestyle = graph.edge[source][target]['linestyle'],
                    connectionstyle = 'arc3,rad=0.',
                    lw=2.,
                    fc=graph.edge[source][target]['color'],
                    ec=graph.edge[source][target]['color'],
                    alpha=1.))
    axes.set_xlim(xmin, xmax)
    axes.set_ylim(ymin, ymax)
    return axes
