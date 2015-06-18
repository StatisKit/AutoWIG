# Title

AutoWIG: An automatic wrapper generator of large C++ libraries in Python

# Audience level

- [ ] Novice
- [x] Intermediate
- [ ] Experienced

# Brief description
<!---
If your proposal is accepted this will be made public and printed in the program.
Should be one paragraph, maximum 400 characters.
-->

The Python programming language is one of the most popular language in scientific computing.
However, most scientifc Python libraries incorporates C++ libraries.
While several semi-automatic solution and tools exist to wrap large C++ libraries, the process of wrapping a large C++ library is cumbersome and time consumming.
Some solutions have been developped in the past (e.g. Py++) but require to write complex code to automate the process, and rely on technologies that are not maintained.
AutoWIG relies on the LLVM/Clang technology for parsing C/C++ code and the Mako templating engine for generating Boost.Python wrappers.
Rather than having to write parsers in Python like in Py++, the approach is similar to XDress, but for Boost.Python wrappers instead of Cython wrappers.
We will demonstrate the use of AutoWIG on a complex collection of C++ libraries for statistical analysis.

# Detailed abstract
<!---
Detailed outline.
Will be made public if your proposal is accepted.
-->

[AutoWIG (Automatic Wrapper and Interface Generator)](https://github.com/VirtualPlants/autowig) is an automatic wrapper generator for C/C++ libraries written in Python and based on [LLVM/Clang](http://clang.llvm.org/).
It generates Boost.Python code for C/C++ enumerations, variables, functions, C structures and C++ classes in order to provide Python bindings for C/C++ libraries.

The main features of AutoWIG are:

*   The automatic construction of Abstract Semantic Graphs (ASGs) in Python from Abstract Syntax Trees (ASTs) given by LLVM/Clang.
*   The versatile generation of Python bindings using the Python [Mako](http://www.makotemplates.org) templating engine.

ASTs produced by LLVM/Clang are not capable of representing shared subexpressions due to their simplistic structure, this simplicity comes at a cost of efficiency due to redundant duplicate computations of identical terms.
AutoWIG therefore constructs an ASG from a LLVM/Clang AST by a process of enrichment and abstraction.
This enrichment can for example be the addition of nodes (types) and edges to represent variables or parameters types.
The abstraction entail the removal of details which are relevant only in parsing, such as forward declarations.
In particular this ASG representation enables code introspection via graph traversals such as the inquiry of number of classes, list of class methods, list of all types of inputs and outputs considered in class methods...
This provides an efficient and simple way to produces minimal induced subgraphs of C/C++ library ASGs where minimal stands for the addition of a minimal number of vertices to a given subset of vertices in order to obtain an induced subgraph of the ASG.

The use of a templating engine for the wrapper generation consists in the use of a default template that can be applied to any node (or set of nodes) of an ASG in order to produce the corresponding Boost.Python wrapper.
This template concentrate the Boost.Python knowledge required to produce reflexive wrappers.
Since for some C++ libraries this behaviour is not wanted or would need slight modifications, this template is encapsulated into a class that can be derived in order to adapt the wanted bindings.
The wrapper generation step of AutoWIG is therefore considered as a collection of Python scripts specifying the template to consider and nodes targeted.

Currently the AutoWIG package is integrated into [SCons](http://www.scons.org/) via the definition of builders for [OpenAlea](http://openalea.gforge.inria.fr/dokuwiki/doku.php) packages.
Future work considered is the implementation of magic cells for [IPython Notebooks](http://ipython.org/notebook.html) and [OpenAleaLab](https://github.com/openalea/openalea/wiki/Roadmap:-OpenAleaLab) in order to provide a simple way to integrate C/C++ code into Python notebooks and workflows.
Note that the comparison with state of the art wrapper generators (such as [XDress](http://xdress.org/latest/index.html)) is also envisaged.
In particular, such a comparison could lead to a deeper investigation of the respective advantages and inconvenients of Boost.Python and Cython wrappers.

This talk will focus on the generation of Python bindings for C++ libraries.
This will be illustrated by the bootstrapping of LLVM/Clang Python bindings in order to enable the generation of wrappers for template class instantiated.
The case of Python bindings generation for multiple C++ libraries (for statistical analysis) with dependencies will also be discussed (in particular with C++ standard library containers).

# Additional notes
<!---
Anything else you'd like the program committee to know when making their selection: your past experience, etc.
This is not made public. 
-->
