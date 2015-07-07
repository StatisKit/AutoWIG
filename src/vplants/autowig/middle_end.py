from .asg import *
from .bootstrap import bootstrap_middle_end

__all__ = [ 'AbstractSemanticGraph', 'set_middle_end']

def set_middle_end(middle_end, *args, **kwargs):
    if middle_end == 'reflexive':
        def middle_end(self):
            """
            """
            diagnostic = self.clean()
            self.mark_invalid_pointers()
            return diagnostic
        AbstractSemanticGraph.middle_end = middle_end
        del middle_end
    elif middle_end == 'bootstrap':
        AbstractSemanticGraph.middle_end = bootstrap_middle_end
    else:
        raise ValueError('\'middle_end\' parameter')

set_middle_end('reflexive')

class CleanedDiagnostic(object):

    def __init__(self, previous, current):
        self.previous = previous
        self.current = current

    def __repr__(self):
        return 'Previous number of nodes: ' + str(self.previous) + '\nCurrent number of nodes: ' + str(self.current) + '\nPercentage of nodes cleaned: ' + str(round((self.previous-self.current)/float(self.previous)*100, 2)) + '%'

class AlreadyCleanedDiagnostic(object):

    def __init__(self, current):
        self.current = current

    def __repr__(self):
        return 'Number of nodes: ' + str(self.current)

def clean(self):
    """
    """
    if not self._cleaned:
        previous = len(self)
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
        self._clean(cleanbuffer)
        self._cleaned = True
        return CleanedDiagnostic(previous, len(self))
    else:
        return AlreadyCleanedDiagnostic(len(self))

AbstractSemanticGraph.clean = clean
del clean

def mark_invalid_pointers(self):
    for fct in self.functions(free=False):
        if fct.result_type.nested.is_pointer:
            fct.traverse = False
        elif fct.result_type.is_pointer and isinstance(fct.result_type.target, FundamentalTypeProxy):
            fct.traverse = False
        elif any(parameter.type.nested.is_pointer or parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in fct.parameters):
            fct.traverse = False
    for cls in self.classes():
        for ctr in cls.constructors:
            if any(parameter.type.nested.is_pointer or parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in ctr.parameters):
                ctr.traverse = False

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
            if rtype.target.id == cls.id:
                self._nodes[fct.id].update(proxy=MethodProxy,
                        is_static=True,
                        is_virtual=False,
                        is_pure_virtual=False,
                        is_const=ptype.is_const,
                        as_constructor=True,
                        access='public')
                mv = True
            elif fct.nb_parameters > 0:
                ptype = fct.parameters[0].type
                if ptype.target.id == cls.id and (ptype.is_reference or ptype.is_pointer):
                    self._nodes[fct.id].update(proxy=MethodProxy,
                            is_static=False,
                            is_virtual=False,
                            is_pure_virtual=False,
                            is_const=ptype.is_const,
                            access='public')
                    mv = True
            if mv:
                self._syntax_edges[fct.parent.id].remove(fct.id)
                self._syntax_edges[cls.id].append(fct.id)

AbstractSemanticGraph.c_struct_to_class = c_struct_to_class
del c_struct_to_class
