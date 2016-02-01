"""
"""

import time
from openalea.core.plugin.functor import PluginFunctor
import pickle
import subprocess
from path import path

from autowig.ast import *
from autowig.asg import *
from autowig.tools import subclasses

__all__ = ['front_end']

def preprocessing(asg, headers, flags):
    """Pre-processing step of an AutoWIG front-end

    During this step, files are added into the Abstract Semantic Graph (ASG) and a string corresponding to the content of a temporary header including all these files is returned.
    The attribute :attr:`is_primary` of nodes corresponding to these files is set to `True` (see :func:`autowig.middle_end.clean` for a detailed explanation of this operation).
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
        :func:`autowig.libclang_front_end.front_end` for an example.
    """
    cmd = ' '.join(flag.strip() for flag in flags)
    if '-x c' in cmd:
        asg._language = 'c'
        s = subprocess.Popen(['clang', '-x', 'c', '-v', '-E', '/dev/null'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif '-x c++' in cmd:
        asg._language = 'c++'
        s = subprocess.Popen(['clang++', '-x', 'c++', '-v', '-E', '/dev/null'],
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
            flags.extend(['-I'+str(path(sysinclude.strip()).abspath()) for sysinclude in sysincludes])

    if not '::' in asg._nodes:
        asg._nodes['::'] = dict(proxy = NamespaceProxy)
    if not '::' in asg._syntax_edges:
        asg._syntax_edges['::'] = []

    for directory in asg.directories():
        directory.is_searchpath = False

    for flag in flags:
        if flag.startswith('-I'):
            includedir = asg.add_directory(flag.strip('-I'))
            includedir.is_searchpath = True

    for fundamental in subclasses(FundamentalTypeProxy):
        if isinstance(fundamental.node, basestring):
            if not fundamental.node in asg._nodes:
                asg._nodes[fundamental.node] = dict(proxy = fundamental)
            if not fundamental.node in asg._syntax_edges['::']:
                asg._syntax_edges['::'].append(fundamental.node)

    headers = [path(header) if not isinstance(header, path) else header for header in headers]
    return "\n".join('#include "' + header.abspath() + '"')

def postprocessing(asg, headers, overload='all'):
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
        :func:`autowig.libclang_front_end.front_end` for an example.
        :func:`compute_overloads`, :func:`discard_forward_declarations` and :func:`resolve_templates` for a more detailed documentatin about AutoWIG front-end post-processing step.
    """
    for header in headers:
        asg[header].is_standalone = True
    compute_overloads(asg, overload=overload)
    discard_forward_declarations(asg)
    resolve_templates(asg)

def compute_overloads(asg, overload):
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
            fct.is_overload = True
    else:
        for fct in asg.functions(free=free):
            if not fct.is_overloaded:
                overloads = fct.overloads
                if len(overloads) > 1:
                    for overload in overloads:
                        overload.is_overloaded = True

def discard_forward_declarations(asg):
    black = set()
    for cls in asg.classes(templated=False):
        if not cls.node in black and not cls.node.startswith('union '):
            if cls.is_complete:
                complete = cls
                if cls.node.startswith('class '):
                    try:
                        duplicate = asg[cls.node.replace('class ', 'struct ', 1)]
                    except:
                        duplicate = None
                elif cls.node.startswith('struct '):
                    try:
                        duplicate = asg[cls.node.replace('struct ', 'class ', 1)]
                    except:
                        duplicate = None
                else:
                    duplicate = None
            else:
                duplicate = cls
                if cls.node.startswith('class '):
                    try:
                        complete = asg[cls.node.replace('class ', 'struct ', 1)]
                    except:
                        complete = None
                elif cls.node.startswith('struct '):
                    try:
                        complete = asg[cls.node.replace('struct ', 'class ', 1)]
                    except:
                        complete = None
                else:
                    complete = None
            if not duplicate is None:
                if isinstance(duplicate, ClassTemplateProxy) and not complete is None:
                    black.add(complete.node)
                    #if complete.is_complete: TODO
                    if isinstance(complete, ClassProxy):
                        for enm in complete.enums():
                            black.add(enm.node)
                        for ncls in complete.classes(recursive=True):
                            black.add(ncls.node)
                            if isinstance(ncls, ClassProxy):
                                for enm in ncls.enums():
                                    black.add(enm.node)
                elif isinstance(complete, ClassTemplateProxy):
                    black.add(duplicate.node)
                    #if duplicate.is_complete:
                    if isinstance(duplicate, ClassProxy):
                        for enm in duplicate.enums():
                            black.add(enm.node)
                        for ncls in duplicate.classes(recursive=True):
                            black.add(ncls.node)
                            if isinstance(ncls, ClassProxy):
                                for enm in ncls.enums():
                                    black.add(enm.node)
                elif complete is None or not complete.is_complete or duplicate.is_complete:
                    black.add(duplicate.node)
                    #if duplicate.is_complete:
                    if isinstance(duplicate, ClassProxy):
                        for enm in duplicate.enums():
                            black.add(enm.node)
                        for ncls in duplicate.classes(recursive=True):
                            black.add(ncls.node)
                            if isinstance(ncls, ClassProxy):
                                for enm in ncls.enums():
                                    black.add(enm.node)
                    if not complete is None:
                        black.add(complete.node)
                        #if complete.is_complete:
                        if isinstance(complete, ClassProxy):
                            for enm in complete.enums():
                                black.add(enm.node)
                            for ncls in complete.classes(recursive=True):
                                black.add(ncls.node)
                                if isinstance(ncls, ClassProxy):
                                    for enm in ncls.enums():
                                        black.add(enm.node)
                else:
                    complete = complete.node
                    duplicate = duplicate.node
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
            if not cls.node in black:
                templates = [tpl.target for tpl in cls.templates]
                while not(len(templates) == 0 or any(tpl.node in black for tpl in templates)):
                    _templates = templates
                    templates = []
                    for _tpl in _templates:
                        if isinstance(_tpl, ClassTemplateSpecializationProxy):
                            templates.extend([tpl.target for tpl in _tpl.templates])
                if not len(templates) == 0:
                    change = True
                    black.add(cls.node)
                    for enm in cls.enums():
                        black.add(enm.node)
                    for ncls in cls.classes(recursive=True):
                        black.add(ncls.node)
                        if isinstance(ncls, ClassProxy):
                            for enm in ncls.enums():
                                black.add(enm.node)
        nb += 1
    gray = set(black)
    for tdf in asg.typedefs():
        if tdf.type.target.node in black:
            gray.add(tdf.node)
            asg._type_edges.pop(tdf.node)
            asg._nodes.pop(tdf.node)
    for var in asg.variables():
        if var.type.target.node in black:
            gray.add(var.node)
            asg._type_edges.pop(var.node)
            asg._nodes.pop(var.node)
    for fct in asg.functions():
        if fct.result_type.target.node in black or any(prm.type.target.node in black for prm in fct.parameters):
            gray.add(fct.node)
            asg._parameter_edges.pop(fct.node)
            asg._type_edges.pop(fct.node)
            asg._nodes.pop(fct.node)
    for parent, children in asg._syntax_edges.items():
        asg._syntax_edges[parent] = [child for child in children if not child in gray]
    gray = set()
    for cls in asg.classes(templated=False):
        if not cls.node in black:
            for ctr in cls.constructors:
                if any(prm.type.target.node in black for prm in ctr.parameters):
                    gray.add(ctr.node)
                    asg._parameter_edges.pop(ctr.node)
                    asg._nodes.pop(ctr.node)
            asg._base_edges[cls.node] = [dict(base = base['base'], access = base['access'], is_virtual = base['is_virtual']) for base in asg._base_edges[cls.node] if not base['base'] in black]
        else:
            enum_constants = cls.enum_constants()
            dtr = cls.destructor
            constructors = cls.constructors
            typedefs = cls.typedefs()
            fields = cls.fields()
            methods = cls.methods()
            for cst in enum_constants:
                gray.add(cst.node)
                asg._nodes.pop(cst.node)
            if not dtr is None:
                asg._nodes.pop(dtr.node)
            for ctr in constructors:
                gray.add(ctr.node)
                asg._parameter_edges.pop(ctr.node)
                asg._nodes.pop(ctr.node)
            for tdf in typedefs:
                gray.add(tdf.node)
                asg._type_edges.pop(tdf.node)
                asg._nodes.pop(tdf.node)
            for fld in fields:
                gray.add(fld.node)
                asg._type_edges.pop(fld.node)
                asg._nodes.pop(fld.node)
            for mtd in methods:
                gray.add(mtd.node)
                asg._parameter_edges.pop(mtd.node)
                asg._type_edges.pop(mtd.node)
                asg._nodes.pop(mtd.node)
    for parent, children in asg._syntax_edges.items():
        asg._syntax_edges[parent] = [child for child in children if not child in gray]
    for cls in asg.classes(templated=True, specialized=False):
        asg._specialization_edges[cls.node] = [spec for spec in asg._specialization_edges[cls.node] if not spec in black]
    for cls in black:
        asg._nodes.pop(cls)
        asg._syntax_edges.pop(cls, None)
        asg._base_edges.pop(cls, None)
        asg._template_edges.pop(cls, None)
        asg._specialization_edges.pop(cls, None)

def resolve_templates(asg):
    for cls in asg.classes(templated=True, specialized=False):
        if hasattr(cls, 'access'):
            for spc in cls.specializations(partial=False):
                asg._nodes[spc.node]['access'] = cls.access
    for cls in asg.classes(templated=None, specialized=True):
        if hasattr(cls, 'access') and not hasattr(cls.specialize, 'access'):
            asg._nodes[cls.specialize.node]['access'] = cls.access

front_end = PluginFunctor.factory('autowig.front_end')

#front_end.__class__.__doc__ = """AutoWIG front-ends functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""
