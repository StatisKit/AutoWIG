% if len(func) > 1:
    % for index, overload in enumerate(func):
        % if not overload.hidden:
${str(overload.output)} (*${str(overload)}_${index})(${", ".join([str(input.type) for input in overload.inputs])}) = ${scope}${str(overload)};
        % endif
    % endfor
% endif
