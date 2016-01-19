<%!
    from vplants.autowig.tools import indent
    from vplants.autowig.cpp.interface import enums, functions, classes
%>\
<%
    public = clss.access('public')
    nclsses = [nclss for nclss in classes(*public) if not nclss.hidden and not nclss.has_templates and not nclss.empty]
%>\
% for enum in enums(*public):
    % if not enum.hidden:
${enum_thin.render(enum=enum, scope=scope+str(clss), lookup=lookup)}\
    % endif
% endfor
% for method in functions(*public):
${func_thin.render(
    func = method,
    scope = scope+str(clss)+"::",
    lookup = lookup)}\
% endfor
% if len(nclsses) > 0:
namespace ${str(clss)}
{
    % for nclss in nclsses:
        % if not nclss.hidden:
${indent(
    clss_thin.render(
        clss = nclss,
        scope = scope+str(clss)+"::",
        enum_thin = enum_thin,
        func_thin = func_thin,
        clss_thin = clss_thin,
        lookup=lookup))}\
        % endif
    % endfor
}
% endif
