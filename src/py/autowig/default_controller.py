from .asg import AbstractSemanticGraph, \
                 HeaderProxy, \
                 TypedefProxy, \
                 EnumerationProxy, \
                 FunctionProxy, \
                 ConstructorProxy, \
                 ClassProxy, \
                 ClassTemplateSpecializationProxy, \
                 ClassTemplateProxy, \
                 VariableProxy, \
                 ClassTemplatePartialSpecializationProxy

__all__ = ['refactoring', 'cleaning']

def default_controller(asg, **kwargs):
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
    if 'env' in kwargs:
        env = kwargs.pop('env')
        if 'autowig_controller_clean' in env and 'clean' not in kwargs:
            kwargs['clean'] = env['autowig_controller_clean']
        if 'autowig_controller_refactoring' in env and 'refactoring' not in kwargs:
            kwargs['refactoring'] = env['autowig_controller_refactoring']
    if kwargs.pop('refactoring', True):
        asg = refactoring(asg)
    if kwargs.pop('clean', True):
        asg = cleaning(asg)
    return asg

def refactoring(asg):
    for function in asg.functions(free=True):
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
    from boost_python_generator import BoostPythonExportFileProxy

    if 'class ::std::fpos< __mbstate_t >' in asg and not isinstance(asg['class ::std::fpos< __mbstate_t >'].boost_python_export, (bool, BoostPythonExportFileProxy)):
        import ipdb
        ipdb.set_trace()

    if '/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp' in asg and asg['/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp'].clean:
        import ipdb
        ipdb.set_trace()

    temp = []
    for node in asg.nodes():
        if node.clean:
            node.clean = True
        else:
            temp.append(node._node)

    if 'class ::std::fpos< __mbstate_t >' in asg and not isinstance(asg['class ::std::fpos< __mbstate_t >'].boost_python_export, (bool, BoostPythonExportFileProxy)):
        import ipdb
        ipdb.set_trace()

    if '/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp' in asg and asg['/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp'].clean:
        import ipdb
        ipdb.set_trace()

    while len(temp) > 0:
        node = asg[temp.pop()]
        node.clean = False
        parent = node.parent
        if not parent is None:
            if parent.clean:
                temp.append(parent._node)
            else:
                parent.clean = False
        if hasattr(node, 'header'):
            header = node.header
            if not header is None:
                if header.clean:
                    temp.append(header._node)
                else:
                    header.clean = False
        if isinstance(node, HeaderProxy):
            include = node.include
            if not include is None:
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

    if 'class ::std::fpos< __mbstate_t >' in asg and not isinstance(asg['class ::std::fpos< __mbstate_t >'].boost_python_export, (bool, BoostPythonExportFileProxy)):
        import ipdb
        ipdb.set_trace()

    if '/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp' in asg and asg['/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp'].clean:
        import ipdb
        ipdb.set_trace()

    nodes = [node for node in asg.nodes() if node.clean]
    for node in nodes:
        if not node._node in ['::', '/']:
            asg._syntax_edges[node.parent._node].remove(node._node)
            if isinstance(node, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
                asg._specialization_edges[node.specialize._node].remove(node._node)

    if 'class ::std::fpos< __mbstate_t >' in asg and not isinstance(asg['class ::std::fpos< __mbstate_t >'].boost_python_export, (bool, BoostPythonExportFileProxy)):
        import ipdb
        ipdb.set_trace()

    if '/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp' in asg and asg['/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp'].clean:
        import ipdb
        ipdb.set_trace()

    nodes = set([node._node for node in nodes])

    for node in nodes:
        asg._nodes.pop(node)
        asg._include_edges.pop(node, None)
        asg._syntax_edges.pop(node, None)
        asg._base_edges.pop(node, None)
        asg._type_edges.pop(node, None)
        asg._parameter_edges.pop(node, None)
        asg._specialization_edges.pop(node, None)

    if 'class ::std::fpos< __mbstate_t >' in asg and not isinstance(asg['class ::std::fpos< __mbstate_t >'].boost_python_export, (bool, BoostPythonExportFileProxy)):
        import ipdb
        ipdb.set_trace()

    if '/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp' in asg and asg['/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp'].clean:
        import ipdb
        ipdb.set_trace()

    for node in asg.nodes():
        if isinstance(node, ClassProxy):
            asg._base_edges[node._node] = [base for base in asg._base_edges[node._node] if not base['base'] in nodes]

    if 'class ::std::fpos< __mbstate_t >' in asg and not isinstance(asg['class ::std::fpos< __mbstate_t >'].boost_python_export, (bool, BoostPythonExportFileProxy)):
        import ipdb
        ipdb.set_trace()

    if '/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp' in asg and asg['/home/pfernique/Desktop/StructureAnalysis/stat_tool/src/wrapper/wrapper_c62bcafb31b250e8bb3f63626536f4b4.cpp'].clean:
        import ipdb
        ipdb.set_trace()

    return asg
