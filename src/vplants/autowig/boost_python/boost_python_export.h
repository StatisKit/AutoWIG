<%!
    from vplants.autowig.tools import lower
%>\
/** This file was automatically generated using VPlants.AutoWIG package
*
* @warning Any modification of this file will be lost if VPlants.AutoWIG is re-run
* */

#include <boost/python.hpp>
% for include in includes:
#include <${library(include)}>
% endfor

% for enum in enums:
void export_enum_${lower(str(enum))}();
% endfor
% if len(enums) > 0:

% endif
% for func in functions:
void export_function_${lower(str(func[0]))}();
% endfor
% if len(func) > 0:

% endif
% for clss in classes:
void export_class_${lower(str(clss))}();
% endfor
