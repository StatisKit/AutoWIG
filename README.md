# AutoWIG

AutoWIG (Automatic Wrapper and Interface Generator) is an automatic wrapper generator for C/C++ libraries written in Python and based on LLVM/Clang. It generates Boost.Python code for C/C++ enumerations, variables, functions, C structures and C++ classes in order to provide Python bindings for C/C++ libraries. The main features of AutoWIG are the automatic construction of Abstract Semantic Graphs (ASGs) in Python from Abstract Syntax Trees (ASTs) given by LLVM/Clang and the versatile generation of Python bindings using the Python Mako templating engine.

## Documentation

Official documentation is available at [virtualplants.github.io](http://virtualplants.github.io)

## Install

To install VPlants.AutoWIG, you need to install these dependencies:
  - LLVM (https://github.com/llvm-mirror/llvm.git),
  - Clang (https://github.com/llvm-mirror/clang.git),
  - Zlib (http://www.zlib.net/),
  - Boost.Python (https://github.com/boostorg/python.git),
  - Mako Templates (http://www.makotemplates.org/),

But it is also highly recommended to install
  - PyClangLite (https://github.com/VirtualPlants/PyClangLite.git)
  - IPython (http://ipython.org/)
  - Jupyter  (http://jupyter.readthedocs.org/en/latest/index.html)

We here assume that you already installed LLVM, Clang, Zlib, Boost.Python and PyClangLite according to the installation procedure described in the PyClangLite [README.md](https://github.com/VirtualPlants/PyClangLite.git).

```
sudo apt-get install python-mako python-pip
pip install -U ipython
pip install -U jupyter
git clone https://github.com/pfernique/AutoWIG.git
cd AutoWIG
sudo python setup.py install
cd ..
sudo rm -rf AutoWIG
```

You will probably need to copy the Clang python bindings (libclang) into your Python library directory or change your PYTHONPATH.

## Contribute

If you want to contribute, please have a look to the [github workflow](http://virtualplants.github.io/contribute/devel/git-workflow.html)
