<%def name="write_import(library, model)">\
<% import re %>\
% for i in [j.type.spelling.replace('const', '').replace('&', '').replace('*', '').replace(' ', '') for j in model.inputs]:
    % if re.match(library+r'::(.*)', i):
from ${'.'.join([''.join('_' + c.lower() if c.isupper() else c for c in j).lstrip('_') for j in i.split('::')[:-1]])} import ${'_'+''.join('_' + c.lower() if c.isupper() else c for c in i.rsplit('::', -1)[-1]).lstrip('_').replace(' ', '_')}
    % endif
% endfor
</%def>\

<%def name="write_test(library, indent, argtype, argname)">\
<%import re %>\
% if argtype in ['unsignedint', 'int']:
${"    "*indent}if not isinstance(${argname}, int):
${"    "*indent}    raise TypeError('`${argname}` parameter')
% elif argtype == 'double':
${"    "*indent}if not isinstance(${argname}, float):
${"    "*indent}    raise TypeError('`${argname}` parameter')
% elif re.match(r'std::(.*)', argtype):
    % if argtype == 'std::string':
${"    "*indent}if not isinstance(${argname}, string):
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

<%def name="write_inputs(library, indent, inputs)">\
${', '.join([i.spelling for i in inputs])}):
% for i in inputs:
<%self:write_test library="${library}" indent="${indent}" argtype="${i.type.spelling.replace('const', '').replace('&', '').replace('*', '').replace(' ', '')}" argname="${i.spelling}">\
\
</%self:write_test>\
% endfor
</%def>\
