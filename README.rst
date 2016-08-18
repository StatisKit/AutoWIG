AutoWIG: Automatic Wrapper and Interface Generator
##################################################

High-level programming languages, like *Python* and *R*, are popular among scientists.
They tend to be concise and readable, leading to a rapid development cycle, but suffer from performance drawback compare to compiled language.
However, these languages allow to interface *C*, *C++* and *Fortran* code.
By this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries.
While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming.
In this paper, we introduce **AutoWIG**, a *Python* library that wraps automatically *C++* libraries into high-level languages.
Our solution consists in parsing *C++*  code using **LLVM**/**CLang** technology and generating the wrappers using the **Mako** templating engine.
Our approach is automatic, extensible, and can scale from simple *C++* libraries to very complex ones, composed of thousands of classes or using modern meta-programming constructs.
The usage and extension of **AutoWIG** is also illustrated on a set of statistical libraries.

.. sidebar:: Summary

    :Version: |VERSION|
    :Status: |TRAVIS| |COVERALLS| |LANDSCAPE| |READTHEDOCS|
    :License: |LICENSE|
    :Authors: |AUTHORS|

.. |LICENSE| replace:: see |LICENSELINK|_

.. |AUTHORS| replace:: see |AUTHORSLINK|_

.. |VERSION| replace:: 0.1.0

.. |LICENSELINK| replace:: LICENSE.rst file

.. _LICENSELINK : LICENSE.rst

.. |AUTHORSLINK| replace:: AUTHORS.rst file

.. _AUTHORSLINK : AUTHORS.rst

.. |VERSION| replace:: 0.1.0

.. |TRAVIS| image:: https://travis-ci.org/StatisKit/AutoWIG.svg?branch=master
           :target: https://travis-ci.org/StatisKit/AutoWIG
           :alt: Travis

.. |COVERALLS| image:: https://coveralls.io/repos/github/StatisKit/AutoWIG/badge.svg?branch=master
               :target: https://coveralls.io/github/StatisKit/AutoWIG?branch=master
               :alt: Coveralls

.. |LANDSCAPE| image:: https://landscape.io/github/StatisKit/AutoWIG/master/landscape.svg?style=flat
                :target: https://landscape.io/github/StatisKit/AutoWIG/master
                :alt: Landscape

.. |READTHEDOCS| image:: https://readthedocs.org/projects/AutoWIG/badge/?version=latest
                :target: http://AutoWIG.readthedocs.io/en/latest
                :alt: Read the Docs
