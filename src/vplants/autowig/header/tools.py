from vplants.autowig.interface import AccessSpecifier, InterfaceCursor, UsingInterfaceCursor, TypedefInterfaceCursor, EnumInterfaceCursor, FunctionInterfaceCursor, ConstructorInterfaceCursor, BaseClassInterfaceCursor, UserDefinedTypeInterfaceCursor, TemplateClassInterfaceCursor, ScopeInterfaceCursor
import re, itertools

def namespaces(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            if spelling in results:
                results[spelling].apppend(interface)
            else:
                results[spelling] = [interface]
            results.update(namespaces(spelling, *interface.declarations))
    return results

def aliases(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results.update(aliases(spelling, *interface.declarations))
        elif isinstance(interface, UserDefinedInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results.update(aliases(spelling, *interface.aliases))
    return results

def enums(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+inface.spelling, interface.declarations))
        elif isinstance(interface, UserDefinedTypeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+interface.spelling, *[enum for enum in interface.enums if enum.access is AccessSpecifier.PUBLIC]))
        elif isinstance(interface, EnumsInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results[spelling] = interface
    return results

def variables(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results.update(functions(spelling, *interface.declarations))
        elif isinstance(interface, VariableInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results[spelling] = interface
    return results

def functions(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results.update(functions(spelling, *interface.declarations))
        elif isinstance(interface, FunctionInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            if not spelling in results:
                results[spelling] = [interface]
            else:
                results[spelling].append(interface)
    return results

def user_defined_types(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results.update(user_defined_types(spelling, *interface.declarations))
        elif isinstance(interface, UserDefinedTypeInterfaceCursor) and not 'hidden' in interface.annotations and not interface.empty:
            spelling = scope+interface.spelling
            results[spelling] = interface
            results.update(user_defined_types(spelling, *[udt for udt in interface.user_defined_types if udt.access is AccessSpecifier.PUBLIC]))
    return results

def fields(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+inface.spelling, interface.declarations))
        elif isinstance(interface, UserDefinedTypeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+interface.spelling, *[field for field in interface.fields if field.access is AccessSpecifier.PUBLIC]))
        elif isinstance(interface, FieldInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            results[spelling] = interface
    return results

def constructors(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+inface.spelling, interface.declarations))
        elif isinstance(interface, UserDefinedTypeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+interface.spelling, *[method for method in interface.methods if method.access is AccessSepcifier.PUBLIC]))
        elif isinstance(interface, ConstructorInterfaceCursor) and not 'hidden' in interface.annotations:
            if not scope in results:
                results[scope] = [interface]
            else:
                results[scope].append(interface)
    return results

def methods(scope, *interfaces):
    """
    """
    if not scope == "":
        scope += "::"
    results = dict()
    for interface in interfaces:
        if isinstance(interface, ScopeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+inface.spelling, interface.declarations))
        elif isinstance(interface, UserDefinedTypeInterfaceCursor) and not 'hidden' in interface.annotations:
            results.update(methods(scope+interface.spelling, *[method for method in interface.methods if method.access is AccessSepcifier.PUBLIC]))
        elif isinstance(interface, MethodInterfaceCursor) and not 'hidden' in interface.annotations:
            spelling = scope+interface.spelling
            if not spelling in results:
                results[spelling] = [interface]
            else:
                results[spelling].append(interface)
    return results

def stl_containers(*interfaces):
    """
    """
    templates = dict(vectortemplates = set(), settemplates = set(), maptemplates = set(), includefiles = set())
    for interface in interfaces:
        if isinstance(interface, InterfaceCursor) and not 'hidden' in interface.annotations:
            if isinstance(interface, ScopeInterfaceCursor):
                for i, j in stl_containers(*interface.declarations).items():
                    templates[i].update(j)
            if isinstance(interface, UserDefinedTypeInterfaceCursor):
                for i, j in stl_containers(*list(itertools.chain(interface.bases, interface.typedefs, interface.constructors, interface.methods, interface.user_defined_types))).items():
                    templates[i].update(j)
            elif isinstance(interface, BaseClassInterfaceCursor):
                if re.match('std::vector< (.*) >', interface.spelling):
                    templates['vectortemplates'].add(re.split('std::vector< (.*) >', interface.spelling)[1])
                    templates['includefiles'].add(interface.file)
                elif re.match('std::set< (.*) >', interface.spelling):
                    templates['settemplates'].add(re.split('std::set< (.*) >', interface.spelling)[1])
                    templates['includefiles'].add(interface.file)
                elif re.match('std::map< (.*), (.*) >', interface.spelling):
                    templates['maptemplates'].add(tuple(re.split('std::map< (.*), (.*) >', interface.spelling)[1:-1]))
                    templates['includefiles'].add(interface.file)
            elif isinstance(interface, FunctionInterfaceCursor):
                if re.match('std::vector<(.*)>', interface.output.spelling):
                    templates['vectortemplates'].add(re.split('std::vector<(.*)>', interface.output.spelling)[1])
                    templates['includefiles'].add(interface.file)
                elif re.match('std::set< (.*) >', interface.output.spelling):
                    templates['settemplates'].add(re.split('std::set< (.*) >', interface.output.spelling)[1])
                    templates['includefiles'].add(interface.file)
                elif re.match('std::map< (.*), (.*) >', interface.output.spelling):
                    templates['maptemplates'].add(tuple(re.split('std::map< (.*), (.*) >', interface.output.spelling)[1:-1]))
                    templates['includefiles'].add(interface.file)
                for input in interface.inputs:
                    if re.match('std::vector<(.*)>', input.type.spelling):
                        templates['vectortemplates'].add(re.split('std::vector<(.*)>', input.type.spelling)[1])
                        templates['includefiles'].add(interface.file)
                    elif re.match('std::set< (.*) >', input.type.spelling):
                        templates['settemplates'].add(re.split('std::set< (.*) >', input.type.spelling)[1])
                        templates['includefiles'].add(interface.file)
                    elif re.match('std::map< (.*), (.*) >', input.type.spelling):
                        templates['maptemplates'].add(tuple(re.split('std::map< (.*), (.*) >', input.type.spelling)[1:-1]))
                        templates['includefiles'].add(interface.file)
            elif isinstance(interface, ConstructorInterfaceCursor):
                for input in interface.inputs:
                    if re.match('std::vector<(.*)>', input.type.spelling):
                        templates['vectortemplates'].add(re.split('std::vector<(.*)>', input.type.spelling)[1])
                        templates['includefiles'].add(interface.file)
                    elif re.match('std::set< (.*) >', input.type.spelling):
                        templates['settemplates'].add(re.split('std::set< (.*) >', input.type.spelling)[1])
                        templates['includefiles'].add(interface.file)
                    elif re.match('std::map< (.*), (.*) >', input.type.spelling):
                        templates['maptemplates'].add(tuple(re.split('std::map< (.*), (.*) >', input.type.spelling)[1:-1]))
                        templates['includefiles'].add(interface.file)
            elif isinstance(interface, UsingInterfaceCursor):
                if re.match('std::vector<(.*)>', interface.type.spelling):
                    templates['vectortemplates'].add(re.split('std::vector<(.*)>', interface.type.spelling)[1])
                    templates['includefiles'].add(interface.file)
                elif re.match('std::set< (.*) >', interface.type.spelling):
                    templates['settemplates'].add(re.split('std::set< (.*) >', interface.type.spelling)[1])
                    templates['includefiles'].add(interface.file)
                elif re.match('std::map< (.*), (.*) >', interface.type.spelling):
                    templates['maptemplates'].add(tuple(re.split('std::map< (.*), (.*) >', interface.type.spelling)[1:-1]))
                    templates['includefiles'].add(interface.file)
            elif isinstance(interface, TypedefInterfaceCursor):
                if re.match('std::vector<(.*)>', interface.type.spelling):
                    templates['vectortemplates'].add(re.split('std::vector<(.*)>', interface.type.spelling[1]))
                    templates['includefiles'].add(interface.file)
                elif re.match('std::set< (.*) >', interface.type.spelling):
                    templates['settemplates'].add(re.split('std::set< (.*) >', interface.type.spelling[1]))
                    templates['includefiles'].add(interface.file)
                elif re.match('std::map< (.*), (.*) >', interface.type.spelling):
                    templates['maptemplates'].add(tuple(re.split('std::map< (.*), (.*) >', interface.type.spelling)[1:-1]))
                    templates['includefiles'].add(interface.file)
    return templates

def hide(*interfaces):
    """
    """
    for interface in interfaces:
        interface.annotations.append('hidden')
