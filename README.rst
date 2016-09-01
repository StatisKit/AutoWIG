AutoWIG: Automatic Wrapper and Interface Generator
##################################################

High-level programming languages, such as *Python* and *R*, are popular among scientists.
They are concise, readable and lead to rapid development cycles, but suffer from performance drawback compared to compiled language. 
However, these languages allow to interface *C*, *C++* and *Fortran* code.
In this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries.
While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming.
**AutoWIG** is a *Python* library that wraps automatically compiled libraries into high-level languages.
Our approach consists in parsing *C++*  code using the **LLVM**/**Clang** technologies and generating the wrappers using the **Mako** templating engine.
Our approach is automatic, extensible, and applies to very complex *C++* libraries, composed of thousands of classes or incorporating modern meta-programming constructs.

.. sidebar:: Summary

    :Status: |TRAVIS| |COVERALLS| |LANDSCAPE| |READTHEDOCS|
    :License: |LICENSE|
    :Authors: |AUTHORS|
    
.. |LICENSE| replace:: see |LICENSELINK|_ file

.. |AUTHORS| replace:: see |AUTHORSLINK|_ file

.. |VERSION| replace:: 0.1.0

.. |LICENSELINK| replace:: LICENSE.rst

.. _LICENSELINK : LICENSE.rst

.. |AUTHORSLINK| replace:: AUTHORS.rst

.. _AUTHORSLINK : AUTHORS.rst

.. |VERSION| replace:: 0.1.0

.. |TRAVIS| image:: https://travis-ci.org/StatisKit/AutoWIG.svg?branch=master
           :target: https://travis-ci.org/StatisKit/AutoWIG
           :alt: Travis

.. |COVERALLS| image:: https://coveralls.io/repos/github/StatisKit/AutoWIG/badge.svg
               :target: https://coveralls.io/github/StatisKit/AutoWIG?branch=master
               :alt: Coveralls

.. |LANDSCAPE| image:: https://landscape.io/github/StatisKit/AutoWIG/master/landscape.svg?style=flat
                :target: https://landscape.io/github/StatisKit/AutoWIG/master
                :alt: Landscape

.. |READTHEDOCS| image:: https://readthedocs.org/projects/AutoWIG/badge/?version=latest
                :target: http://AutoWIG.readthedocs.io/en/latest
                :alt: Read the Docs
