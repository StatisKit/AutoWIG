/** This file was automaticaly generated using VPlants.AutoWIG package
 * 
 * @warning Any post-processing of this file will be lost if VPlants.AutoWIG is re-run
 * */

#include <boost/python.hpp>
<% files = set() %>\
% for m in models:
    % if not m.file in files:
#include <${m.file}><% files.add(m.file) %>
    % endif
% endfor

using namespace boost::python;

% for i, j in enumerate(models):
${j.output.spelling} (${scope}*${j.spelling}_${i})(${", ".join([k.type.spelling if not k.const else 'const '+k.type.spelling for k in j.inputs])}) = ${scope}${j.spelling};
% endfor

BOOST_PYTHON_MODULE(_${models[0].spelling})
{
% for i, j in enumerate(models):
    def("${j.spelling}", ${j.spelling}_${i})
% endfor
}

void init_bindings()
{
    Py_Initialize();
    init_${models[0].spelling}();
}
