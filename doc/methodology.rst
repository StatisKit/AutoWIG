Methodology
===========

In this section, we present a methodological workflow to wrap *C++* libraries in *Python* using  **AutoWIG** .
The workflow is composed on 3 steps: a :code:`Parse`, a :code:`Control`, and a :code:`Generate` step.
First, the :code:`Parse` step parse the *C++* components and produce a graph database that represent them.
Then, this graph database is traverse by the :code:`Control` step to select which *C++* components  will be wrapped and how.
Finally, the :code:`Generate` step will produce the *C++* files containing the wrappers.
This workflow can be executed interactively in an interpreter for exploratory purpose, or integrated in a software construction tool for automation.
The next subsections present with more details the interactive and integrated options for workflow execution.

An interactive workflow
-----------------------

A major functionality of **AutoWIG** is its interactivity.
As for scripting languages (versus compiled langagues), interactive processing have some advantages versus batch processing.
In our context, such advantages are that an interactive framework allows developers to look at the abstraction of their code, test new wrapping strategies and evaluate their outcomes directly.
%that can be used for training purpose, wrapping strategies comparisons or one-shot library wrapping.
In such cases, the user must consider the following $3$ steps:

:code:`Parse`
    In *C++* library, headers contain all declarations of usable *C++* components.
         In this step, **AutoWIG** performs a syntactic and a semantic analysis of these headers to obtain a proper abstraction of available *C++* components (see section~\ref{subsec:architecture:plugin} for more details).
    This abstraction is a graph database within which each *C++* component (namespaces, enumerators, enumerations, variables, functions, classes and aliases) used in the *C++* library are represented by a node.
    Edges connecting nodes in this graph database represent syntactic or semantic relation between nodes (see section~\ref{subsec:architecture:asg} for more details).
    Mandatory inputs of this workflow are headers and relevant compilation flags to conduct the *C++* code parsing (see section~\ref{subsec:results:simple} for an example).

:code:`Control`
    Once the *C++* code parsing step has been computed, the graph database can be used to interactively inspect the *C++* code.
    This step is particularly useful for controlling the output of this workflow.
    By default, **AutoWIG** has a set of rules for determining which *C++* components to wrap, selecting the adapted memory management, identifying special classes representing exceptions or smart pointers, adapting *C++* philosophy to *Python* and managing library dependencies (see section~\ref{subsec:architecture:plugin} for more details).
    Such rules produce consistent wrapping of *C++* libraries following precise guidelines (see section~\ref{sec:guidelines} for more details).
    This step enable the control of parameters to ensure a consistent wrapping of a *C++* library, even if it does not respect **AutoWIG** guidelines (see section~\ref{subsec:results:pyclanglite} for an example).

:code:`Generate`
    Once control parameters have been correctly set in the :code:`Control` step, the process of wrapping consists in the generation of wrapper functions for each *C++* component.
    This is also coupled with the generation of a pythonic interface for the *Python* module containing the wrappers (see section~\ref{subsec:architecture:plugin} for more details).
    This code generation step is based on graph database traversals and rules using *C++* code introspection realizable via the graph database (e.g. parent scope, type of variables, inputs and output of functions, class bases and members).
    The outputs of this workflow consists in *C++* files containing wrappers that need to be compiled and a *Python* file proposing a pythonic interface for the *C++* library (see section~\ref{subsec:results:simple} for an example).

Integrated workflows
--------------------

If an interactive workflow is very convenient for first approaches with **AutoWIG**, once the wrapping strategies have been chosen, batch mode workflows are of most interest.
Note that the usage of the \pkg{IPython} console :cite:`PG07` and its :code:`%history` magic function enable to save an interactive workflow into a *Python* file that can be executed in batch mode using the :code:`python` command line.

In order to ease the deployment of libraries, in particular for multiple platform support, software construction tools such as \pkg{CMake} :cite:`MH10` or **SCons** :cite:`Kni05` are used by developers.
Since such tools provide the information required for *C++* code parsing in **AutoWIG** (i.e. headers and compilation flags), it is convenient and desirable to intricate the wrapping process of **AutoWIG** with the deployment process of these software construction tools (see figure~\ref{fig:scons:workflow} for more details).

.. _fig-scons-worklow:

.. figure:: workflow.png

    Deployment workflow using **SCons** :cite:`Kni05` and **AutoWIG** for generating *Python* bindings for *C++* libraries.
    The **SCons** workflow can be decomposed into $2$ steps: :code:`Deploy` and :code:`Compile`.
    In the :code:`Deploy` step, headers (denoted by :code:`*.h`) and source code  (denoted by :code:`*.cpp`) files are deployed in the filesystem according to developer instructions given in SConscripts and SContructs files (denoted by :code:`*/SCons*`).
    In the :code:`Compile` step, source code files are compiled to build libraries (denoted by :code:`*.so`).
    The integration of **AutoWIG** in **SCons** is made through the definition of a builder that takes deployed headers as input and uses **SCons** environment variables to drive the wrapping process.
    This leads to the generation of new source code files (i.e. wrappers) that will be compiled using **SCons** to product *Python* bindings for a *C++* library.
    Afterward, *Python* users can import the *C++* library in the *Python* interpreter.
    Red files represent files written by the *C++* developer.
    Blue files represent files generated by **AutoWIG**.


.. bibliography:: references.bib
