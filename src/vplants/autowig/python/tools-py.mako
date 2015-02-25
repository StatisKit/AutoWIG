<%def name="method_spelling(method)">\
% if method.spelling == 'operator()':
__call__\
% elif method.spelling == 'get_size':
__len__\
% else:
${method.spelling}\
% endif
</%def>

<%def name="write_import(library, objects, imported)">\
<% import re %>\
% for i in [o.spelling.replace('const', '').replace('&', '').replace('*', '').replace(' ', '') for o in objects]:
    % if re.match(library+r'::(.*)', i) and not i in imported:
from ${'.'.join([''.join('_' + c.lower() if c.isupper() else c for c in j) for j in i.split('::')])} import ${i.rsplit('::', -1)[-1]}
    <% imported.add(i) %>\
    % endif
% endfor
</%def>\

<%def name="write_test(library, indent, argtype, argname)">\
<%import re %>\
% if argtype in ['unsignedint', 'int']:
${"    "*indent}if not isinstance(${argname}, int):
${"    "*indent}    raise TypeError('`${argname}` parameter')
    % if argtype == 'unsignedint':
${"    "*indent}if not ${argname} > 0:
${"    "*indent}    raise ValueError('`${argname}` parameter')
    % endif
% elif argtype == 'double':
${"    "*indent}if not isinstance(${argname}, float):
${"    "*indent}    raise TypeError('`${argname}` parameter')
% elif re.match(r'std::(.*)', argtype):
    % if argtype == 'std::string':
${"    "*indent}if not isinstance(${argname}, str):
${"    "*indent}    raise TypeError('`${argname}` parameter')
    % elif re.match(r'std::vector<(.*)>', argtype):
${"    "*indent}if not isinstance(${argname}, collections.Sequence):
${"    "*indent}    raise TypeError('`${argname}` parameter')
${"    "*indent}try:
${"    "*indent}    for ${argname}_iter in ${argname}:<%self:write_test library="${library}" indent="${indent+2}" argtype="${re.split(r'std::vector<(.*)>', argtype)[1]}" argname="${argname}_iter)">\
        \
        </%self:write_test>\
${"    "*indent}except TypeError as error:
${"    "*indent}    error.msg = error.msg.replace('_iter', '', 1)
${"    "*indent}    raise error
    % endif
% elif re.match(library+r'::(.*)', argtype):
${"    "*indent}if not isinstance(${argname}, ${argtype.rpartition('::')[-1]}):
${"    "*indent}    raise TypeError('`${argname}` parameter')
% endif
</%def>\

<%def name="write_inputs(library, indent, inputs, args=False, kwargs=False)">\
${', '.join([i.spelling for i in inputs])}\
% if args:
    % if len(inputs) > 0:
, \
    % endif
*args\
% endif
% if kwargs:
    % if len(inputs) > 0 or args:
, \
    % endif
**kwargs\
% endif
):
% for i in inputs:
<%self:write_test library="${library}" indent="${indent}" argtype="${i.type.spelling.replace('const', '').replace('&', '').replace('*', '').replace(' ', '')}" argname="${i.spelling}">\
\
</%self:write_test>\
% endfor
</%def>\
