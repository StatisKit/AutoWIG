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
## file except in compliance with the License.You should have received a ##
## copy of the Apache License, Version 2.0 along with this file; see the ##
## file LICENSE. If not, you may obtain a copy of the License at         ##
##                                                                       ##
##     http://www.apache.org/licenses/LICENSE-2.0                        ##
##                                                                       ##
## Unless required by applicable law or agreed to in writing, software   ##
## distributed under the License is distributed on an "AS IS" BASIS,     ##
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or       ##
## mplied. See the License for the specific language governing           ##
## permissions and limitations under the License.                        ##

import autowig

import unittest
from nose.plugins.attrib import attr

import os
import sys
from path import Path
from git import Repo
import subprocess
import shutil
import platform
import six

@attr(win=True,
      linux=True,
      osx=True,
      level=1)
class TestBasic(unittest.TestCase):
    """Test the wrapping of a basic library"""

    @classmethod
    def setUpClass(cls):
        if 'libclang' in autowig.parser:
            autowig.parser.plugin = 'libclang'
        autowig.generator.plugin = 'boost_python_internal'
        cls.srcdir = Path('fp17')
        cls.prefix = Path(Path(sys.prefix).abspath())
        if any(platform.win32_ver()):
            cls.prefix = cls.prefix/'Library'
        Repo.clone_from('https://github.com/StatisKit/FP17.git', cls.srcdir.relpath('.'))
        if any(platform.win32_ver()):
            cls.scons = subprocess.check_output(['where', 'scons.bat']).strip()
        else:
            cls.scons = subprocess.check_output(['which', 'scons']).strip()
        if six.PY3:
            cls.scons = cls.scons.decode("ascii", "ignore")
        subprocess.check_output([cls.scons, 'cpp', '--prefix=' + str(cls.prefix)],
                                cwd=cls.srcdir)
        cls.incdir = cls.prefix/'include'/'basic'

    def test_mapping_export(self):
        """Test `mapping` export"""

        subprocess.check_call([self.scons, 'cpp', '--prefix=' + self.prefix],
                              cwd=self.srcdir)

        asg = autowig.AbstractSemanticGraph()

        if autowig.parser.plugin == 'libclang':
            kwargs = dict(silent = True)
        else:
            kwargs = dict()

        asg = autowig.parser(asg, self.incdir.files('*.h'),
                                  flags = ['-x', 'c++', '-std=c++11', '-I' + str(self.incdir.parent)],
                                  **kwargs)

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        wrappers = autowig.generator(asg, module = self.srcdir/'src'/'py'/'__basic.cpp',
                                        decorator = self.srcdir/'src'/'py'/'basic'/'_basic.py',
                                        prefix = 'wrapper_')
        wrappers.write()
        
        subprocess.check_call([self.scons, 'py', '--prefix=' + self.prefix],
                              cwd=self.srcdir)

        for filepath in (self.srcdir/'src'/'py').walkfiles():
            if filepath.exists() and filepath.ext in ['.cpp', '.h']:
                filepath.remove()

    @attr(win=False)
    def test_pyclanglite_parser(self):
        """Test `pyclanglite` parser"""
        plugin = autowig.parser.plugin
        autowig.parser.plugin = 'clanglite'
        self.test_mapping_export()
        autowig.parser.plugin = plugin

    def test_boost_python_pattern_generator(self):
        """Test `boost_python_pattern` generator"""
        plugin = autowig.generator.plugin
        autowig.generator.plugin = 'boost_python_pattern'
        self.test_mapping_export()
        autowig.generator.plugin = plugin
