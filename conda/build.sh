# Build python-clang recipe
conda build conda/python-clang -c statiskit
conda install python-clang --use-local -c statiskit 

# Build python-autowig recipe
conda build conda/python-autowig -c statiskit -c conda-forge
conda install python-autowig --use-local -c statiskit -c conda-forge
conda remove python-autowig
conda install python-scons -c statiskit
scons py
pip install -e .
