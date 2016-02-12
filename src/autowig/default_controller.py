from .asg import *

__all__ = ['resolve_overload', 'suppress_forward_declarations']

def default_controller(asg, clean=True, **kwargs):
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
    resolve_overload(asg)
    suppress_forward_declarations(asg)
    if clean:
        asg.clean()

def resolve_overload(asg, overload='all'):
    """
    """
    if isinstance(overload, bool):
        if overload:
            overload = 'all'
        else:
            overload = 'none'
    if not isinstance(overload, basestring):
        raise TypeError('\'overload\' parameter')
    if overload == 'all':
        free = None
    elif overload == 'namespace':
        free = True
    elif overload == 'class':
        free = False
    elif not overload == 'none':
        raise ValueError('\'overload\' parameter')
    if overload == 'none':
        for fct in asg.functions(free=None):
            fct.is_overloaded = True
    else:
        for fct in asg.functions(free=free):
            if not fct.is_overloaded:
                overloads = fct.overloads
                if len(overloads) > 1:
                    for overload in overloads:
                        overload.is_overloaded = True

def suppress_forward_declarations(asg):
    """
    """
    black = set()
    def blacklist(cls, black):
        black.add(cls._node)
        if isinstance(cls, ClassProxy):
            for enm in cls.enumerations():
                black.add(enm._node)
            for cls in cls.classes():
                blacklist(cls, black)
    for cls in asg.classes(templated=False):
        if not cls._node in black and not cls._node.startswith('union '):
            if cls.is_complete:
                complete = cls
                if cls._node.startswith('class '):
                    try:
                        duplicate = asg[cls._node.replace('class ', 'struct ', 1)]
                    except:
                        duplicate = None
                elif cls._node.startswith('struct '):
                    try:
                        duplicate = asg[cls._node.replace('struct ', 'class ', 1)]
                    except:
                        duplicate = None
                else:
                    duplicate = None
            else:
                duplicate = cls
                if cls._node.startswith('class '):
                    try:
                        complete = asg[cls._node.replace('class ', 'struct ', 1)]
                    except:
                        complete = None
                elif cls._node.startswith('struct '):
                    try:
                        complete = asg[cls._node.replace('struct ', 'class ', 1)]
                    except:
                        complete = None
                else:
                    complete = None
            if not duplicate is None:
                if isinstance(duplicate, ClassTemplateProxy) and not complete is None:
                    blacklist(complete, black)
                elif isinstance(complete, ClassTemplateProxy):
                    blacklist(duplicate, black)
                elif complete is None or not complete.is_complete or duplicate.is_complete:
                    blacklist(duplicate, black)
                    if not complete is None:
                        blacklist(complete, black)
                else:
                    complete = complete._node
                    duplicate = duplicate._node
                    for node, edge in asg._type_edges.iteritems():
                        if edge['target'] == duplicate:
                            edge['target'] = complete
                    for node, edges in asg._base_edges.iteritems():
                        for index, edge in enumerate(edges):
                            if edge['base'] == duplicate:
                                edges[index]['base'] = complete
                    for node, edges in asg._template_edges.iteritems():
                        for index, edge in enumerate(edges):
                            if edge['target'] == duplicate:
                                edges[index]['target'] = complete
                    if 'access' in asg._nodes[duplicate]:
                        asg._nodes[complete]['access'] = asg._nodes[duplicate]['access']
                    black.add(duplicate)
    change = True
    nb = 0
    while change:
        change = False
        for cls in asg.classes(specialized=True, templated=False):
            # TODO templated=None
            if not cls._node in black:
                templates = [tpl.unqualified_type for tpl in cls.templates]
                while not(len(templates) == 0 or any(tpl._node in black for tpl in templates)):
                    _templates = templates
                    templates = []
                    for _tpl in _templates:
                        if isinstance(_tpl, ClassTemplateSpecializationProxy):
                            templates.extend([tpl.unqualified_type for tpl in _tpl.templates])
                if not len(templates) == 0:
                    change = True
                    blacklist(cls, black)
        nb += 1
    gray = set(black)
    for tdf in asg.typedefs():
        if tdf.qualified_type.unqualified_type._node in black:
            gray.add(tdf._node)
            asg._type_edges.pop(tdf._node)
            asg._nodes.pop(tdf._node)
    for var in asg.variables():
        if var.qualified_type.unqualified_type._node in black:
            gray.add(var._node)
            asg._type_edges.pop(var._node)
            asg._nodes.pop(var._node)
    for fct in asg.functions():
        if fct.return_type.unqualified_type._node in black or any(prm.qualified_type.unqualified_type._node in black for prm in fct.parameters):
            gray.add(fct._node)
            asg._parameter_edges.pop(fct._node)
            asg._type_edges.pop(fct._node)
            asg._nodes.pop(fct._node)
    for parent, children in asg._syntax_edges.items():
        asg._syntax_edges[parent] = [child for child in children if not child in gray]
    gray = set()
    for cls in asg.classes(templated=False):
        if not cls._node in black:
            for ctr in cls.constructors:
                if any(prm.qualified_type.unqualified_type._node in black for prm in ctr.parameters):
                    gray.add(ctr._node)
                    asg._parameter_edges.pop(ctr._node)
                    asg._nodes.pop(ctr._node)
            asg._base_edges[cls._node] = [dict(base = base['base'], _access = base['_access'], _is_virtual = base['_is_virtual']) for base in asg._base_edges[cls._node] if not base['base'] in black]
        else:
            enumerators = cls.enumerators()
            dtr = cls.destructor
            constructors = cls.constructors
            typedefs = cls.typedefs()
            fields = cls.fields()
            methods = cls.methods()
            for enm in enumerators:
                gray.add(enm._node)
                asg._nodes.pop(enm._node)
            if not dtr is None:
                asg._nodes.pop(dtr._node)
            for ctr in constructors:
                gray.add(ctr._node)
                asg._parameter_edges.pop(ctr._node)
                asg._nodes.pop(ctr._node)
            for tdf in typedefs:
                gray.add(tdf._node)
                asg._type_edges.pop(tdf._node)
                asg._nodes.pop(tdf._node)
            for fld in fields:
                gray.add(fld._node)
                asg._type_edges.pop(fld._node)
                asg._nodes.pop(fld._node)
            for mtd in methods:
                gray.add(mtd._node)
                asg._parameter_edges.pop(mtd._node)
                asg._type_edges.pop(mtd._node)
                asg._nodes.pop(mtd._node)
    for parent, children in asg._syntax_edges.items():
        asg._syntax_edges[parent] = [child for child in children if not child in gray]
    for cls in asg.classes(templated=True, specialized=False):
        asg._specialization_edges[cls._node] = [spec for spec in asg._specialization_edges[cls._node] if not spec in black]
    for cls in black:
        asg._nodes.pop(cls)
        asg._syntax_edges.pop(cls, None)
        asg._base_edges.pop(cls, None)
        asg._template_edges.pop(cls, None)
        asg._specialization_edges.pop(cls, None)
