from .plugin import PluginManager

from .asg import (HeaderProxy,
                  TypedefProxy,
                  EnumerationProxy,
                  FunctionProxy,
                  ConstructorProxy,
                  ClassProxy,
                  ClassTemplateSpecializationProxy,
                  ClassTemplateProxy,
                  VariableProxy,
                  ClassTemplatePartialSpecializationProxy)
 
controller = PluginManager('autowig.controller', brief="AutoWIG middle-end plugin_managers",
        details="""AutoWIG middle-end plugin_managers are responsible for Abstract Semantic Graph (ASG) modification from Python semantic queries.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")
                 
def refactoring(asg):
    for function in asg.functions(free=True):
        if len(function.parameters) > 1:
            if function.localname == 'operator<<':
                parameters = [parameter.qualified_type.desugared_type for parameter in function.parameters]
                if len(parameters) == 2 and parameters[0].unqualified_type.globalname == 'class ::std::basic_ostream< char, struct ::std::char_traits< char > >' and parameters[1].is_class:
                    function.parent = parameters[1].unqualified_type
                else:
                    parameter = function.parameters[0].qualified_type.desugared_type
                    if parameter.is_class:
                        function.parent = parameter.unqualified_type
            elif function.localname.startswith('operator'):
                parameter = function.parameters[0].qualified_type.desugared_type
                if parameter.is_class:
                    function.parent = parameter.unqualified_type
    return asg

def cleaning(asg):
    """
    """
    temp = []
    for node in asg.nodes():
        if node.clean:
            node.clean = True
        else:
            temp.append(node._node)

    while len(temp) > 0:
        node = asg[temp.pop()]
        node.clean = False
        parent = node.parent
        if parent is not None:
            if parent.clean:
                temp.append(parent._node)
            else:
                parent.clean = False
        if hasattr(node, 'header'):
            header = node.header
            if header is not None:
                if header.clean:
                    temp.append(header._node)
                else:
                    header.clean = False
        if isinstance(node, HeaderProxy):
            include = node.include
            if include is not None:
                if include.clean:
                    temp.append(include._node)
                else:
                    include.clean = False
        elif isinstance(node, (TypedefProxy, VariableProxy)):
            target = node.qualified_type.unqualified_type
            if target.clean:
                temp.append(target._node)
            else:
                target.clean = False
        elif isinstance(node, EnumerationProxy):
            for enumerator in node.enumerators:
                if enumerator.clean:
                    temp.append(enumerator._node)
                else:
                    enumerator.clean = False
        elif isinstance(node, FunctionProxy):
            result_type = node.return_type.unqualified_type
            if result_type.clean:
                temp.append(result_type._node)
            else:
                result_type.clean = False
            for parameter in node.parameters:
                target = parameter.qualified_type.unqualified_type
                if target.clean:
                    temp.append(target._node)
                else:
                    target.clean = False
        elif isinstance(node, ConstructorProxy):
            for parameter in node.parameters:
                target = parameter.qualified_type.unqualified_type
                if target.clean:
                    temp.append(target._node)
                else:
                    target.clean = False
        elif isinstance(node, ClassProxy):
            for base in node.bases():
                if base.clean:
                    temp.append(base._node)
                else:
                    base.clean = False
            for dcl in node.declarations():
                if dcl.clean:
                    temp.append(dcl._node)
                else:
                    dcl.clean = False
            if isinstance(node, ClassTemplateSpecializationProxy):
                specialize = node.specialize
                if specialize.clean:
                    temp.append(node.specialize._node)
                else:
                    specialize.clean = False
                for template in node.templates:
                    target = template.desugared_type.unqualified_type
                    if target.clean:
                        temp.append(target._node)
                    else:
                        target.clean = False
        elif isinstance(node, ClassTemplateProxy):
            pass
    nodes = sorted([node for node in asg.nodes() if node.clean], key=lambda node: -len(node.ancestors))
    for node in nodes:
        if node._node not in ['::', '/']:
            asg._syntax_edges[node.parent._node].remove(node._node)
            if isinstance(node, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
                asg._specialization_edges[node.specialize._node].remove(node._node)

    nodes = set([node._node for node in nodes])

    for node in nodes:
        asg._nodes.pop(node)
        asg._include_edges.pop(node, None)
        asg._syntax_edges.pop(node, None)
        asg._base_edges.pop(node, None)
        asg._type_edges.pop(node, None)
        asg._parameter_edges.pop(node, None)
        asg._specialization_edges.pop(node, None)

    for node in asg.nodes():
        if isinstance(node, ClassProxy):
            asg._base_edges[node._node] = [base for base in asg._base_edges[node._node] if not base['base'] in nodes]

    return asg
