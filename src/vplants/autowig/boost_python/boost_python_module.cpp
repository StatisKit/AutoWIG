/** This file was automatically generated using VPlants.AutoWIG package
*
* @warning Any modification of this file will be lost if VPlants.AutoWIG is re-run
* */
<%!
    from vplants.autowig.boost_python.tools import write_deep
%>\

#include <boost/python.hpp>
% for include in includes:
#include <${include}>
% endfor

BOOST_PYTHON_MODULE(_${filename})
${write_deep(module)}

void init_bindings()
{
    Py_Initialize();
    init_${filename}();
}
