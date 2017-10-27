**AutoWIG**: Automatic Wrapper and Interface Generator
######################################################

High-level programming languages, such as *Python* and *R*, are popular among scientists.
They are concise, readable, lead to rapid development cycles, but suffer from performance drawback compared to compiled language. 
However, these languages allow to interface *C*, *C++* and *Fortran* code.
In this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries.
While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming.
**AutoWIG** is a *Python* library that wraps automatically compiled libraries into high-level languages.
Our approach consists in parsing *C++*  code using the **LLVM**/**Clang** technologies and generating the wrappers using the **Mako** templating engine.
Our approach is automatic, extensible, and applies to very complex *C++* libraries, composed of thousands of classes or incorporating modern meta-programming constructs.
