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

Citation
========

If you use AutoWIG in a scientific publication, we would appreciate citations: 

         Fernique P, Pradal C. (2018) AutoWIG: automatic generation of python bindings for C++ libraries. PeerJ Computer Science 4:e149 https://doi.org/10.7717/peerj-cs.149 
