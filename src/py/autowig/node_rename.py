from .tools import camel_case_to_lower, to_camel_case, camel_case_to_upper
from .asg import (FunctionProxy,
                  VariableProxy,
                  EnumeratorProxy,
                  ClassTemplateSpecializationProxy,
                  ClassTemplateProxy,
                  ClassProxy,
                  NamespaceProxy)

__all__ = []

PYTHON_OPERATOR = dict()
PYTHON_OPERATOR['+'] = '__add__'
PYTHON_OPERATOR['++'] = '__next__'
PYTHON_OPERATOR['-'] = '__sub__'
PYTHON_OPERATOR['--'] = '__prev__'
PYTHON_OPERATOR['*'] = '__mul__'
PYTHON_OPERATOR['/'] = '__div__'
PYTHON_OPERATOR['%'] = '__mod__'
PYTHON_OPERATOR['=='] = '__eq__'
PYTHON_OPERATOR['!='] = '__neq__'
PYTHON_OPERATOR['>'] = '__gt__'
PYTHON_OPERATOR['<'] = '__lt__'
PYTHON_OPERATOR['>='] = '__ge__'
PYTHON_OPERATOR['<='] = '__le__'
PYTHON_OPERATOR['!'] = '__not__'
PYTHON_OPERATOR['&&'] = '__and__'
PYTHON_OPERATOR['||'] = '__or__'
PYTHON_OPERATOR['~'] = '__invert__'
PYTHON_OPERATOR['&'] = '__and__'
PYTHON_OPERATOR['|'] = '__or__'
PYTHON_OPERATOR['^'] = '__xor__'
PYTHON_OPERATOR['<<'] = '__lshift__'
PYTHON_OPERATOR['>>'] = '__rshift__'
PYTHON_OPERATOR['+='] = '__iadd__'
PYTHON_OPERATOR['-='] = '__isub__'
PYTHON_OPERATOR['*='] = '__imul__'
PYTHON_OPERATOR['%='] = '__idiv__'
PYTHON_OPERATOR['&='] = '__iand__'
PYTHON_OPERATOR['|='] = '__ior__'
PYTHON_OPERATOR['^='] = '__ixor__'
PYTHON_OPERATOR['<<='] = '__ilshift__'
PYTHON_OPERATOR['>>='] = '__irshift__'
PYTHON_OPERATOR['()'] = '__call__'
PYTHON_OPERATOR['[]'] = '__getitem__'

def pep8_node_rename(node, scope=False):
    if isinstance(node, FunctionProxy) and node.localname.startswith('operator'):
        return PYTHON_OPERATOR[node.localname.strip('operator').strip()]
    elif isinstance(node, FunctionProxy):
        return camel_case_to_lower(node.localname)
    elif isinstance(node, FunctionProxy):
        return camel_case_to_lower(node.localname)
    elif isinstance(node, VariableProxy):
        #if node.type.is_const:
        #    return camel_case_to_upper(node.localname)
        #else:
        return camel_case_to_lower(node.localname)
    elif isinstance(node, EnumeratorProxy):
        return camel_case_to_upper(node.localname)
    elif isinstance(node, ClassTemplateSpecializationProxy):
        if not scope:
            return '_' + to_camel_case(node.specialize.localname).strip('_') + '_' + node.hash
        else:
            return '__' + camel_case_to_lower(node.specialize.localname).strip('_') + '_' + node.hash
    elif isinstance(node, TypedefProxy):
        return to_camel_case(node.localname)
    elif isinstance(node, (ClassTemplateProxy, ClassProxy)):
        if scope:
            return '_' + camel_case_to_lower(node.localname).strip('_')
        elif isinstance(node, ClassProxy):
            return to_camel_case(node.localname)
        else:
            return '_' + to_camel_case(node.localname)
    elif isinstance(node, NamespaceProxy):
        return camel_case_to_lower(node.localname)
    else:
        return NotImplementedError(node.__class__)
