"""
"""

import time
from openalea.core.plugin.functor import PluginFunctor
import pickle

from .ast import *
from .asg import *
from .tools import subclasses

__all__ = ['front_end']

def preprocessing(asg, filepaths, flags, cache=None, force=False):
    """Pre-processing step of an AutoWIG front-end

    During this step, files are added into the Abstract Semantic Graph (ASG) and a string corresponding to the content of a temporary header including all these files is returned.
    The attribute :attr:`is_primary` of nodes corresponding to these files is set to `True` (see :func:`vplants.autowig.middle_end.clean` for a detailed explanation of this operation).
    Nodes corresponding to the C++ global scope and C/C++ fundamental types (:class:`vplants.autowig.asg.FundamentalTypeProxy`) are also added to the ASG if not present.

    :Parameters:
        * `asg` (:class:'vplants.autowig.asg.AbstractSemanticGraph') - The ASG in which the files are added.
        * `filepaths` ([basestring|path]) - Paths to the files. Note that a path can be relative or absolute.
        * `flags ([basestring]) - Flags needed to perform`

    :Returns:
        A temporary header content including all given files.

    :Return Type:
        str

    .. note:: Determine the language of parsed files

        A temporary protected attribute `_language` is added to the ASG.
        This protected attribute is used to determine the language (C or C++) of parsed files during the processing step.
        This temporary attribute is deleted during the post-processing step.

    .. seealso::
        :class:`FrontEndFunctor` for a detailed documentation about AutoWIG front-end step.
        :func:`vplants.autowig.libclang_front_end.front_end` for an example.
    """
    if cache is not None and not force:
        try:
            with open(cache, 'r') as f:
                _asg, _md5 = pickle.load(f)
                if all(filepath in _asg for filepath in filepaths):
                    if all(_asg[header].md5() == _md5[header] for header in _md5):
                        asg._nodes.update(_asg._nodes)
                        asg._syntax_edges.update(_asg._syntax_edges)
                        asg._base_edges.update(_asg._base_edges)
                        asg._type_edges.update(_asg._type_edges)
                        asg._parameter_edges.update(_asg._parameter_edges)
                        asg._template_edges.update(_asg._template_edges)
                        asg._specialization_edges.update(_asg._specialization_edges)
                        asg._include_edges.update(_asg._include_edges)
                        return ''
        except:
            pass
    if 'c' in flags:
        asg._language = 'c'
    elif 'c++' in flags:
        asg._language = 'c++'
    else:
        asg._language = None
    content = ""
    for filenode in [asg.add_file(filepath, proxy=HeaderProxy) for filepath in filepaths]:
        filenode.is_primary = True
        if asg._language == 'c++':
            if filenode.language == 'c':
                content += 'extern "C" { #include "' + filenode.globalname + '" }\n'
            else:
                content += '#include "' + filenode.globalname + '"\n'
                if filenode.language is None:
                    filenode.language = asg._language
        elif asg._language == 'c':
            if filenode.language == 'c++':
                content += 'extern "C++" { #include "' + filenode.globalname + '" }\n'
            else:
                content += '#include "' + filenode.globalname + '" }\n'
                if arg.language is None:
                    arg.language = asg._language
        else:
            content += '#include "' + filenode.globalname + '"\n'

    if not '::' in asg._nodes:
        asg._nodes['::'] = dict(proxy = NamespaceProxy)
    if not '::' in asg._syntax_edges:
        asg._syntax_edges['::'] = []

    for flag in flags:
        if flag.startswith('-I'):
            includedir = asg.add_directory(flag.strip('-I'))
            includedir.as_include = True

    for fundamental in subclasses(FundamentalTypeProxy):
        if isinstance(fundamental.node, basestring):
            if not fundamental.node in asg._nodes:
                asg._nodes[fundamental.node] = dict(proxy = fundamental)
            if not fundamental.node in asg._syntax_edges['::']:
                asg._syntax_edges['::'].append(fundamental.node)

    return content

def postprocessing(asg, filepaths, force_overload=True, cache=None):
    """Post-processing step of an AutoWIG front-end

    During this step, three distinct operations are executed:

        * The **overloading** operation.
          During this operation functions and methods of the Abstract Semantic Graph (ASG) are traversed in order to determine if they are overloaded or not.
          This operation has at worst a time-complexity in :math:`\mathcal{O}\left(F^2\right)` where :math:`F` denotes the number of functions and methods in the ASG.
          Therefore, its default behavior is altered and all functions and methods are considered as overloaded which induces a time-complexity of :math:`\mathcal{O}\left(N\right)` where :math:`N` denotes the number of nodes in the ASG.

        * The **discarding** operation.

        * The **templating** operation.

    :Parameter:
        `force_overload` (bool) - The boolean considered in order to determine if the behavior of the **overloading** operation is altered or not.

    :Return Type:
        `None`

    .. seealso::
        :func:`vplants.autowig.libclang_front_end.front_end` for an example.
        :func:`compute_overloads`, :func:`discard_forward_declarations` and :func:`resolve_templates` for a more detailed documentatin about AutoWIG front-end post-processing step.
    """
    compute_overloads(asg, force_overload=force_overload)
    discard_forward_declarations(asg)
    resolve_templates(asg)
    compute_cache(asg, filepaths, cache)

def compute_overloads(asg, force_overload):
    """
    """
    if force_overload:
        for fct in asg.functions(free=None):
            fct.is_overloaded = True
    else:
        for fct in asg.functions(free=None):
            if not fct.is_overloaded:
                overloads = fct.overloads
                if len(overloads) > 1:
                    for old in overloads:
                        old.is_overloaded = True

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

def compute_cache(asg, filepaths, cache):
    try:
        with open(cache, 'w') as f:
            included = {asg[filepath].globalname for filepath in filepaths}
            curr = asg.files(header=True)
            prev = []
            changed = True
            while changed:
                prev = curr
                curr = []
                changed = False
                while len(prev) > 0:
                    header = prev.pop()
                    if not header.include is None:
                        if header.include.globalname in included:
                            included.add(header.globalname)
                            changed = True
                        else:
                            curr.append(header)
            md5 = {header : asg[header].md5() for header in included}
            pickle.dump((asg, md5), f)
    except:
        pass

front_end = PluginFunctor.factory('autowig.front_end')

#front_end.__class__.__doc__ = """AutoWIG front-ends functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""
