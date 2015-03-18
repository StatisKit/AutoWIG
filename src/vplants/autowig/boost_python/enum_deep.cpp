% if enum.anonymous:
    % for value in enum.values:
boost::python::scope().attr("${value}") = ${scope}${value};
    % endfor
% else:
boost::python::enum_< ${scope}${str(enum)} >("${str(enum)}")\
        % for value in enum.values:

    .value("${value}", ${scope}${value})\
        % endfor
;
% endif
