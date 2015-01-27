/** This file was automaticaly generated using VPlants.AutoWIG package
 * 
 * @warning Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
 * */
 
#include <boost/python.hpp>
#include <${model.file}>

using namespace boost::python;

% for m in model.overloaded_methods:
    % for i, j in enumerate(m):
${j.output.spelling} (${model.scope}${model.spelling}::*${j.spelling}_${i})(${", ".join([k.type.spelling if not k.const else 'const '+k.type.spelling for k in j.inputs])}) = \
        % if not j.static:
&\
        % endif
(${model.scope}${model.spelling}::${j.spelling};
    % endfor
% endfor

BOOST_PYTHON_MODULE(_${''.join('_' + char.lower() if char.isupper() else char for char in model.spelling).lstrip('_')})
{
    class_< ${model.scope}${model.spelling}, \
    % if len(model.bases) > 0:
bases< ${", ".join([i.spelling for i in model.bases])} >, \
    %endif
boost::shared_ptr< ${model.scope}${model.spelling} >\
    % if model.pure_virtual:
, boost::noncopyable\
    % endif
 >("${model.spelling}", no_init)
    % if not model.pure_virtual:
        % for c in model.constructors:
            % if len(c.inputs) > 0:
        .def(init< ${", ".join([i.type.spelling if not i.const else "const "+i.type.spelling for i in c.inputs])} >())
            % else:
        .def(init<>())
            % endif
        % endfor
    % endif
        % for m in model.methods:
        .def("${m.spelling}", \
            % if not m.static:
&\
            % endif
${model.scope}::${model.spelling}::${m.spelling})
        % endfor
        % for m in model.overloaded_methods:
            % for i, j in enumerate(m):
        .def("${j.spelling}", ${j.spelling}_${i})
            % endfor
        % endfor
        ;
    % for i in model.bases:
    implicitly_convertible< boost::shared_ptr< ${model.scope}${model.spelling} >, boost::shared_ptr< ${i.spelling} > >();
% endfor
}

void init_bindings()
{
    Py_Initialize();
    init_${''.join('_' + char.lower() if char.isupper() else char for char in model.spelling).lstrip('_')}();
}
