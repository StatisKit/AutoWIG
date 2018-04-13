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

import os
import parse
from path import Path

from .plugin import PluginManager

feedback = PluginManager('autowig.feedback', brief="",
        details="""""")

def parse_errors(err, directory, asg, **kwargs):
    if not isinstance(err, str):
        raise TypeError('\'err\' parameter')
    if not isinstance(directory, Path):
        directory = Path(directory)
    variant_dir = kwargs.pop('variant_dir', None)
    if variant_dir:
        variant_dir = directory/variant_dir
    else:
        variant_dir = directory
    src_dir = kwargs.pop('src_dir', None)
    if src_dir:
        src_dir = directory/src_dir
    else:
        src_dir = directory
    indent = kwargs.pop('indent', 0)
    src_dir = str(src_dir.abspath()) + os.sep
    variant_dir = str(variant_dir.relpath(directory))
    if variant_dir == '.':
        variant_dir = ''
    else:
        variant_dir += os.sep
    wrappers = dict()
    for line in err.splitlines():
        parsed = parse.parse(variant_dir+'{filename}:{row}:{column}:{message}', line)
        if parsed:
            try:
                row = int(parsed['row'])
                node = src_dir + parsed['filename']
                if node in asg:
                    if node not in wrappers:
                        wrappers[node] = [row]
                    else:
                        wrappers[node].append(row)
            except:
                pass
    return wrappers