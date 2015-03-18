<%!
    from vplants.autowig.tools import indent
    from vplants.autowig.cpp.interface import enums, functions, constructors, classes
%>\
<%
    public = clss.access('public')
    bclsses = [bclss for bclss in clss.bases('public') if not bclss.hidden]
    nclsses = [nclss for nclss in classes(*public) if not nclss.hidden and not nclss.has_templates and not nclss.empty]
%>\
boost::python::scope ${"nested_"*level}scope = boost::python::class_< ${scope}${str(clss)}, \
% if len(bclsses) > 0:
boost::python::bases< ${", ".join(str(bclss) for bclss in bclsses)} >, \
% endif
boost::shared_ptr< ${scope}${str(clss)} >\
% if clss.pure_virtual:
, boost::noncopyable\
% endif
 >("${str(clss)}", boost::python::no_init)
% if not clss.pure_virtual:
    % for constructor in constructors(*public):
        % if len(constructor.inputs) > 0:
    .def(boost::python::init< ${", ".join(str(input.type) for input in constructor.inputs)} >())
        % else:
    .def(boost::python::init<>())
        % endif
    % endfor
% endif
% for enum in enums(*public):
${enum_deep.render(
        enum=enum,
        scope=scope+str(clss)+"::",
        lookup=lookup)}\
% endfor
% for method in functions(*public):
${indent(
        func_deep.render(
            func = method,
            scope = scope+str(clss)+"::",
            lookup = lookup).replace('boost::python::def', '.def').replace(";", ""))}
% endfor
    ;
% for bclss in bclsses:
boost::python::implicitly_convertible< boost::shared_ptr< ${scope}${str(clss)} >, boost::shared_ptr< ${str(bclss)} > >();
% endfor
% for nclss in nclsses:
{
${indent(
    clss_deep.render(
        clss = nclss,
        scope = scope+str(clss)+"::",
        enum_deep = enum_deep,
        func_deep = func_deep,
        clss_deep = clss_deep,
        level = level+1,
        lookup = lookup))}
}
% endfor
