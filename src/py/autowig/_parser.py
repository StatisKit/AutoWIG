## Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ##
##                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
## Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
##                                                                       ##
## This file is part of the AutoWIG project. More information can be     ##
## found at                                                              ##
##                                                                       ##
##     http://autowig.rtfd.io                                            ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

import subprocess
from path import Path
from tempfile import NamedTemporaryFile
import os
import warnings
from .plugin import PluginManager
import sys
import platform
import six

from .asg import (DeclarationProxy,
                  NamespaceProxy,
                  FundamentalTypeProxy,
                  HeaderProxy,
                  VariableProxy,
                  FunctionProxy,
                  ConstructorProxy,
                  ClassProxy,
                  ClassTemplateSpecializationProxy,
                  ClassTemplateProxy,
                  TypedefProxy)
from .tools import subclasses

__all__ = ['pre_processing', 'post_processing']

parser = PluginManager('autowig.parser', brief="AutoWIG front-end plugin_managers",
        details="""AutoWIG front-end plugin_managers are responsible for Abstract Semantic Graph (ASG) completion from C/C++ parsing.

.. seealso:: :class:`autowig.AbstractSemanticGraph` for more details on ASGs""")

def pre_processing(asg, headers, flags, **kwargs):
    """Pre-processing step of an AutoWIG front-end

    During this step, files are added into the Abstract Semantic Graph (ASG)
    and a string corresponding to the content of a temporary header including
    all these files is returned. The attribute :attr:`is_primary` of nodes
    corresponding to these files is set to `True` (see
    :func:`autowig.controller.clean` for a detailed explanation of this operation).
    Nodes corresponding to the C++ global scope and C/C++ fundamental types 
    (:class:`autowig.asg.FundamentalTypeProxy`) are also added to the ASG if 
    not present.

    :Parameters:
     - `asg` (:class:'autowig.asg.AbstractSemanticGraph') - The ASG in which the 
                                                            files are added.
     - `headers` ([basestring|path]) - Paths to the source code. Note that a path
                                       can be relative or absolute.
     - `flags` ([basestring]) - Flags needed to perform the syntaxic analysis 
                                of source code.


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
    cmd = ' '.join(flag.strip() for flag in flags)

    bootstrapping = kwargs.pop('bootstrapping', False)

    if hasattr(asg, '_headers'):
        delattr(asg, '_headers')

    if not bootstrapping:
        for directory in asg.directories():
            del directory.is_searchpath

        for header in asg.files(header=True):
            del header.is_external_dependency

        for flag in flags:
            if flag.startswith('-I'):
                includedir = asg.add_directory(flag.strip('-I'))
                includedir.is_searchpath = True
            if flag.startswith('/I'):
                includedir = asg.add_directory(flag.strip('/I'))
                includedir.is_searchpath = True

    SYSTEMS = dict(Linux   = "linux",
                   Darwin  = "osx",
                   Windows = "win")
    system = str(platform.system())
    if not system in SYSTEMS:
      system = "unknown"
    else:
      system = SYSTEMS[system]

    if '-x c++' in cmd:
        asg._language = 'c++'
    elif '-x c' in cmd:
        asg._language = 'c'
    else:
        raise ValueError('\'flags\' parameter must include the `-x` option with `c` or `c++`')

    if not bootstrapping:
        if system == 'win':
            devnull = 'nul'
            compiler = 'clang'
        elif system == 'linux':
            devnull = '/dev/null'
            if asg._language == 'c++':
                compiler = os.environ.get('GXX', 'clang')
            else:
                compiler = os.environ.get('GCC', 'clang')
        elif system == 'osx':
            devnull = '/dev/null'
            if asg._language == 'c++':
                compiler = os.environ.get('CLANGXX', os.environ.get('CLANG__', 'clang'))
            else:
                compiler = os.environ.get('CLANG', 'clang')
        else:
            raise Exception("unknown system")

        s = subprocess.Popen([compiler, '-x', asg._language, '-v', '-E', devnull],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if s.returncode:
            warnings.warn('System includes not computed: clang command failed', Warning)
        else:
            out, err = s.communicate()
            if six.PY3:
                err = err.decode('ascii', 'ignore')
            sysincludes = err.splitlines()
            if '#include <...> search starts here:' not in sysincludes or 'End of search list.' not in sysincludes:
                warnings.warn('System includes not computed: parsing clang command output failed', Warning)
            else:
                sysincludes = sysincludes[sysincludes.index('#include <...> search starts here:')+1:sysincludes.index('End of search list.')]
                if system == 'win':
                    if 'msvc_version' in kwargs:
                        msvc_version = kwargs.pop('msvc_version')
                        sysincludes = [str(Path(sysinclude.strip()).abspath()).replace('14.0', msvc_version) for sysinclude in sysincludes]
                    else:
                        sysincludes = [str(Path(sysinclude.strip()).abspath()) for sysinclude in sysincludes]
                else:
                    sysincludes = [str(Path(sysinclude.strip()).abspath()) for sysinclude in sysincludes]
                    if system == 'linux':
                        sysincludes = [sysinclude for sysinclude in sysincludes if not 'lib/gcc' in sysinclude and os.path.exists(sysinclude)]
                        s = subprocess.Popen(['clang', '-x', asg._language, '-v', '-E', devnull],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if s.returncode:
                            warnings.warn('System includes not computed: clang command failed', Warning)
                        else:
                            out, err = s.communicate()
                            if six.PY3:
                                err = err.decode('ascii', 'ignore')
                            _sysincludes = err.splitlines()
                            if '#include <...> search starts here:' not in _sysincludes or 'End of search list.' not in _sysincludes:
                                warnings.warn('System includes not computed: parsing clang command output failed', Warning)
                            else:
                                _sysincludes = [str(Path(sysinclude.strip()).abspath()) for sysinclude in _sysincludes]
                                sysincludes += [sysinclude for sysinclude in _sysincludes if 'lib/clang' in sysinclude and os.path.exists(sysinclude)]
                flags.extend(['-I' + sysinclude for sysinclude in sysincludes if not '-I' + sysinclude in flags])
                for sysinclude in sysincludes:
                    asg.add_directory(sysinclude).is_searchpath = True

    if system == 'win':
        if '-fno-exceptions' not in flags and '-fexceptions' not in flags:
            flags.append('-fexceptions')

        if '-fno-cxx-exceptions' not in flags and '-fcxx-exceptions' not in flags:
            flags.append('-fcxx-exceptions')

    if '::' not in asg._nodes:
        asg._nodes['::'] = dict(_proxy = NamespaceProxy)
    if '::' not in asg._syntax_edges:
        asg._syntax_edges['::'] = []

    for fundamental in subclasses(FundamentalTypeProxy):
        if hasattr(fundamental, '_node'):
            if fundamental._node not in asg._nodes:
                asg._nodes[fundamental._node] = dict(_proxy = fundamental)
            if fundamental._node not in asg._syntax_edges['::']:
                asg._syntax_edges['::'].append(fundamental._node)

    headers = [Path(header) if not isinstance(header, Path) else header for header in headers]

    if not bootstrapping:
        for header in headers:
            header = asg.add_file(header, proxy=HeaderProxy, _language=asg._language)
            header.is_self_contained = True
            header.is_external_dependency = False

    return "\n".join('#include "' + str(header.abspath()) + '"' for header in headers)

def post_processing(asg, flags, **kwargs):
    if not kwargs.pop('bootstrapping', False):
        bootstrap(asg, flags, **kwargs)
        update_overload(asg, **kwargs)
        suppress_forward_declaration(asg, **kwargs)
    return asg

def bootstrap(asg, flags, **kwargs):
    bootstrap = kwargs.pop('bootstrap', True)
    maximum = kwargs.pop('maximum', 1000)
    maxdepth = kwargs.pop('depth', 1)
    if bootstrap:
        __index = 0
        if isinstance(bootstrap, bool):
            bootstrap = float("Inf")
        nodes = 0
        while not nodes == len(asg) and __index < bootstrap:
            nodes = len(asg)
            black = set()
            white = {asg['::'] : 0 }
            gray = set()
            while len(white) > 0:
                node, depth = white.popitem()

                if node.access in ['none', 'public']:
                    if isinstance(node, NamespaceProxy):
                        for dcl in node.declarations():
                            header = dcl.header
                            if isinstance(dcl, NamespaceProxy) or header and not header.is_external_dependency and dcl._node not in black:
                                white[dcl] = depth
                                black.add(dcl._node)              
                    elif isinstance(node, (TypedefProxy, VariableProxy)) and depth <= maxdepth - 1:
                        target = node.qualified_type.desugared_type.unqualified_type
                        if target._node not in black:
                            if isinstance(node, TypedefProxy):
                                white[target] = min(white.get(target, depth), depth)
                            else:
                                white[target] = min(white.get(target, depth + 1), depth + 1)
                            black.add(target._node)
                    elif isinstance(node, FunctionProxy) and depth <= maxdepth - 1:
                        return_type = node.return_type.desugared_type.unqualified_type
                        if return_type._node not in black:
                            white[return_type] = min(white.get(return_type, depth + 1), depth + 1)
                            black.add(return_type._node)
                        for parameter in node.parameters:
                            target = parameter.qualified_type.desugared_type.unqualified_type
                            if target._node not in black:
                                white[target] = min(white.get(target, depth + 1), depth + 1)
                                black.add(target._node)
                    elif isinstance(node, ConstructorProxy) and depth <= maxdepth - 1:
                        for parameter in node.parameters:
                            target = parameter.qualified_type.desugared_type.unqualified_type
                            if target._node not in black:
                                white[target] = min(white.get(target, depth + 1), depth + 1)
                                black.add(target._node)
                    elif isinstance(node, ClassProxy)  and depth <= maxdepth:
                        for base in node.bases():
                            if base.access == 'public':
                                if base._node not in black:
                                    white[base] = min(white.get(base, depth), depth)
                                    black.add(base._node)
                        for dcl in node.declarations():
                            try:
                                if dcl.access == 'public':
                                    if dcl._node not in black:
                                        white[dcl] = min(white.get(dcl, depth), depth)
                                        black.add(dcl._node)
                            except:
                                pass
                        if isinstance(node, ClassTemplateSpecializationProxy) and (not node.is_complete or any([not cls.is_complete for cls in node.classes(templated=False)])):
                            gray.add(node._node)
            gray = list(gray)
            for gray in [gray[index:index+maximum] for index in xrange(0, len(gray), maximum)]:
                headers = []
                for header in asg.files(header=True):
                    if not header.is_external_dependency:
                        headers.append("#include \"" + header.globalname + "\"")
                headers.append("")
                for spc in gray:
                    if spc not in asg._bootstrapped:
                        headers.append("template " + spc + ";")
                asg._bootstrapped.update(set(gray))
                header = NamedTemporaryFile(delete=False)
                if six.PY2:
                    header.write('\n'.join(headers))
                else:
                    header.write(('\n'.join(headers)).encode())
                header.close()
                asg = parser(asg, [header.name], flags + ["-Wno-everything",  "-ferror-limit=0"], bootstrapping=True, **kwargs)
                os.unlink(header.name)
                if header.name in asg:
                    asg._syntax_edges[asg[header.name].parent.globalname].remove(header.name)
                    asg._nodes.pop(header.name)
                asg._include_edges.pop(header.name, None)
                asg._include_edges = {key : value for key, value in asg._include_edges.iteritems() if not value == header.name}
                for node in asg._nodes.keys():
                    if '_header' in asg._nodes[node] and asg._nodes[node]['_header'] == header.name:
                        asg._nodes[node].pop('_header')
            __index += 1

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
        for fct in asg.functions(free=None):
            overloads = fct.overloads
            if len(overloads) > 1:
                for fct in overloads:
                    fct.is_overloaded = True
            else:
                fct.is_overloaded = False
    elif overload == 'namespace':
        for fct in asg.functions(free=True):
            overloads = fct.overloads
            if len(overloads) > 1:
                for fct in overloads:
                    fct.is_overloaded = True
            else:
                fct.is_overloaded = False
        for fct in asg.functions(free=False):
            fct.is_overloaded = True
    elif overload == 'class':
        for fct in asg.functions(free=False):
            overloads = fct.overloads
            if len(overloads) > 1:
                for fct in overloads:
                    fct.is_overloaded = True
            else:
                fct.is_overloaded = False
        for fct in asg.functions(free=True):
            fct.is_overloaded = True
    elif overload == 'none':
        for fct in asg.functions(free=None):
            fct.is_overloaded = True
    else:
        raise ValueError('\'overload\' parameter')

def suppress_forward_declaration(asg, **kwargs):
    """
    """
    # TODO More
    for cls in asg.classes(templated=False, specialized=True):
        tpl = cls.specialize
        for mtd in cls.methods():
            qtype = mtd.return_type
            if qtype.unqualified_type.parent == tpl:
                utype = asg._type_edges[mtd._node]["target"].replace('::' + tpl.localname + '::', '::' + cls.localname + '::', 1)
                if utype in asg:
                    asg._type_edges[mtd._node]["target"] = utype
            for parm in mtd.parameters:
                qtype = parm.qualified_type
                if qtype.unqualified_type.parent == tpl:
                    utype = asg._parameter_edges[mtd._node][parm.index]["target"].replace('::' + tpl.localname + '::', '::' + cls.localname + '::', 1)
                    if utype in asg:
                        asg._parameter_edges[mtd._node][parm.index]["target"] = utype
        for ctr in cls.constructors():
            for parm in ctr.parameters:
                qtype = parm.qualified_type
                if qtype.unqualified_type.parent == tpl:
                    utype = asg._parameter_edges[ctr._node][parm.index]["target"].replace('::' + tpl.localname + '::', '::' + cls.localname + '::', 1)
                    if utype in asg:
                        asg._parameter_edges[ctr._node][parm.index]["target"] = utype
    black = set()
    def blacklist(cls, black):
        black.add(cls._node)
        if isinstance(cls, ClassProxy):
            for enm in cls.enumerations():
                black.add(enm._node)
            for tdf in cls.typedefs():
                black.add(tdf._node)
            for cls in cls.classes():
                blacklist(cls, black)
    def blacklisted(type, black):
        return type.unqualified_type._node in black or type.desugared_type.unqualified_type._node in black
    for cls in asg.classes(templated=False):
        if cls._node not in black and not cls._node.startswith('union '):
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
            if duplicate is not None:
                if isinstance(duplicate, ClassTemplateProxy) and complete is not None:
                    blacklist(complete, black)
                elif isinstance(complete, ClassTemplateProxy):
                    blacklist(duplicate, black)
                elif complete is None or not complete.is_complete or duplicate.is_complete:
                    blacklist(duplicate, black)
                    if complete is not None:
                        blacklist(complete, black)
                else:
                    complete = complete._node
                    duplicate = duplicate._node
                    for edge in asg._type_edges.itervalues():
                        if edge['target'] == duplicate:
                            edge['target'] = complete
                    for edges in asg._base_edges.itervalues():
                        for index, edge in enumerate(edges):
                            if edge['base'] == duplicate:
                                edges[index]['base'] = complete
                    for  edges in asg._template_edges.itervalues():
                        for index, edge in enumerate(edges):
                            if edge['target'] == duplicate:
                                edges[index]['target'] = complete
                    if 'access' in asg._nodes[duplicate]:
                        asg._nodes[complete]['access'] = asg._nodes[duplicate]['access']
                    black.add(duplicate)
    change = True
    nb = 0
    _nodes = set()
    while change:
        change = False
        for cls in asg.classes(specialized=True, templated=False):
            # TODO templated=None
            if cls._node not in black:
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
    prev = -1
    gray = set(black)
    def to_blacklist(obj, black, asg):
        if obj._node in black:
            return True
        else:
            parent = obj.parent
            if parent is None:
                return True
            else:
                return parent._node in black or obj._node not in asg._syntax_edges[parent._node]
    while not prev == len(black):
        prev = len(black)
        for tdf in asg.typedefs():
            if blacklisted(tdf.qualified_type, black):
                black.add(tdf._node)
                gray.add(tdf._node)
        for enm in asg.enumerations():
            if to_blacklist(enm, black, asg):
                black.add(enm._node)
                _nodes.add(enm._node)
                enumerators = enm.enumerators
                for enm in enumerators:
                    gray.add(enm._node)
                    #asg._nodes.pop(enm._node)
                    _nodes.add(enm._node)
    _type_edges = set()
    _parameter_edges = set()
    for enm in asg.enumerators():
        if to_blacklist(enm, black, asg):
            gray.add(enm._node)
            #asg._nodes.pop(enm._node)
            _nodes.add(enm._node)
    for var in asg.variables():
        if blacklisted(var.qualified_type, black) or to_blacklist(var, black, asg):
            gray.add(var._node)
            #asg._type_edges.pop(var._node)
            _type_edges.add(var._node)
            #asg._nodes.pop(var._node)
            _nodes.add(var._node)
    for fct in asg.functions():
        if blacklisted(fct.return_type, black) or any(blacklisted(prm.qualified_type, black) for prm in fct.parameters) or to_blacklist(fct, black, asg):
            gray.add(fct._node)
            #asg._parameter_edges.pop(fct._node)
            _parameter_edges.add(fct._node)
            #asg._type_edges.pop(fct._node)
            _type_edges.add(fct._node)
            #asg._nodes.pop(fct._node)
            _nodes.add(fct._node)
    for ctr in asg.constructors():
        if any(blacklisted(prm.qualified_type, black) for prm in ctr.parameters) or to_blacklist(ctr, black, asg):
            gray.add(ctr._node)
            #asg._parameter_edges.pop(fct._node)
            _parameter_edges.add(ctr._node)
            #asg._type_edges.pop(fct._node)
            # _type_edges.add(ctr._node)
            #asg._nodes.pop(fct._node)
            _nodes.add(ctr._node)
    for dtr in asg.destructors():
        if to_blacklist(dtr, black, asg):
            gray.add(dtr._node)
            #asg._parameter_edges.pop(fct._node)
            # _parameter_edges.add(ctr._node)
            #asg._type_edges.pop(fct._node)
            # _type_edges.add(ctr._node)
            #asg._nodes.pop(fct._node)
            _nodes.add(dtr._node)
    # for tdf in asg.typedefs():
    #     if blacklisted(tdf.qualified_type, gray) or to_blacklist(tdf, gray, asg):
    #         gray.add(tdf._node)
    for parent, children in asg._syntax_edges.items():
        asg._syntax_edges[parent] = [child for child in children if child not in gray]
    # gray = set()
    # for cls in asg.classes(templated=False):
    #     if cls._node not in black:
    #         for ctr in cls.constructors():
    #             if any(blacklisted(prm.qualified_type, black) for prm in ctr.parameters):
    #                 gray.add(ctr._node)
    #                 #asg._parameter_edges.pop(ctr._node)
    #                 _parameter_edges.add(ctr._node)
    #                 #asg._nodes.pop(ctr._node)
    #                 _nodes.add(ctr._node)
    #         asg._base_edges[cls._node] = [dict(base = base['base'],
    #                                            _access = base['_access'],
    #                                            _is_virtual = base['_is_virtual'])
    #                                       for base in asg._base_edges[cls._node]
    #                                       if not base['base'] in black]
    #     else:
    #         enumerators = cls.enumerators()
    #         dtr = cls.destructor
    #         constructors = cls.constructors()
    #         typedefs = cls.typedefs()
    #         fields = cls.fields()
    #         methods = cls.methods()
    #         for enm in enumerators:
    #             gray.add(enm._node)
    #             #asg._nodes.pop(enm._node)
    #             _nodes.add(enm._node)
    #         if dtr is not None:
    #             #asg._nodes.pop(dtr._node)
    #             _nodes.add(dtr._node)
    #         for ctr in constructors:
    #             gray.add(ctr._node)
    #             #asg._parameter_edges.pop(ctr._node)
    #             _parameter_edges.add(ctr._node)
    #             #asg._nodes.pop(ctr._node)
    #             _nodes.add(ctr._node)
    #         # for tdf in typedefs:
    #         #     gray.add(tdf._node)
    #         #     #asg._type_edges.pop(tdf._node)
    #         #     _type_edges.add(tdf._node)
    #         #     #asg._nodes.pop(tdf._node)
    #         #     _nodes.add(tdf._node)
    #         for fld in fields:
    #             gray.add(fld._node)
    #             #asg._type_edges.pop(fld._node)
    #             _type_edges.add(fld._node)
    #             #asg._nodes.pop(fld._node)
    #             _nodes.add(fld._node)
    #         for mtd in methods:
    #             gray.add(mtd._node)
    #             #asg._parameter_edges.pop(mtd._node)
    #             _parameter_edges.add(mtd._node)
    #             #asg._type_edges.pop(mtd._node)
    #             _type_edges.add(mtd._node)
    #             #asg._nodes.pop(mtd._node)
    #             _nodes.add(mtd._node)
    for cls in asg.classes(templated=False):
        asg._base_edges[cls._node] = [base for base in asg._base_edges[cls._node] if base['base'] not in black]
    for cls in asg.classes(templated=True, specialized=False):
        asg._specialization_edges[cls._node] = {spec for spec in asg._specialization_edges[cls._node] if spec not in black}
    for type_edge in _type_edges:
        asg._type_edges.pop(type_edge)
    _nodes = [node for node in _nodes if node not in black]
    for node in _nodes:
        asg._nodes.pop(node)
    for parameter_edge in _parameter_edges:
        asg._parameter_edges.pop(parameter_edge)
    for parent, children in asg._syntax_edges.items():
        asg._syntax_edges[parent] = [child for child in children if child not in gray]
    for cls in black:
        asg._nodes.pop(cls)
        asg._type_edges.pop(cls, None)
        asg._syntax_edges.pop(cls, None)
        asg._base_edges.pop(cls, None)
        asg._template_edges.pop(cls, None)
        asg._specialization_edges.pop(cls, None)