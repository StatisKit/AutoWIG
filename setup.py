##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (19)                       #
#                                                                                #
##################################################################################

import os
from setuptools import setup, find_packages

packages = {"" : "src" + os.sep + "py"}
for package in find_packages("src" + os.sep + "py"):
    packages[package] = "src" + os.sep + "py"

# from pkg.metadata import load_metadata
# metadata = load_metadata('.')	

setup(packages = packages.keys(),
      package_dir = {"" : "src" + os.sep + "py"},
      name = 'autowig',
      version = '1.0.0',
      author = 'Pierre Fernique',
      author_email = 'pfernique@gmail',
      description = '',
      long_description = '',
      license = 'CeCILL',
      package_data = {package: [ "*.so", "*.dll"] for package in packages},
      entry_points = {
        'autowig.parser': ['libclang = autowig.libclang_parser:libclang_parser'],
        'autowig.controller': ['default = autowig.default_controller:default_controller'],
        'autowig.generator': ['boost_python = autowig.boost_python_generator:boost_python_generator',
                              'boost_python_pattern = autowig.boost_python_generator:boost_python_pattern_generator',
                              'boost_python_internal = autowig.boost_python_generator:boost_python_internal_generator',
                              'boost_python_closure = autowig.boost_python_generator:boost_python_closure_generator'],
        'autowig.visitor': ['boost_python = autowig.boost_python_generator:boost_python_visitor',
                            'boost_python_closure = autowig.boost_python_generator:boost_python_closure_visitor',
                            'all = autowig.asg:all_visitor',
                            'free = autowig.asg:free_visitor',
                            'public = autowig.asg:public_visitor',
                            'protected = autowig.asg:protected_visitor',
                            'private = autowig.asg:private_visitor'],
        'autowig.feedback' : ['edit = autowig.edit_feedback:edit_feedback',
                              'comment = autowig.comment_feedback:comment_feedback'],
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


