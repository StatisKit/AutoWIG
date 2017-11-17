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

from .plugin import PluginManager

from .tools import camel_case_to_lower, to_camel_case, camel_case_to_upper
from .asg import (FunctionProxy,
                  VariableProxy,
                  EnumerationProxy,
                  EnumeratorProxy,
                  ClassTemplateSpecializationProxy,
                  ClassTemplateProxy,
                  ClassProxy,
                  NamespaceProxy,
                  TypedefProxy)

__all__ = []

node_rename = PluginManager('autowig.node_rename', brief="",
        details="")

PYTHON_OPERATOR = dict()
PYTHON_OPERATOR['+'] = '__add__'
PYTHON_OPERATOR['++'] = '__next__'
PYTHON_OPERATOR['-'] = '__sub__'
PYTHON_OPERATOR['--'] = '__prev__'
PYTHON_OPERATOR['*'] = '__mul__'
PYTHON_OPERATOR['/'] = '__div__'
PYTHON_OPERATOR['%'] = '__mod__'
PYTHON_OPERATOR['=='] = '__eq__'
PYTHON_OPERATOR['!='] = '__neq__'
PYTHON_OPERATOR['>'] = '__gt__'
PYTHON_OPERATOR['<'] = '__lt__'
PYTHON_OPERATOR['>='] = '__ge__'
PYTHON_OPERATOR['<='] = '__le__'
PYTHON_OPERATOR['!'] = '__not__'
PYTHON_OPERATOR['&&'] = '__and__'
PYTHON_OPERATOR['||'] = '__or__'
PYTHON_OPERATOR['~'] = '__invert__'
PYTHON_OPERATOR['&'] = '__and__'
PYTHON_OPERATOR['|'] = '__or__'
PYTHON_OPERATOR['^'] = '__xor__'
PYTHON_OPERATOR['<<'] = '__lshift__'
PYTHON_OPERATOR['>>'] = '__rshift__'
PYTHON_OPERATOR['+='] = '__iadd__'
PYTHON_OPERATOR['-='] = '__isub__'
PYTHON_OPERATOR['*='] = '__imul__'
PYTHON_OPERATOR['%='] = '__idiv__'
PYTHON_OPERATOR['&='] = '__iand__'
PYTHON_OPERATOR['|='] = '__ior__'
PYTHON_OPERATOR['^='] = '__ixor__'
PYTHON_OPERATOR['<<='] = '__ilshift__'
PYTHON_OPERATOR['>>='] = '__irshift__'
PYTHON_OPERATOR['()'] = '__call__'
PYTHON_OPERATOR['[]'] = '__getitem__'

PYTHON_FUNCTION = dict()
PYTHON_FUNCTION['generator'] = '__iter__'
PYTHON_FUNCTION['size'] = '__len__'

def pep8_node_rename(node, scope=False):
    if isinstance(node, FunctionProxy) and node.localname.startswith('operator'):
        return PYTHON_OPERATOR[node.localname.strip('operator').strip()]
    elif isinstance(node, FunctionProxy):
        if node.localname in PYTHON_FUNCTION:
            return PYTHON_FUNCTION[node.localname]
        else:
            return camel_case_to_lower(node.localname)
    elif isinstance(node, VariableProxy):
        return camel_case_to_lower(node.localname)
    elif isinstance(node, EnumerationProxy):
        return camel_case_to_lower(node.localname)
    elif isinstance(node, EnumeratorProxy):
        return camel_case_to_upper(node.localname)
    elif isinstance(node, ClassTemplateSpecializationProxy):
        if not scope:
            return '_' + to_camel_case(node.specialize.localname).strip('_') + '_' + node.hash
        else:
            return '__' + camel_case_to_lower(node.specialize.localname).strip('_') + '_' + node.hash
    elif isinstance(node, TypedefProxy):
        return to_camel_case(node.localname)
    elif isinstance(node, (ClassTemplateProxy, ClassProxy)):
        if scope:
            return '_' + camel_case_to_lower(node.localname).strip('_')
        elif isinstance(node, ClassProxy):
            return to_camel_case(node.localname)
        else:
            return '_' + to_camel_case(node.localname)
    elif isinstance(node, NamespaceProxy):
        return camel_case_to_lower(node.localname)
    else:
        return NotImplementedError(node.__class__)
