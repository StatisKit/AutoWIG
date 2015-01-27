/** This file was automaticaly generated using VPlants.AutoWIG package
 * 
 * @warning Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
 * */
 
#include <boost/python.hpp>
#include <${model.file}>

using namespace boost::python;

BOOST_PYTHON_MODULE(_${model.spelling})
{
    enum_< ${scope}${model.spelling} >("${model.spelling}")
        % for v in model.values:
        .value("${v}", ${scope}${v})
        % endfor
}

void init_bindings()
{
    Py_Initialize();
    init_${model.spelling}();
}
