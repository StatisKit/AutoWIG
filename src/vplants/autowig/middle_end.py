import time

from .asg import *
from .bootstrap_middle_end import *
from .tools import FactoryDocstring

__all__ = [ 'AbstractSemanticGraph']

class MiddleEndDiagnostic(object):

    def __init__(self):
        self.preprocessing = None
        self.previous = 0
        self.current = 0
        self.marked = 0
        self.cleaning = 0.
        self.invalidating = 0.

    @property
    def total(self):
        if not self.processing is None:
            return self.cleaning + self.invalidating + self.preprocessing.total
        else:
            return self.cleaning + self.invalidating

def middle_end(self, identifier=None, *args, **kwargs):
    diagnostic = MiddleEndDiagnostic()
    if not identifier is None:
        middle_end = getattr(self, '_' + identifier + '_middle_end')
        diagnostic.preprocessing = middle_end(*args, **kwargs)
    self.clean(diagnostic=diagnostic)
    self.mark_invalid_pointers(diagnostic=diagnostic)
    return diagnostic

AbstractSemanticGraph.middle_end = middle_end
del middle_end
FactoryDocstring.as_factory(AbstractSemanticGraph.middle_end)

def get_traverse(self):
    if not '_traverse' in self.asg._nodes[self.node]:
        return True
    else:
        return self.asg._nodes[self.node]['_traverse']

def set_traverse(self, traverse):
    if not traverse:
        self.asg._nodes[self.node]['_traverse'] = traverse

def del_traverse(self):
    self.asg._nodes[self.node].pop('_traverse')

NodeProxy.traverse = property(get_traverse, set_traverse, del_traverse)
del get_traverse, set_traverse, del_traverse

def get_clean(self):
    if not hasattr(self, '_clean'):
        return self._clean_default
    else:
        return self._clean

def set_clean(self, clean):
    self.asg._nodes[self.node]['_clean'] = clean

def del_clean(self):
    self.asg._nodes[self.node].pop('_clean', False)

NodeProxy._clean_default = True
NodeProxy.clean = property(get_clean, set_clean, del_clean)
del get_clean, set_clean, del_clean

def _clean_default(self):
    return not self.parsed

FileProxy._clean_default = property(_clean_default)
del _clean_default

def _clean_default(self):
    header = self.header
    return header is None or header.clean

CodeNodeProxy._clean_default = property(_clean_default)
del _clean_default

FundamentalTypeProxy._clean_default = False

def _clean_default(self):
    header = self.header
    if header is None or header.clean:
        return True
    elif not self.is_complete:
        return True
    else:
        return False

EnumProxy._clean_default = property(_clean_default)
ClassProxy._clean_default = property(_clean_default)
del _clean_default

def get_clean(self):
    if not hasattr(self, '_clean'):
        return self._clean_default
    else:
        return self._clean

def set_clean(self, clean):
    self.asg._nodes[self.node]['_clean'] = clean
    for parameter in self.parameters:
        parameter.clean = clean

def del_clean(self):
    self.asg._nodes[self.node].pop('_clean', False)
    for parameter in self.parameters:
        del parameter.clean

FunctionProxy.clean = property(get_clean, set_clean, del_clean)
ConstructorProxy.clean = property(get_clean, set_clean, del_clean)
del get_clean, set_clean, del_clean

def clean(self, diagnostic=None):
    """
    """
    if not diagnostic is None:
        diagnostic.previous = len(self)
        prev = time.time()
    cleanbuffer = [(node, node._clean) for node in self.nodes() if hasattr(node, '_clean')]
    temp = []
    for node in self.nodes():
        if node.clean:
            node.clean = True
        else:
            temp.append(node)
    while len(temp) > 0:
        node = temp.pop()
        node.clean = False
        parent = node.parent
        if parent.clean:
            temp.append(parent)
        else:
            parent.clean = False
        if hasattr(node, 'header'):
            header = node.header
            if not header is None:
                if header.clean:
                    temp.append(header)
                else:
                    header.clean = False
        if isinstance(node, (TypedefProxy, VariableProxy)):
            underlying_type = node.type.target
            if underlying_type.clean:
                temp.append(underlying_type)
            else:
                underlying_type.clean = False
        elif isinstance(node, FunctionProxy):
            result_type = node.result_type.target
            if result_type.clean:
                temp.append(result_type)
            else:
                result_type.clean = False
            for parameter in node.parameters:
                if parameter.clean:
                    temp.append(parameter)
                else:
                    parameter.clean = False
        elif isinstance(node, ConstructorProxy):
            for parameter in node.parameters:
                if parameter.clean:
                    temp.append(parameter)
                else:
                    parameter.clean = False
        elif isinstance(node, ClassProxy):
            for base in node.bases():
                if base.clean:
                    temp.append(base)
                else:
                    base.clean = False
            if isinstance(node, ClassTemplateSpecializationProxy):
                for template in node.templates:
                    if template.target.clean:
                        temp.append(template.target)
                    else:
                        template.target.clean = False
    nodes = [node for node in self.nodes() if node.clean]
    for node in nodes:
        if not node.node in ['::', '/']:
            self._syntax_edges[node.parent.node].remove(node.node)
    for node in nodes:
        self._nodes.pop(node.node)
        self._syntax_edges.pop(node.node, None)
        self._base_edges.pop(node.node, None)
        self._type_edges.pop(node.node, None)
    for node in self.nodes():
        del node.clean
    for node, clean in cleanbuffer:
        if node.node in self:
            node.clean = clean
    if not diagnostic is None:
        diagnostic.current = len(self)
        curr = time.time()
        diagnostic.cleaning = curr - prev
    return diagnostic

AbstractSemanticGraph.clean = clean
del clean

def mark_invalid_pointers(self, diagnostic=None):
    marked = 0
    if not diagnostic is None:
        prev = time.time()
    for fct in self.functions(free=False):
        if fct.result_type.nested.is_pointer:
            fct.traverse = False
            marked += 1
        elif fct.result_type.is_pointer and isinstance(fct.result_type.target, FundamentalTypeProxy):
            fct.traverse = False
            marked += 1
        elif any(parameter.type.nested.is_pointer or parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in fct.parameters):
            fct.traverse = False
            marked += 1
    for cls in self.classes():
        for ctr in cls.constructors:
            if any(parameter.type.nested.is_pointer or parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in ctr.parameters):
                ctr.traverse = False
                marked += 1
    if not diagnostic is None:
        curr = time.time()
        diagnostic.invalidating = curr - prev
        diagnostic.marked = marked
    return diagnostic

AbstractSemanticGraph.mark_invalid_pointers = mark_invalid_pointers
del mark_invalid_pointers

def char_pointer_to_std_string(self):
    def is_char_pointer(proxy):
        return proxy.is_pointer and isinstance(proxy.target, CharTypeProxy)
    functions = [fct for fct in self.functions(free=True) if is_char_pointer(fct.result_type) or any(is_char_pointer(parameter.type) for parameter in fct.parameters)]
    content = ''
    for fct in functions:
        if is_char_pointer(fct.result_type):
            content += '::std::string'
        else:
            content += fct.result_type.globalname
        content += ' ' + fct.hash + '(' + ', '.join(['::std::string ' + prm.localname if is_char_pointer(prm.type) else prm.type.globalname + ' ' + prm.localname for prm in fct.parameters]) + ')\n'
        content += '{\n'
        for prm in fct.parameters:
            if is_char_pointer(prm):
                if prm.nested.is_const:
                    content += '\tchar const * _' + prm.localname + ' = ' + prm.localname + '.c_str();\n'
                else:
                    content += '\tchar * _' + prm.localname + ' = new char[' + prm.localname + '.length() + 1];\n'
                    content += '\t::std::strcpy(_' + prm.localname + ', ' + prm.localname + '.c_str());\n'
        content += fct.result_type.globalname + ' '
        if is_char_pointer(fct.result_type):
            content += '_'
        content += 'res = '
        content += fct.globalname + '(' + ', '.join('_' + prm.localname if is_char_pointer(prm) else prm.localname  for prm in fct.parameters) + ');\n'
        if is_char_pointer(fct.result_type):
            content += '::std::string res = ::std::string(_res);\n'
        for prm in fct.parameters:
            if is_char_pointer(prm):
                content += '\tdelete [] _' + prm.localname +';\n'
        if is_char_pointer(fct.result_type):
            content += '\tdelete [] _res;\n'
        content += '\treturn res;\n'
        content += '}\n'
    return content

AbstractSemanticGraph.char_pointer_to_std_string = char_pointer_to_std_string
del char_pointer_to_std_string

def c_struct_to_class(self):
    """
    """
    for cls in [cls for cls in self['::'].classes() if hasattr(cls, '_header') and cls.header.language == 'c' and cls.traverse]:
        for fct in [fct for fct in self['::'].functions() if fct.traverse]:
            mv = False
            rtype = fct.result_type
            if rtype.target.node == cls.node:
                self._nodes[fct.node].update(proxy=MethodProxy,
                        is_static=True,
                        is_virtual=False,
                        is_pure_virtual=False,
                        is_const=ptype.is_const,
                        as_constructor=True,
                        access='public')
                mv = True
            elif fct.nb_parameters > 0:
                ptype = fct.parameters[0].type
                if ptype.target.node == cls.node and (ptype.is_reference or ptype.is_pointer):
                    self._nodes[fct.node].update(proxy=MethodProxy,
                            is_static=False,
                            is_virtual=False,
                            is_pure_virtual=False,
                            is_const=ptype.is_const,
                            access='public')
                    mv = True
            if mv:
                self._syntax_edges[fct.parent.node].remove(fct.node)
                self._syntax_edges[cls.node].append(fct.node)

AbstractSemanticGraph.c_struct_to_class = c_struct_to_class
del c_struct_to_class
