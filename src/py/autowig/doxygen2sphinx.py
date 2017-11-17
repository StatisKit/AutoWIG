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

from mako.template import Template
import pypandoc
import re

from .asg import (ClassTemplateSpecializationProxy,
                  EnumeratorProxy,
                  ClassProxy,
                  FieldProxy,
                  FundamentalTypeProxy,
                  VariableProxy,
                  MethodProxy,
                  NamespaceProxy,
                  TypedefProxy,
                  EnumerationProxy,
                  FunctionProxy,
                  ConstructorProxy)
                  
from ._node_rename import node_rename

FORMATTER = Template(text=r"""\
% if brief:
${brief}

% endif
% if details:
${details}

% endif
% if len(param) == 1:
:Parameter:
    `${param[0][0]}` (${param[0][1]}) - ${('\n' + ' ' * (len(param[0][0]) + len(param[0][1]) + 12)).join(param[0][2].splitlines())}

% elif len(param) > 1:
:Parameters:
    % for nparam, tparam, dparam in param:
  - `${nparam}` (${tparam}) - ${('\n' + ' ' * (len(nparam) + len(tparam) + 12)).join(dparam.splitlines())}
    % endfor

% endif
% if returns:
:Returns:
    ${'\n    '.join(returns.splitlines())}

% endif
% if return_type:
:Return Type:
    ${'\n    '.join(return_type.splitlines())}

% endif
% if len(throws) == 1:
:Raises:
    ${throws[0][0]} - ${('\n' + ' ' * (len(throws[0][0]) + 7)).join(throws[0][1].splitlines())}

% elif len(throws) > 1:
:Raises:
    % for tthrows, dthrows in throws:
  - ${tthrows} - ${('\n' + ' ' * (len(tthrows) + 7)).join(dthrows.splitlines())}
    % endfor

% endif
% for _note in note:
.. note::

    ${'\n    '.join(_note.splitlines())}

% endfor
% for _warning in warning:
.. warning::

    ${'\n    '.join(_warning.splitlines())}

% endfor
% for _see in see:
.. seealso::

    ${'\n    '.join(_see.splitlines())}

% endfor
% for _todo in todo:
.. todo::

    ${'\n    '.join(_todo.splitlines())}

% endfor""")

def doxygen2sphinx_documenter(node, mako=True):
    try:
        doc = sphinx_formatter(**doxygen_parser(node))
        if mako:
            return doc.replace('\n', '\\n').replace('\\', '\\\\').replace('\\\\n', '\\n')
        else:
            return doc
    except:
        return ""

def doxygen_parser(node):
    """
    """

    comment = node.comment
    fmtargs = dict(brief = None,
            details = None,
            see = [],
            note = [],
            warning = [],
            param = dict(),
            todo = [],
            returns = None,
            return_type = None,
            throws = [])

    lines = []
    if (comment.startswith('/**') or comment.startswith('/*!')) and comment.endswith('*/'):
        comment = comment[3:-2].splitlines()
        comment[0].strip('*')
        if comment[0].isspace():
            comment.pop(0)
        comment[-1].strip('*')
        if comment[-1].isspace():
            comment.pop(-1)
        lines = [line.strip(' * ') for line in comment]
    elif comment.startswith('/// '):
        lines = [line.strip('/// ') for line in comment.splitlines()]
    elif comment.startswith('//! '):
        lines = [line.strip('//! ') for line in comment.splitlines()]
    else:
        raise ValueError('\'node\' parameter: attribute \'comment\' not formatted as expected')
    curr = 0
    asg = node._asg
    while curr < len(lines):
        if lines[curr].startswith(r'\brief'):
            if not fmtargs['brief']:
                prev, curr = desc_boundary(curr, lines)
                fmtargs['brief'] = extract_desc('brief', prev, curr, lines, asg)
            else:
                raise ValueError('\'comment\' parameter not formatted as expected')
        elif lines[curr].startswith(r'\details'):
            if not fmtargs['details']:
                prev, curr = desc_boundary(curr, lines)
                fmtargs['details'] = extract_desc('details', prev, curr, lines, asg)
            else:
                raise ValueError('\'comment\' parameter not formatted as expected')
        elif lines[curr].startswith(r'\warning'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['warning'].append(extract_desc('warning', prev, curr, lines, asg))
        elif lines[curr].startswith(r'\see'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['see'].append(extract_desc('see', prev, curr, lines, asg))
        elif lines[curr].startswith(r'\param'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['param'].__setitem__(*extract_named_desc('param', prev, curr, lines, asg))
        elif lines[curr].startswith(r'\throws'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['throws'].append(extract_named_desc('throws', prev, curr, lines, asg))
        elif lines[curr].startswith(r'\returns'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['returns'] = extract_desc('returns', prev, curr, lines, asg)
        elif lines[curr].startswith(r'\note'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['note'].append(extract_desc('note', prev, curr, lines, asg))
        elif lines[curr].startswith(r'\todo'):
            prev, curr = desc_boundary(curr, lines)
            fmtargs['todo'].append(extract_desc('todo', prev, curr, lines, asg))
        else:
            curr += 1
    fmtargs['throws'] = [(desc_converter(desc_parser(asg, r'\ref '+ cls)), desc) for cls, desc in fmtargs['throws']]
    if isinstance(node, FunctionProxy):
        fmtargs['return_type'] = desc_converter(desc_parser(asg, r'\ref ' + link_formatter(node.return_type.desugared_type.unqualified_type)))
    if isinstance(node, (ConstructorProxy, FunctionProxy)):
        fmtargs['param'] = [(parameter.localname, desc_converter(desc_parser(asg, r'\ref ' + link_formatter(parameter.qualified_type.desugared_type.unqualified_type))), fmtargs['param'].get(parameter.localname, 'Undocumented')) for parameter in node.parameters]
    return fmtargs

def sphinx_formatter(**kwargs):
    return FORMATTER.render_unicode(**kwargs)

def desc_parser(asg, text):
    text = text.replace(r'\f$', '$').replace(r'\f[', '$$').replace(r'\f]', '$$')
    desc = ''
    curr = 0
    while curr < len(text):
        if text[curr:curr+3] == r'\f{':
            curr += 3
            prev = curr
            while not text[curr] == '}':
                curr += 1
            env = text[prev:curr]
            curr += 1
            if text[curr] == '{':
                curr += 1
            prev = curr
            while curr < len(text) and not text[curr:curr+3] == r'\f}':
                curr += 1
            if text[curr:curr+3] == r'\f}':
                desc += r'\begin{' + env + '}' + text[prev:curr] + r'\end{' + env + '}'
                curr += 4
        elif text[curr:curr+9] == r'\parblock':
            curr += 9
        elif text[curr:curr+12] == r'\endparblock':
            curr += 12
        elif text[curr:curr+5] == r'\cite':
            curr += 5
            prev = curr
            while curr < len(text) and text[curr].isspace():
                curr += 1
            prev = curr
            while curr < len(text) and not text[curr].isspace():
                curr += 1
            while curr > prev and text[curr] in [')', '.', ']']:
                curr -= 1
            desc += '~~:cite:`' + text[prev:curr] + '`~~'
        elif text[curr:curr+4] == r'\ref':
            curr += 4
            prev = curr
            while curr < len(text) and text[curr].isspace():
                curr += 1
            prev = curr
            while curr < len(text) and not text[curr].isspace():
                curr += 1
            while curr > prev and text[curr-1] in [')', '.', ']']:
                curr -= 1
            node = text[prev:curr]
            if node in asg:
                node = asg[node]
            elif 'class ' + node in asg:
                node = asg['class ' + node]
            elif 'struct ' + node in asg:
                node = asg['struct ' + node]
            elif 'union ' + node in asg:
                node = asg['union ' + node]
            elif 'enum ' + node in asg:
                node = asg['enum ' + node]
            else:
                nodes = asg.nodes(node + '::[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')
                if len(nodes) > 0:
                    if any(node.boost_python_export and node.boost_python_export is not True for node in nodes):
                        node = [node for node in nodes if node.boost_python_export and node.boost_python_export is not True]
                    node = nodes.pop()
                else:
                    node = ':cpp:any:`' + node + '`'
            if not isinstance(node, basestring):
                node = name_formatter(node)
            desc += '~~' + node + '~~'
        else:
            desc += text[curr]
            curr += 1
    return desc

def desc_boundary(curr, lines):
    prev = curr
    curr += 1
    while curr < len(lines) and (not lines[curr].startswith('\\') or lines[curr].startswith('\\f') or lines[curr].startswith('\\ref')):
        curr += 1
    return prev, curr

def extract_desc(cmd, prev, curr, lines, asg):
    lines = lines[prev:curr]
    if len(lines) > 0:
        lines[0] = ' ' * (len(cmd) + 1) + lines[0][len(cmd)+1:]
        if len(lines) > 1:
            trim = float("inf")
            for line in lines:
                if line:
                    trim = min(trim, trimming(line))
            if trim > 0:
                return desc_converter(desc_parser(asg, '\n'.join(line[trim:] for line in lines)).strip())
            else:
                return desc_converter(desc_parser(asg, '\n'.join(lines)).strip())
        else:
            return desc_converter(desc_parser(asg, lines[0]).strip())

def extract_named_desc(cmd, prev, curr, lines, asg):
    lines = lines[prev:curr]
    if len(lines) > 0:
        ncmd = str(cmd)
        while lines[0][len(ncmd)+1].isspace():
            ncmd += ' '
        while not lines[0][len(ncmd)+1].isspace():
            ncmd += lines[0][len(ncmd)+1]
        return ncmd.lstrip(cmd).strip(), extract_desc(ncmd, 0, curr-prev, lines, asg)
    else:
        return None, None

def trimming(line):
    index = 0
    while index < len(line) and line[index].isspace():
        index += 1
    return index

def link_formatter(node):
    globalname = node.globalname
    if globalname.startswith('class '):
        return globalname[len('class '):]
    elif globalname.startswith('struct '):
        return globalname[len('struct '):]
    elif globalname.startswith('union '):
        return globalname[len('union '):]
    elif globalname.startswith('enum '):
        return globalname[len('enum '):]
    else:
        return globalname

def name_formatter(node):
    if isinstance(node, ClassTemplateSpecializationProxy):
        while node.is_smart_pointer:
            node = node.templates[0].desugared_type.unqualified_type
    elif isinstance(node, TypedefProxy):
        node = node.qualified_type.desugared_type.unqualified_type
    if node.boost_python_export and node.boost_python_export is not True:
        decorator = node.boost_python_export.module.decorator
        parent = node.parent
        name = '`' + decorator.package + '.' + '.'.join(node_rename(ancestor, scope=True) for ancestor in parent.ancestors[1:])
        if parent.globalname == '::':
            name += node_rename(node) + '`'
        elif parent.parent.globalname == '::':
            name += node_rename(parent) + '.' + node_rename(node) + '`'
        else:
            name += '.' + node_rename(parent) + '.' + node_rename(node) + '`'
        if isinstance(node, NamespaceProxy):
            name = ':py:mod:' + name
        elif isinstance(node, MethodProxy):
            name = ':py:meth:' + name
        elif isinstance(node, FunctionProxy):
            name = ':py:func:' + name
        elif isinstance(node, FieldProxy):
            name = ':py:attr:' + name
        elif isinstance(node, VariableProxy):
            name = ':py:data:' + name
        elif isinstance(node, EnumeratorProxy):
            name = ':py:const:' + name
        elif isinstance(node, ClassProxy):
            if node.is_error:
                name = ':py:exc:' + name
            else:
                name = ':py:class:' + name
        else:
            name = ':py:obj:' + name
    elif not isinstance(node, FundamentalTypeProxy):
        name = '`' + link_formatter(node) + '`'
        if isinstance(node, FunctionProxy):
            name = ':cpp:func:' + name
        elif isinstance(node,  VariableProxy):
            name = ':cpp:var:' + name
        elif isinstance(node, EnumeratorProxy):
            name = ':cpp:enumerator:' + name
        elif isinstance(node, EnumerationProxy):
            name = ':cpp:enumerator:' + name
        elif isinstance(node, ClassProxy):
            name = ':cpp:class:' + name
        else:
            name = ':cpp:any:' + name
    else:
        name = ':cpp:any:' + node.localname
    return name

def desc_converter(desc):
    desc = pypandoc.convert(desc, to='rst', format='markdown')
    return re.sub(r'\[STRIKEOUT:(\:.*)\:``(.*)``\]', r'\1:`\2`', desc).rstrip().replace(r'"', "'")

