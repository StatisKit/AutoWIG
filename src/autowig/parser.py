"""
"""

import subprocess
from path import path

from .asg import *
from .tools import subclasses

__all__ = ['preprocessing', 'postprocessing']

def preprocessing(asg, headers, flags):
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
            flags.extend(['-I'+str(path(sysinclude.strip()).abspath()) for sysinclude in sysincludes])

    if not '::' in asg._nodes:
        asg._nodes['::'] = dict(_proxy = NamespaceProxy)
    if not '::' in asg._syntax_edges:
        asg._syntax_edges['::'] = []

    for directory in asg.directories():
        del directory.is_searchpath

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
        header = asg.add_file(header, proxy=HeaderProxy)
        header.is_self_contained = True
        header.is_external_dependency = False

    return "\n".join('#include "' + str(header.abspath()) + '"' for header in headers)

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
