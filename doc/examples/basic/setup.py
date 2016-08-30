import os
from setuptools import setup, find_packages

packages = {"" : "src" + os.sep + "py"}
for package in find_packages("src" + os.sep + "py"):
    packages[package] = "src" + os.sep + "py"

setup(packages = packages.keys(),
      package_dir = {"" : "src" + os.sep + "py"},
      name = 'basic',
      version = '1.0.0',
      author = 'Pierre Fernique',
      author_email = 'pfernique@gmail.com',
      description = 'A basic library',
      long_description = 'This library is designed to be an example for AutoWIG',
      license = 'none',
      package_data = {package: [ "*.so", "*.dll"] for package in packages},
      zip_safe = False)


