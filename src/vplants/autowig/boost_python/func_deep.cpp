<%!
    from vplants.autowig.boost_python.tools import return_value_policy
%>\
% if len(func) > 1:

    % for index, overload in enumerate(func):
        % if not overload.hidden:
    boost::python::def("${str(overload)}", ${"&"*(hasattr(overload, 'static') and overload.static)}::autowig${scope}${str(overload)}_${index}\
<%
            policy = return_value_policy(overload)
%>\
            % if not policy is None:
, ${policy}\
            % endif
);
        % endif
    % endfor
% else:
boost::python::def("${str(func[0])}", ${"&"*(hasattr(func[0], 'static') and func[0].static)}${scope}${str(func[0])}\
<%
    policy = return_value_policy(func[0])
%>\
    % if not policy is None:
, ${policy}\
    % endif
); \
% endif
