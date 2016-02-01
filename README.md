# VPlants.AutoWIG

## Documentation

Official documentation is available at [virtualplants.github.io](http://virtualplants.github.io)

## Install

To install VPlants.AutoWIG, you need to install these dependencies:
  - LLVM (https://github.com/llvm-mirror/llvm.git),
  - Clang (https://github.com/llvm-mirror/clang.git),
  - Zlib (http://www.zlib.net/),
  - Boost.Python (https://github.com/boostorg/python.git),
  - Mako Templates (http://www.makotemplates.org/),
  - OpenAlea.OpenAlea (https://github.com/openalea/openalea.git)
  
But it is also highly recommended to install
  - PyClangLite (https://github.com/VirtualPlants/PyClangLite.git)
  - IPython (http://ipython.org/)
  - Jupyter  (http://jupyter.readthedocs.org/en/latest/index.html)

We here assume that you already installed LLVM, Clang, Zlib, Boost.Python and PyClangLite according to the installation procedure described in the PyClangLite [README.md](https://github.com/VirtualPlants/PyClangLite.git).

```
sudo apt-get install python-mako python-pip
git clone git@github.com:openalea/openalea.git
cd openalea 
python multisetup.py install --user
pip install -U ipython
pip install -U jupyter
git clone git@github.com:VirtualPlants/AutoWIG.git
```

You will probably need to copy the Clang python bindings (libclang) into your Python library directory or change your PYTHONPATH.

## Contribute

If you want to contribute, please have a look to the [github workflow](http://virtualplants.github.io/contribute/devel/git-workflow.html)
