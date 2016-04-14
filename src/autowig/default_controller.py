from .asg import *

__all__ = ['refactoring', 'cleaning']

def default_controller(asg, clean=True, operators=False, **kwargs):
    """Post-processing step of an AutoWIG front-end

    During this step, three distinct operations are executed:

        * The **overloading** operation.
          During this operation functions and methods of the Abstract Semantic Graph (ASG) are traversed in order to determine if they are overloaded or not.
          This operation has at worst a time-complexity in :math:`\mathcal{O}\left(F^2\right)` where :math:`F` denotes the number of functions and methods in the ASG.
          Therefore, its default behavior is altered and all functions and methods are considered as overloaded which induces a time-complexity of :math:`\mathcal{O}\left(N\right)` where :math:`N` denotes the number of nodes in the ASG.

        * The **discarding** operation.

        * The **templating** operation.

    :Parameter:
        `overload` (bool) - The boolean considered in order to determine if the behavior of the **overloading** operation is altered or not.

    :Return Type:
        `None`

    .. seealso::
        :func:`autowig.libclang_parser.parser` for an example.
        :func:`compute_overloads`, :func:`discard_forward_declarations` and :func:`resolve_templates` for a more detailed documentatin about AutoWIG front-end post-processing step.
    """
    asg = refactoring(asg)
    if clean:
        asg = cleaning(asg)
    return asg

def refactoring(asg):
    for function in asg.functions(free=True):
        if function.localname.startswith('operator'):
            parameter = function.parameters[0].qualified_type.desugared_type
            if parameter.is_class:
                function.parent = parameter.unqualified_type
    return asg

def cleaning(asg):
    """
    """
    cleanbuffer = [(node, node._clean) for node in asg.nodes() if hasattr(node, '_clean')]
    temp = []
    for node in asg.nodes():
        if node.clean:
            node.clean = True
        else:
            temp.append(node)

    while len(temp) > 0:
        node = temp.pop()
        node.clean = False
        parent = node.parent
        if not parent is None:
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
        if isinstance(node, HeaderProxy):
            include = node.include
            if not include is None:
                if include.clean:
                    temp.append(include)
                else:
                    include.clean = False
        elif isinstance(node, (TypedefProxy, VariableProxy)):
            target = node.qualified_type.unqualified_type
            if target.clean:
                temp.append(target)
            else:
                target.clean = False
        elif isinstance(node, EnumerationProxy):
            for enumerator in node.enumerators:
                if enumerator.clean:
                    temp.append(enumerator)
                else:
                    enumerator.clean = False
        elif isinstance(node, FunctionProxy):
            result_type = node.return_type.unqualified_type
            if result_type.clean:
                temp.append(result_type)
            else:
                result_type.clean = False
            for parameter in node.parameters:
                target = parameter.qualified_type.unqualified_type
                if target.clean:
                    temp.append(target)
                else:
                    target.clean = False
        elif isinstance(node, ConstructorProxy):
            for parameter in node.parameters:
                target = parameter.qualified_type.unqualified_type
                if target.clean:
                    temp.append(target)
                else:
                    target.clean = False
        elif isinstance(node, ClassProxy):
            for base in node.bases():
                if base.clean:
                    temp.append(base)
                else:
                    base.clean = False
            for dcl in node.declarations():
                if dcl.clean:
                    temp.append(dcl)
                else:
                    dcl.clean = False
            if isinstance(node, ClassTemplateSpecializationProxy):
                specialize = node.specialize
                if specialize.clean:
                    temp.append(node.specialize)
                else:
                    specialize.clean = False
                for template in node.templates:
                    target = template.desugared_type.unqualified_type
                    if target.clean:
                        temp.append(target)
                    else:
                        target.clean = False
        elif isinstance(node, ClassTemplateProxy):
            pass

    for tdf in asg.typedefs():
        if tdf.clean and not tdf.qualified_type.unqualified_type.clean and not tdf.parent.clean:
            tdf.clean = False
            include = tdf.header
            while not include is None:
                include.clean = False
                include = include.include

    nodes = [node for node in asg.nodes() if node.clean]
    for node in nodes:
        if not node._node in ['::', '/']:
            asg._syntax_edges[node.parent._node].remove(node._node)
            if isinstance(node, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
                asg._specialization_edges[node.specialize._node].remove(node._node)

    for node in nodes:
        asg._nodes.pop(node._node)
        asg._include_edges.pop(node._node, None)
        asg._syntax_edges.pop(node._node, None)
        asg._base_edges.pop(node._node, None)
        asg._type_edges.pop(node._node, None)
        asg._parameter_edges.pop(node._node, None)
        asg._specialization_edges.pop(node._node, None)

    nodes = set([node._node for node in nodes])
    for node in asg.nodes():
        if isinstance(node, ClassProxy):
            asg._base_edges[node._node] = [base for base in asg._base_edges[node._node] if not base['base'] in nodes]
        del node.clean

    for node, clean in cleanbuffer:
        if node._node in asg:
            node.clean = clean

    return asg
