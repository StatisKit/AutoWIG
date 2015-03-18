from ..tools import indent
from ..cpp.interface import InterfaceTypedefType, TypeRefHeaderInterface, InterfaceLValueReferenceType, InterfacePointerType, FunctionHeaderInterface

def special_functions(funcname):
    if funcname == "operator()":
        return "__call__"
    else:
        return funcname

def write_thin(scope, string, level=0, tabsize=4):
    if len(string) == 0 or string.isspace():
        return ""
    else:
        result = ""
        _level = level
        if level == 0:
            result += "namespace autowig\n{\n"
            _level += 1
        for scope in [scope for scope in scope.split('::') if not scope == ""]:
            result += " "*tabsize*_level+"namespace "+scope+"\n"+" "*tabsize*_level+"{\n"
            _level += 1
        result += indent(string, level=_level)
        while not _level == level:
            _level -= 1
            result += "\n"+" "*tabsize*_level+"}"
        return result+"\n\n"

def write_deep(string):
    if len(string) == 0 or string.isspace():
        return "{}\n\n"
    else:
        lines = string.splitlines()
        if len(lines) == 1:
            return "{ "+lines[0]+" }"
        else:
            return "{\n    "+"\n    ".join(lines)+"\n}\n";

def return_value_policy(function):
    if not isinstance(function, FunctionHeaderInterface):
        raise TypeError('`function` parameter')
    if hasattr(function, 'return_value_policy'):
        return function.return_value_policy
    else:
        output = function.output
        if isinstance(output, (InterfaceTypedefType, TypeRefHeaderInterface)):
            output = output.type
        if isinstance(output, InterfaceLValueReferenceType):
            if output.type.const:
                return 'boost::python::copy_const_reference'
            else:
                return 'boost::python::copy_non_const_reference'
        elif isinstance(output, InterfacePointerType):
            return 'boost::python::manage_new_object'
        else:
            return None
