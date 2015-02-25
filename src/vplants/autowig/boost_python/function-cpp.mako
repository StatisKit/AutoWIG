/** This file was automaticaly generated using VPlants.AutoWIG package
 * 
 * @warning Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
 * */
<%!
    from vplants.autowig.interface import InterfaceTypedefType, TypeRefInterfaceCursor, InterfaceLValueReferenceType, InterfacePointerType

    def get_return_value_policy(output):
        if isinstance(output, (InterfaceTypedefType, TypeRefInterfaceCursor)):
            return get_return_value_policy(output.type)
        elif isinstance(output, InterfaceLValueReferenceType):
            if output.type.const:
                return 'boost::python::copy_const_reference'
            else:
                return 'boost::python::copy_non_const_reference'
        elif isinstance(output, InterfacePointerType):
            return 'boost::python::manage_new_object'
%>
#include <boost/python.hpp>
#include <${model.file.replace('./src/cpp', library)}>

BOOST_PYTHON_MODULE(_${model.spelling})
{ <% return_value_policy = get_return_value_policy(model.output) %>\
boost::python::def("${model.spelling}", ${scope}${model.spelling}\
% if not return_value_policy is None:
, boost::python::return_value_policy< ${return_value_policy} >()\
% endif
);\
}

void init_bindings()
{
    Py_Initialize();
    init_${model.spelling}();
}
