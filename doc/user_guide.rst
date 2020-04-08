.. Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ..
..                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ..
.. Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ..
..                                                                       ..
.. This file is part of the AutoWIG project. More information can be     ..
.. found at                                                              ..
..                                                                       ..
..     http://autowig.rtfd.io                                            ..
..                                                                       ..
.. The Apache Software Foundation (ASF) licenses this file to you under  ..
.. the Apache License, Version 2.0 (the "License"); you may not use this ..
.. file except in compliance with the License. You should have received  ..
.. a copy of the Apache License, Version 2.0 along with this file; see   ..
.. the file LICENSE. If not, you may obtain a copy of the License at     ..
..                                                                       ..
..     http://www.apache.org/licenses/LICENSE-2.0                        ..
..                                                                       ..
.. Unless required by applicable law or agreed to in writing, software   ..
.. distributed under the License is distributed on an "AS IS" BASIS,     ..
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ..
.. mplied. See the License for the specific language governing           ..
.. permissions and limitations under the License.                        ..

User guide
==========

.. note:: 

    In this section, we introduce wrapping problems and how **AutoWIG** aims at minimize developers effort.
    Basic concepts and conventions are introduced.

Problem setting
---------------

Consider a scientist who has designed multiple *C++* libraries for statistical analysis.
He would like to distribute his libraries and decide to make them available in *Python* in order to reach a public of scientists, expert and non-expert programmers alike.
Yet, he is not interested in becoming an expert in *C++*/*Python* wrapping, even if it exists classical approaches consisting in writing wrappers with **SWIG** :cite:`Bea03` or **Boost.Python** :cite:`AG03`.
Moreover, he would have serious difficulties to maintain the wrappers, since this semi-automatic process is time consuming and error prone.
Instead, he would like to automate the process of generating wrappers in sync with his evolving *C++* libraries.
That's what the **AutoWIG** software aspires to achieve.

Automating the process
----------------------

Building such a system entails achieving some minimal features:

*C++* parsing
    In order to automatically expose *C++* components in *Python*, the system requires parsing full legacy code implementing the last *C++* standard.
    It has also to represent C++ constructs in Python, like namespaces, enumerators, enumerations, variables, functions, classes or aliases.
    
Documentation
    The documentation of *C++* components has to be associated automatically to their corresponding *Python* components in order to reduce the redundancy and to keep it up-to-date in only one place.

Pythonic interface
    To respect the *Python* philosophy,  *C++* language patterns need to be consistently translated into *Python*.
    Some syntax or design patterns in *C++* code are specific and need to be adapted in order to obtain a functional *Python* package.
    Note that this is particularly sensible for *C++* operators (e.g. :code:`()`, :code:`<`, :code:`[]`) and corresponding *Python* special functions (e.g. :code:`__call__`, :code:`__lt__`, :code:`__getitem__`, :code:`__setitem__`) or for object serialization.

Memory management
    *C++* libraries expose in their interfaces either raw pointers, shared pointers or references, while *Python* handles memory allocation and garbage collection automatically.
    The concepts of pointer or references are thus not meaningful in *Python*.
    These language differences entail several problems in the memory management of *C++* components into *Python*.
    A special attention is therefore required for dealing with references (:code:`&`) and pointers (:code:`*`) that are highly used in *C++*.
    
Error management
    *C++* exceptions need to be consistently managed in *Python*.
    *Python* doesn't have the necessary equipment to properly unwind the *C++* stack when exception are thrown.
    It is therefore important to make sure that exceptions thrown by *C++* code do not pass into the *Python* interpreter core.
    All *C++* exceptions thrown by wrappers must therefore be translated into *Python* errors.
    This translation must preserve exception names and contents in order to raise informative *Python* errors.

Dependency management between components
    The management of multiple dependencies between *C++* libraries with *Python* bindings is required at run-time from *Python*.
    *C++* libraries tends to have dependencies.
    For instance the *C++* **Standard Template Library** containers :cite:`PLMS00` are used in many *C++* libraries (e.g :code:`std::vector`, :code:`std::set`).
    For such cases, it doesn't seem relevant that every wrapped *C++* library contains wrappers for usual **STL** containers (e.g. :code:`std::vector< double >`, :code:`std::set< int >`).
    Moreover, loading in the *Python* interpreter multiple compiled libraries sharing different wrappers from same *C++* components could lead to serious side effects.
    It is therefore required that dependencies across different library bindings can be handled automatically.
