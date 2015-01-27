/** This file was automaticaly generated using VPlants.AutoWIG package
 * 
 * @warning Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
 * */
 
 #include <boost/python.hpp>
#include <${model.file}>

using namespace boost::python;

BOOST_PYTHON_MODULE(_${model.spelling})
{
    def("${model.spelling}", ${scope}${model.spelling});
}

void init_bindings()
{
    Py_Initialize();
    init_${model.spelling}();
}
