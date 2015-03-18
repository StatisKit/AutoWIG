/***************************************************************************/
/* This file was automatically generated using VPlants.AutoWIG package     */
/*                                                                         */
/* Any modification of this file will be lost if VPlants.AutoWIG is re-run */
/***************************************************************************/

#include <boost/python.hpp>
% for funcname in funcnames:
void ${funcname}();
% endfor

BOOST_PYTHON_MODULE(_${modname})
{
% for funcname in funcnames:
    ${funcname}();
% endfor
}

void init_bindings()
{
    Py_Initialize();
    init_${modname}();
}
