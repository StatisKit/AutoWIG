"""This file was automaticaly generated using VPlants.AutoWIG package

.. warning:: Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
"""

<% imported = set() %>\
<%namespace file='/tools-py.mako' import='write_import, write_inputs, method_spelling'/>\
${write_import(library, model.bases, imported)}\
% for c in model.constructors:
    ${write_import(library, [i.type for i in c.inputs], imported)}\
% endfor
% for m in model.methods:
    ${write_import(library, [i.type for i in m.inputs], imported)}\
% endfor
% for om in model.overloaded_methods:
    % for m in om:
        ${write_import(library, [i.type for i in m.inputs], imported)}\
    % endfor
% endfor

from _${''.join('_' + char.lower() if char.isupper() else char for char in model.spelling).lstrip('_')} import ${model.spelling}
from functools import wraps
import collections

% if len(model.constructors) == 1:
def wrapper(f):
    @wraps(f)
    def __init__(self, ${write_inputs(library, 2, model.constructors[0].inputs, kwargs=True)}\
        % if len(model.constructors[0].inputs) == 0:
        f(self)
        % else:
        f(self, ${', '.join(i.spelling for i in model.constructors[0].inputs)})
        % endif
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError('`'+key+'` parameter')
    return __init__

${model.spelling}.__init__ = wrapper(${model.spelling}.__init__)
del wrapper
% endif
% for m in model.methods:

    % if not m.pure_virtual:
def wrapper(f):
    @wraps(f)
    def ${method_spelling(m)}(\
        % if not m.static:
self\
            % if len(m.inputs) > 0:
, \
            % endif
        % endif
        % if len(m.inputs) > 0:
${write_inputs(library, 2, m.inputs)}\
        % else:
):
        %endif
        % if not m.output.spelling == 'void':
        return f(\
        % else:
        f(\
        % endif
        % if not m.static:
self\
            % if len(m.inputs) > 0:
, \
            % endif
        % endif
${', '.join(i.spelling for i in m.inputs)})
    return ${method_spelling(m)}

${model.spelling}.${method_spelling(m)} = wrapper(${model.spelling}.${method_spelling(m)})
del wrapper
    %endif
% endfor
% for f in model.fields:

getter = getattr(${model.spelling}, get_${f.spelling}, None)
if not getter is None:
    setter = getattr(${model.spelling}, set_${f.spelling}, None)
    ${model.spelling}.${f.spelling} = property(getter, setter)
    if not setter is None:
        del ${model.spelling}.set_${f.spelling}
    del ${model.spelling}.get_${f.spelling}, getter, setter
    % if f.type.spelling.replace('const', '').replace('&', '').replace(' ', '') == 'bool':
else:
    getter = getattr(${model.spelling}, is_${f.spelling}, None)
    if not getter is None:
        ${model.spelling}.${f.spelling} = property(getter)
        del ${model.spelling}.is_${f.spelling}, getter
    % endif
% endfor
\
del wraps
