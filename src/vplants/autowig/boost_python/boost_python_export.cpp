/***************************************************************************/
/* This file was automatically generated using VPlants.AutoWIG package     */
/*                                                                         */
/* Any modification of this file will be lost if VPlants.AutoWIG is re-run */
/***************************************************************************/
<%!
    from vplants.autowig.tools import lower
    from vplants.autowig.boost_python.tools import write_thin, write_deep
%>\

#include <boost/python.hpp>
% for include in includes:
#include <${include}>
% endfor
% if len(enums)+len(functions)+len(classes) > 0:

% endif
% for enum in enums:
${write_thin(
    scope = scope,
    string = enum_thin.render(
        enum = enum,
        scope = scope,
        lookup = lookup))}\
void export_enum_${lower(str(enum))}()
${write_deep(
        enum_deep.render(
            enum = enum,
            scope = scope,
            lookup = lookup))}\
% endfor
% for func in functions:
${write_thin(
    scope = scope,
    string = func_thin.render(
        func = func,
        scope = scope,
        lookup = lookup))}\
void export_function_${lower(str(func[0]))}()
${write_deep(func_deep.render(
            func = func,
            scope = scope,
            lookup = lookup))}\
% endfor
% for clss in classes:
${write_thin(
    scope = scope,
    string = clss_thin.render(
        clss = clss,
        scope = scope,
        enum_thin = enum_thin,
        func_thin = func_thin,
        clss_thin = clss_thin,
        lookup = lookup))}\
void export_class_${lower(str(clss))}()
${write_deep(
    clss_deep.render(
        clss = clss,
        scope = scope,
        enum_deep = enum_deep,
        func_deep = func_deep,
        clss_deep = clss_deep,
        level = 0,
        lookup = lookup))}\
% endfor
