# -*- coding: utf-8 -*-
__revision__ = "$Id: $"

import sys
import os

from setuptools import setup, find_packages

packages = {"" : "src"}
for package in find_packages("src"):
    packages[package] = ""
    
setup(
    name="AutoWIG",
    version="0.1.0",
    description="AUTOmatic Wrapper and Interface Generator package",
    long_description="",
    author="P. Fernique, C. Pradal",
    author_email="pierre.fernique@inria.fr, christophe.pradal@cirad.fr",
    url="autowig.readthedocs.org",
    license="CeCILL-C",
    keywords = '',

    # package installation
    packages= packages.keys(),
    package_dir=  {"" : "src"},

    # Namespace packages creation by deploy
    #namespace_packages = [namespace],
    #create_namespaces = False,
    zip_safe= False,

    # Dependencies
    setup_requires = setup_requires,
    install_requires = install_requires,
    dependency_links = dependency_links,

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data = True,
    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include
    #package_data = {'' : ['*.pyd', '*.so'],},

    # postinstall_scripts = ['',],

    # Declare scripts and wralea as entry_points (extensions) of your package
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
            'basic = autowig.boost_python_generator:BoostPythonExportBasicFileProxy',
            'mapping = autowig.boost_python_generator:BoostPythonExportMappingFileProxy'],
        'autowig.boost_python_module': ['default = autowig.boost_python_generator:BoostPythonModuleFileProxy'],
        'autowig.boost_python_decorator': ['default = autowig.boost_python_generator:BoostPythonDecoratorDefaultFileProxy'],
        'autowig.node_rename': ['PEP8 = autowig.node_rename:pep8_node_rename'],
        'autowig.documenter': ['doxygen2sphinx = autowig.doxygen2sphinx:doxygen2sphinx_documenter'],
        'autowig.node_path' : ['scope = autowig.node_path:scope_node_path',
            'hash = autowig.node_path:hash_node_path'],
        'console_scripts': [],
        # 'gui_scripts': [
        #      'fake_gui = openalea.fakepackage.amodule:gui_script',],
        #	'wralea': wralea_entry_points
        },
    )


