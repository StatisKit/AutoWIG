import os
from setuptools import setup, find_packages

packages = {"" : "src" + os.sep + "py"}
for package in find_packages("src" + os.sep + "py"):
    packages[package] = "src" + os.sep + "py"

try:
    from mngit.config import load_config
    config = load_config('.')
except:
    import os
    import yaml
    with open('.' + os.sep + '.mngit.yml', 'r') as filehandler:
        config = yaml.load(filehandler.read())

with open('README.rst', 'r') as filehandler:
    long_description = filehandler.read()

setup(packages = packages.keys(),
      package_dir = {"" : "src" + os.sep + "py"},
      name = config['about']['name'],
      version = config['about']['version'],
      author = config['about']['authors'],
      author_email = config['about']['email'],
      description = config['about']['brief'],
      long_description = long_description,
      license = config['license']['plugin'],
      package_data = {package: [ "*.so", "*.dll"] for package in packages},
      entry_points = {
        'autowig.parser': ['libclang = autowig.libclang_parser:libclang_parser'],
        'autowig.controller': ['default = autowig.default_controller:default_controller'],
        'autowig.generator': ['boost_python = autowig.boost_python_generator:boost_python_generator',
            'boost_python_pattern = autowig.boost_python_generator:boost_python_pattern_generator',
            'boost_python_internal = autowig.boost_python_generator:boost_python_internal_generator',
            'boost_python_closure = autowig.boost_python_generator:boost_python_closure_generator'],
        'autowig.visitor': ['boost_python = autowig.boost_python_generator:boost_python_visitor',
            'all = autowig.asg:all_visitor',
            'free = autowig.asg:free_visitor',
            'public = autowig.asg:public_visitor',
            'protected = autowig.asg:protected_visitor',
            'private = autowig.asg:private_visitor'],
        'autowig.feedback' : ['gcc-5 = autowig.gcc_feedback:gcc_5_feedback'],
        'autowig.boost_python_call_policy': ['default = autowig.boost_python_generator:boost_python_default_call_policy'],
        'autowig.boost_python_export': ['custom = autowig.boost_python_generator:BoostPythonExportFileProxy',
            'default = autowig.boost_python_generator:BoostPythonExportDefaultFileProxy'],
        'autowig.boost_python_module': ['default = autowig.boost_python_generator:BoostPythonModuleFileProxy'],
        'autowig.boost_python_decorator': ['default = autowig.boost_python_generator:BoostPythonDecoratorDefaultFileProxy'],
        'autowig.node_rename': ['PEP8 = autowig._node_rename:pep8_node_rename'],
        'autowig.documenter': ['doxygen2sphinx = autowig.doxygen2sphinx:doxygen2sphinx_documenter'],
        'autowig.node_path' : ['scope = autowig._node_path:scope_node_path',
            'hash = autowig._node_path:hash_node_path'],
        'console_scripts': [],
        },
        zip_safe = False
    )


