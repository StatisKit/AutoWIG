"""
"""

import subprocess
from path import path

from .asg import *
from .tools import subclasses
from .plugin_manager import parser

__all__ = ['pre_processing', 'post_processing']

def pre_processing(asg, headers, flags, **kwargs):
    """Pre-processing step of an AutoWIG front-end

    During this step, files are added into the Abstract Semantic Graph (ASG) and a string corresponding to the content of a temporary header including all these files is returned.
    The attribute :attr:`is_primary` of nodes corresponding to these files is set to `True` (see :func:`autowig.controller.clean` for a detailed explanation of this operation).
    Nodes corresponding to the C++ global scope and C/C++ fundamental types (:class:`autowig.asg.FundamentalTypeProxy`) are also added to the ASG if not present.

    :Parameters:
     - `asg` (:class:'autowig.asg.AbstractSemanticGraph') - The ASG in which the files are added.
     - `headers` ([basestring|path]) - Paths to the source code. Note that a path can be relative or absolute.
     - `flags` ([basestring]) - Flags needed to perform the syntaxic analysis of source code.


    :Returns:
        A source code including all given source code paths.

    :Return Type:
        str

    .. note:: Determine the language of source code

        A temporary protected attribute `_language` is added to the ASG.
        This protected attribute is used to determine the language (C or C++) of header files during the processing step.
        This temporary attribute is deleted during the post-processing step.
        The usage of the `-x` option in flags is therefore mandatory.

    .. seealso::
        :class:`FrontEndFunctor` for a detailed documentation about AutoWIG front-end step.
        :func:`autowig.libclang_parser.parser` for an example.
    """
    for directory in asg.directories():
        del directory.is_searchpath

    cmd = ' '.join(flag.strip() for flag in flags)

    if '-x c++' in cmd:
        asg._language = 'c++'
        s = subprocess.Popen(['clang++', '-x', 'c++', '-v', '-E', '/dev/null'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif '-x c' in cmd:
        asg._language = 'c'
        s = subprocess.Popen(['clang', '-x', 'c', '-v', '-E', '/dev/null'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        raise ValueError('\'flags\' parameter must include the `-x` option with `c` or `c++`')
    if s.returncode:
        warnings.warn('System includes not computed: clang command failed', Warning)
    else:
        out, err = s.communicate()
        sysincludes = err.splitlines()
        if '#include <...> search starts here:' not in sysincludes or 'End of search list.' not in sysincludes:
            warnings.warn('System includes not computed: parsing clang command output failed', Warning)
        else:
            sysincludes = sysincludes[sysincludes.index('#include <...> search starts here:')+1:sysincludes.index('End of search list.')]
            #flags.extend(['-I'+str(path(sysinclude.strip()).abspath()) for sysinclude in sysincludes])
            for sysinclude in sysincludes:
                includedir = asg.add_directory(str(path(sysinclude.strip()).abspath()))
                includedir.is_searchpath = True

    if not '::' in asg._nodes:
        asg._nodes['::'] = dict(_proxy = NamespaceProxy)
    if not '::' in asg._syntax_edges:
        asg._syntax_edges['::'] = []

    for header in asg.files(header=True):
        del header.is_external_dependency

    for flag in flags:
        if flag.startswith('-I'):
            includedir = asg.add_directory(flag.strip('-I'))
            includedir.is_searchpath = True

    for fundamental in subclasses(FundamentalTypeProxy):
        if hasattr(fundamental, '_node'):
            if not fundamental._node in asg._nodes:
                asg._nodes[fundamental._node] = dict(_proxy = fundamental)
            if not fundamental._node in asg._syntax_edges['::']:
                asg._syntax_edges['::'].append(fundamental._node)

    headers = [path(header) if not isinstance(header, path) else header for header in headers]

    for header in headers:
        header = asg.add_file(header, proxy=HeaderProxy, _language=asg._language)
        header.is_self_contained = True
        header.is_external_dependency = False

    return "\n".join('#include "' + str(header.abspath()) + '"' for header in headers)

def post_processing(asg, flags, **kwargs):
    bootstrap(asg, flags, **kwargs)
    update_overload(asg, **kwargs)
    suppress_forward_declaration(asg, **kwargs)

def bootstrap(asg, flags, bootstrap=True, maximum=1000, **kwargs):
    if bootstrap:
        index = 0
        if isinstance(bootstrap, bool):
            bootstrap = float("Inf")
        nodes = 0
        forbidden = set()
        while not nodes == len(asg) and index < bootstrap:
            nodes = len(asg)
            white = []
            black = set()
            for node in asg.nodes():
                if not node.clean:
                    white.append(node)
                    black.add(node._node)
            gray = set()
            while len(white) > 0:
                node = white.pop()
                if isinstance(node, (TypedefProxy, VariableProxy)):
                    target = node.qualified_type.desugared_type.unqualified_type
                    if not target._node in black:
                        white.append(target)
                        black.add(target._node)
                elif isinstance(node, FunctionProxy):
                    return_type = node.return_type.desugared_type.unqualified_type
                    if not return_type._node in black:
                        white.append(return_type)
                        black.add(return_type._node)
                    for parameter in node.parameters:
                        target = parameter.qualified_type.desugared_type.unqualified_type
                        if not target._node in black:
                            white.append(target)
                            black.add(target._node)
                elif isinstance(node, ConstructorProxy):
                    for parameter in node.parameters:
                        target = parameter.qualified_type.desugared_type.unqualified_type
                        if not target._node in black:
                            white.append(target)
                            black.add(target._node)
                elif isinstance(node, ClassProxy):
                    for base in node.bases():
                        if base.access == 'public':
                            if not base._node in black:
                                white.append(base)
                                black.add(base._node)
                    for dcl in node.declarations():
                        try:
                            if dcl.access == 'public':
                                if not dcl._node in black:
                                    white.append(dcl)
                                    black.add(dcl._node)
                        except:
                            pass
                    if isinstance(node, ClassTemplateSpecializationProxy):
                        if not node.is_complete:
                            gray.add(node._node)
                        specialize = node.specialize
                        if not specialize._node in black:
                            white.append(node.specialize)
                            black.add(node.specialize._node)
                    elif not node.is_complete:
                        gray.add(node._node)
                elif isinstance(node, ClassTemplateProxy):
                    for specialization in node.specializations():
                        if not specialization._node in black:
                            white.append(specialization)
                            black.add(specialization._node)
            gray = list(gray)
            for gray in [gray[index:index+maximum] for index in xrange(0, len(gray), maximum)]:
                headers = []
                for header in asg.headers(*[asg[node] for node in gray]):
                    headers.append("#include \"" + header.globalname + "\"")
                headers.append("")
                headers.append("int main(void)")
                headers.append("{")
                for _index, spc in enumerate(gray):
                    if not spc in forbidden:
                        headers.append("\tsizeof(" + spc + ");")
                headers.append("\treturn 0;")
                headers.append("}")
                header = '\n'.join(headers)
                forbidden.update(set(gray))
                parser(asg, header, flags, booststrap=False, **kwargs)
            index += 1

def update_overload(asg, overload='none', **kwargs):
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

def suppress_forward_declaration(asg, **kwargs):
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
            for ctr in cls.constructors():
                if any(prm.qualified_type.unqualified_type._node in black for prm in ctr.parameters):
                    gray.add(ctr._node)
                    asg._parameter_edges.pop(ctr._node)
                    asg._nodes.pop(ctr._node)
            asg._base_edges[cls._node] = [dict(base = base['base'], _access = base['_access'], _is_virtual = base['_is_virtual']) for base in asg._base_edges[cls._node] if not base['base'] in black]
        else:
            enumerators = cls.enumerators()
            dtr = cls.destructor
            constructors = cls.constructors()
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

#def postprocessing(asg, headers, overload='all'):
#    """Post-processing step of an AutoWIG front-end
#
#    During this step, three distinct operations are executed:
#
#        * The **overloading** operation.
#          During this operation functions and methods of the Abstract Semantic Graph (ASG) are traversed in order to determine if they are overloaded or not.
#          This operation has at worst a time-complexity in :math:`\mathcal{O}\left(F^2\right)` where :math:`F` denotes the number of functions and methods in the ASG.
#          Therefore, its default behavior is altered and all functions and methods are considered as overloaded which induces a time-complexity of :math:`\mathcal{O}\left(N\right)` where :math:`N` denotes the number of nodes in the ASG.
#
#        * The **discarding** operation.
#
#        * The **templating** operation.
#
#    :Parameter:
#        `overload` (bool) - The boolean considered in order to determine if the behavior of the **overloading** operation is altered or not.
#
#    :Return Type:
#        `None`
#
#    .. seealso::
#        :func:`autowig.libclang_parser.parser` for an example.
#        :func:`compute_overloads`, :func:`discard_forward_declarations` and :func:`resolve_templates` for a more detailed documentatin about AutoWIG front-end post-processing step.
#    """
#    resolve_templates(asg)
#    compute_overloads(asg, overload=overload)
#    discard_forward_declarations(asg)
#
#
#
#def resolve_templates(asg):
#    for cls in asg.classes(templated=True, specialized=False):
#        if hasattr(cls, '_access'):
#            for spc in cls.specializations(partial=False):
#                asg._nodes[spc._node]['_access'] = cls._access
#    for cls in asg.classes(templated=None, specialized=True):
#        if hasattr(cls, '_access') and not hasattr(cls.specialize, '_access'):
#            asg._nodes[cls.specialize._node]['_access'] = cls._access
