## Copyright [2017-2018] UMR MISTEA INRA, UMR LEPSE INRA,                ##
##                       UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
## Copyright [2015-2016] UMR AGAP CIRAD, EPI Virtual Plants Inria        ##
##                                                                       ##
## This file is part of the AutoWIG project. More information can be     ##
## found at                                                              ##
##                                                                       ##
##     http://autowig.rtfd.io                                            ##
##                                                                       ##
## The Apache Software Foundation (ASF) licenses this file to you under  ##
## the Apache License, Version 2.0 (the "License"); you may not use this ##
## file except in compliance with the License. You should have received  ##
## a copy of the Apache License, Version 2.0 along with this file; see   ##
## the file LICENSE. If not, you may obtain a copy of the License at     ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

import six
import os
from setuptools import setup, find_packages

packages = {"" : "src" + os.sep + "py"}
for package in find_packages("src" + os.sep + "py"):
    packages[package] = "src" + os.sep + "py"

setup(packages = packages.keys(),
      package_dir = {"" : "src" + os.sep + "py"},
      name = 'autowig',
      version = '1.0.0',
      author = 'Pierre Fernique',
      author_email = 'pfernique@gmail',
      description = '',
      long_description = '',
      license = 'Apache License 2.0',
      package_data = {package: [ "*.so", "*.dll"] for package in packages},
      entry_points = {
        'autowig.parser': [],
        'autowig.controller': ['default = autowig.default_controller:default_controller'],
        'autowig.generator': ['boost_python = autowig.boost_python_generator:boost_python_generator',
                              'boost_python_pattern = autowig.boost_python_generator:boost_python_pattern_generator',
                              'boost_python_internal = autowig.boost_python_generator:boost_python_internal_generator',
                              'boost_python_closure = autowig.boost_python_generator:boost_python_closure_generator',
                              'pybind11 = autowig.pybind11_generator:pybind11_generator',
                              'pybind11_pattern = autowig.pybind11_generator:pybind11_pattern_generator',
                              'pybind11_internal = autowig.pybind11_generator:pybind11_internal_generator',
                              'pybind11_closure = autowig.pybind11_generator:pybind11_closure_generator'],
        'autowig.visitor': ['boost_python = autowig.boost_python_generator:boost_python_visitor',
                            'boost_python_closure = autowig.boost_python_generator:boost_python_closure_visitor',
                            'pybind11 = autowig.pybind11_generator:pybind11_visitor',
                            'pybind11_closure = autowig.pybind11_generator:pybind11_closure_visitor',
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
        'autowig.pybind11_call_policy': ['default = autowig.pybind11_generator:pybind11_default_call_policy'],
        'autowig.pybind11_export': ['default = autowig.pybind11_generator:PyBind11ExportFileProxy'],
        'autowig.pybind11_module': ['default = autowig.pybind11_generator:PyBind11ModuleFileProxy'],
        'autowig.pybind11_decorator': ['default = autowig.pybind11_generator:PyBind11DecoratorDefaultFileProxy'],
        'autowig.node_rename': ['PEP8 = autowig._node_rename:pep8_node_rename'],
        'autowig.documenter': ['doxygen2sphinx = autowig.doxygen2sphinx:doxygen2sphinx_documenter'],
        'autowig.node_path' : ['scope = autowig._node_path:scope_node_path',
                               'hash = autowig._node_path:hash_node_path'],
        'console_scripts': [],
        },
        zip_safe = False
    )


