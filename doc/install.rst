Currently, the installation of **AutoWIG** has only be tested on Ubuntu.
**AutoWIG** itself does not introduce particular difficulties for installation procedures on other operating systems since it is a pure *Python* package.
But, since the most effective wrapping process relies on the **PyCLangLite** library, difficulties arising from **LLVM**/**CLang** installation should be more investigated.

.. note::

    Wrappers generated with **AutoWIG** do not depend on **AutoWIG** and can be built on any operating system.

Installation from sources
=========================

Requirements
------------

To install AutoWIG, you need to install these dependencies:

**LLVM** and **Clang**
    The LLVM Project is a collection of modular and reusable compiler and toolchain technologies (http://llvm.org/).
    **Clang** is an "LLVM native" *C*/*C++*/*Objective-C* compiler,
    Sources of **LLVM** and **Clang** can be found on GitHub (respectively https://github.com/llvm-mirror/llvm.git and https://github.com/llvm-mirror/clang.git),

    .. warning::
        
        **PyClangLite** requires special compilation flags for both **LLVM** and **Clang** libraries.
        Refers to the documentation of **PyCLangLite** (http://PyClangLite.readthedocs.io/en/latest) to install these libraries.

**Zlib**
    This library (http://www.zlib.net/) is designed to be a free, general-purpose, legally unencumbered -- that is, not covered by any patents -- lossless data-compression library for use on virtually any computer hardware and operating system.
    This is a dependency of **LLVM**.

**Boost.Python**
    (https://github.com/boostorg/python.git),

**Mako**
    (http://www.makotemplates.org/),

**PyClangLite**
    This library (http://PyClangLite.readthedocs.io/en/latest) contains **Boost.Python** wrappers for the **Clang** library.
    Since **AutoWIG** most effective wrapping process relies on the **PyCLangLite** library, we highly recommand to install it.
    Nevertheless, this dependency is optional.

.. code-block:: console

    $ git clone https://github.com/VirtualPlants/AutoWIG.git
    $ cd AutoWIG


There are two installation mode that can be considered considering your usage of **AutoWIG**:

User installation
    If you don't want to contribute to **AutoWIG** but only use it to generate wrappers, we recommand a system installation.

    .. code-block:: console

        $ sudo python setup.py install
        $ cd ..
        $ sudo rm -rf AutoWIG

Developper installation 
    If you do want to contribute to **AutoWIG** and also use it to generate wrappers, we recommand a local installation.

    .. code-block:: console

        $ python setup.py develop --user
