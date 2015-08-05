from openalea.core.plugin.functor import PluginFunctor
from openalea.core.util import camel_case_to_lower, to_camel_case, camel_case_to_upper

from .tools import remove_templates

__all__ = ['node_rename']

node_rename = PluginFunctor.factory('autowig', implements='name')
#node_rename.__class__.__doc__ = """Node python name functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""

PYTHON_OPERATOR = dict()
PYTHON_OPERATOR['+'] = '__add__'
PYTHON_OPERATOR['-'] = '__sub__'
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

CONST_PYTHON_OPERATOR = dict()
CONST_PYTHON_OPERATOR['[]'] = '__getitem__'

NON_CONST_PYTHON_OPERATOR = dict()
NON_CONST_PYTHON_OPERATOR['[]'] = '__setitem__'

class PEP8NodeNamePlugin(object):
    """PEP8 plugin for the python name computation of a node"""

    implements = 'name'


    def implementation(self, node, scope=False):
        from vplants.autowig.asg import VariableProxy, FunctionProxy, MethodProxy, ClassProxy, ClassTemplateSpecializationProxy, TypedefProxy, EnumProxy, EnumConstantProxy, NamespaceProxy
        if isinstance(node, MethodProxy) and node.localname.startswith('operator'):
            operator = node.localname.strip('operator').strip()
            if operator in PYTHON_OPERATOR:
                return PYTHON_OPERATOR[operator]
            else:
                if node.is_const:
                    return CONST_PYTHON_OPERATOR[operator]
                else:
                    return NON_CONST_PYTHON_OPERATOR[operator]
        elif isinstance(node, FunctionProxy):
            return camel_case_to_lower(node.localname)
        elif isinstance(node, EnumProxy):
            return camel_case_to_lower(node.localname)
        elif isinstance(node, VariableProxy):
            if node.type.is_const:
                return camel_case_to_upper(node.localname)
            else:
                return camel_case_to_lower(node.localname)
        elif isinstance(node, EnumConstantProxy):
            return camel_case_to_upper(node.localname)
        elif isinstance(node, ClassTemplateSpecializationProxy):
            return '_' + to_camel_case(remove_templates(node.localname)).strip('_') + '_' + node.hash
        elif isinstance(node, TypedefProxy):
            return to_camel_case(node.localname)
        elif isinstance(node, ClassProxy):
            if scope:
                return '_' + camel_case_to_lower(node.localname).strip('_')
            else:
                return to_camel_case(node.localname)
        elif isinstance(node, NamespaceProxy):
                return camel_case_to_lower(node.localname)
        else:
            return NotImplementedError(node.__class__)

node_rename['PEP8'] = PEP8NodeNamePlugin
node_rename.plugin = 'PEP8'
