"""This file was automaticaly generated using VPlants.AutoWIG package

.. warning:: Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
"""

<% imported = set() %>\
<%namespace file='/tools-py.mako' import='write_import, write_inputs'/>\
${write_import(library, [i.type for i in model.inputs], imported)}\

from _${model.spelling} import ${model.spelling}
from functools import wraps
import collections

def wrapper(f):
    @wraps(f)
    def ${model.spelling}(${write_inputs(library, 2, model.inputs)}\
        % if not model.output.spelling == 'void':
        return f(${', '.join(i.spelling for i in model.inputs)})
        % else:
        f(${', '.join(i.spelling for i in model.inputs)})
        % endif
    return ${model.spelling}

${model.spelling} = wrapper(${model.spelling})
del wrapper

del wraps
