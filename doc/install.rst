Currently, the installation of **AutoWIG** has only be tested on Ubuntu.
**AutoWIG** itself does not introduce particular difficulties for installation procedures on other operating systems since it is a pure *Python* package.
But, since the most effective wrapping process relies on the **PyCLangLite** library, difficulties arising from **LLVM**/**CLang** installation should be more investigated.

.. note::

    Wrappers generated with **AutoWIG** do not depend on **AutoWIG** and can be built on any operating system.

Dependencies
============

To install AutoWIG, you need to install these dependencies:

**LLVM** and **Clang**
    (https://github.com/llvm-mirror/llvm.git) and **Clang** (https://github.com/llvm-mirror/clang.git),

**Zlib**
    (http://www.zlib.net/),

**Boost.Python**
    (https://github.com/boostorg/python.git),

**Mako**
    (http://www.makotemplates.org/),

**PyClangLite**
    Since the most effective wrapping process relies on the **PyCLangLite** library, we highly recommand to install

AutoWIG
=======

Installation from sources:

.. code-block:: console

    $ git clone https://github.com/VirtualPlants/AutoWIG.git
    $ cd AutoWIG


There are two installation mode that can be considered considering your usage of **AutoWIG**:

User installation
    If you don't want to contribute to **AutoWIG** but only use it to generate wrappers, we recommand a system installation.

    .. code-block:: console

        $ git clone https://github.com/VirtualPlants/AutoWIG.git
        $ cd AutoWIG


.. code-block:: console

    $ sudo python setup.py install
    $ cd ..
    $ sudo rm -rf AutoWIG

 
Developper installation
-----------------------

.. code-block:: console

    $ python setup.py develop --user
