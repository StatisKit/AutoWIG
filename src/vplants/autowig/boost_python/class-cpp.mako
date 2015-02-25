/** This file was automaticaly generated using VPlants.AutoWIG package
 * 
 * @warning Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
 * */
 
#include <boost/python.hpp>
#include <${model.file.replace('./src/cpp', library)}>
<%namespace file='/tools-py.mako' import='method_spelling'/>\
% for m in model.overloaded_methods:
    % for i, j in enumerate(m):
${j.output._repr_interface_()} (${model.scope}${model.spelling}::*${j.spelling}_${i})(${", ".join(k.type._repr_interface_() for k in j.inputs)}) = \
        % if not j.static:
&\
        % endif
(${model.scope}${model.spelling}::${j.spelling};
    % endfor
% endfor

BOOST_PYTHON_MODULE(_${''.join('_' + char.lower() if char.isupper() else char for char in model.spelling).lstrip('_')})
{
    boost::python::class_< ${model.scope}${model.spelling}, \
    % if len(model.bases) > 0:
boost::python::bases< ${", ".join([i.spelling for i in model.bases])} >, \
    %endif
boost::shared_ptr< ${model.scope}${model.spelling} >\
    % if model.pure_virtual:
, boost::noncopyable\
    % endif
 >("${model.spelling}", boost::python::no_init)
    % if not model.pure_virtual:
        % for c in model.constructors:
            % if len(c.inputs) == 0:
        .def(boost::python::init<>())
            % else:
        .def(boost::python::init< ${", ".join(i.type._repr_interface_() for i in c.inputs)} >())
            % endif
        % endfor
    % endif
        % for m in model.methods:
            % if not m.pure_virtual:
        .def("${method_spelling(m)}", \
                % if not m.static:
&\
                % endif
${model.scope}${model.spelling}::${m.spelling})
            % endif
        % endfor
        % for m in model.overloaded_methods:
            % for i, j in enumerate(m):
        .def("${j.spelling}", ${j.spelling}_${i})
            % endfor
        % endfor
        ;
    % for i in model.bases:
    boost::python::implicitly_convertible< boost::shared_ptr< ${model.scope}${model.spelling} >, boost::shared_ptr< ${i.spelling} > >();
% endfor
}

void init_bindings()
{
    Py_Initialize();
    init_${''.join('_' + char.lower() if char.isupper() else char for char in model.spelling).lstrip('_')}();
}
