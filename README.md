# VPlants.AutoWIG

## Documentation

Official documentation is available at [virtualplants.github.io](http://virtualplants.github.io)

## Install

To install VPlants.AutoWIG, you need to install these dependencies:
  - LLVM (http://llvm.org/git/llvm),
  - Clang (https://github.com/llvm-mirror/clang.git),
  - Boost.Python (https://github.com/boostorg/python).
  
In particular to install LLVM and Clang, you can clone this [personal repository](https://github.com/pfernique/llvm) where Clang is added as a submodule of LLVM.
Therefore you only need to follow instructions on the *Getting Started page of LLVM* (http://llvm.org/docs/GettingStarted.html) to install both LLVM and Clang.
You will probably need to copy the Clang python bindings (libclang) into your Python library directory or change your PYTHONPATH.

- PyClangLite (https://github.com/pfernique/pyclanglite)

Additional softwares can be installed
  - asciitree (https://github.com/mbr/asciitree)
  - ipython

## Contribute

If you want to contribute to code, please have a look to [github workflow](http://virtualplants.github.io/contribute/devel/git-workflow.html)
