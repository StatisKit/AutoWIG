AutoWIG: Automatic Wrapper and Interface Generator
==================================================

High-level programming languages, like *Python* and *R*, are popular among scientists. They tend to be concise and readable, leading to a rapid development cycle, but suffer from performance drawback compare to compiled language. However, these languages allow to interface *C*, *C++* and *Fortran* code. By this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries. While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming. In this paper, we introduce **AutoWIG**, a *Python* library that wraps automatically *C++* libraries into high-level languages. Our solution consists in parsing *C++* code using **LLVM**/**CLang** technology and generating the wrappers using the **Mako** templating engine. Our approach is automatic, extensible, and can scale from simple *C++* libraries to very complex ones, composed of thousands of classes or using modern meta-programming constructs. The usage and extension of **AutoWIG** is also illustrated on a set of statistical libraries.

> **Summary**
>
> License  
> CeCILL-C license
>
> Version  
> 0.1.0
>
> Status  
> [![Travis][]][] [![Coveralls][]][] [![Landscape][]][] [![Read the Docs]]
>
  [Travis]: https://travis-ci.org/VirtualPlants/AutoWIG.svg?branch=master
  [![Travis]]: https://travis-ci.org/VirtualPlants/AutoWIG
  [Coveralls]: https://coveralls.io/repos/github/VirtualPlants/AutoWIG/badge.svg?branch=master
  [![Coveralls]]: https://coveralls.io/github/VirtualPlants/AutoWIG?branch=master
  [Landscape]: https://landscape.io/github/VirtualPlants/AutoWIG/master/landscape.svg?style=flat
  [![Landscape]]: https://landscape.io/github/VirtualPlants/AutoWIG/master
  [Read the Docs]: https://readthedocs.org/projects/AutoWIG/badge/?version=latest
  [![Read the Docs]]: http://AutoWIG.readthedocs.io/en/latest