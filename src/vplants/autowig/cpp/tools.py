from vplants.autowig.interface import AliasInterfaceCursor, InterfaceTypedefType, InterfaceLValueReferenceType, InterfacePointerType, FunctionInterfaceCursor, ConstructorInterfaceCursor, UserDefinedTypeInterfaceCursor, ScopeInterfaceCursor, InterfaceType
import re, itertools

def extract_templates(spelling):
    """
    """
    if re.match("std::vector< (.*) >", spelling):
        return "vector", re.split("std::vector< (.*) >", spelling)[1].split(", ")
    elif re.match("std::set< (.*) >", spelling):
        return "set", re.split("std::set< (.*) >", spelling)[1].split(", ")
    elif re.match("std::map< (.*) >", spelling):
        return "map", re.split("std::map< (.*) >", spelling)[1].split(", ")
    else:
        raise ValueError('`spelling` parameter')

def extract_containers(*interfaces):
    """
    """
    templates = dict(vector = set(), set = set(), map = set(), includes = set())
    for interface in interfaces:
        if isinstance(interface, InterfaceType):
            try:
                key, value = extract_templates(spelling)
                templates[key].add(value)
            except:
                pass
        else:
            if isinstance(interface, (ScopeInterfaceCursor, UserDefinedTypeInterfaceCursor)):
                nestedinterfaces = interface.declarations
            elif isinstance(interface, ConstructorInterfaceCursor):
                nestedinterfaces = interface.inputs
            elif isinstance(interface, FunctionInterfaceCursor):
                nestedinterfaces = itertools.chain([interface.output], interface.inputs)
            elif isinstance(interface, (AliasInterfaceCursor, InterfaceTypedefType, InterfaceLValueReferenceType, InterfacePointerType)):
                nestedinterfaces = [interface.type]
            for i, j in stl_containers(*nestedinterfaces).iteritems():
                templates[i].update(j)
            templates['includes'].add(interface.file)
    return templates
