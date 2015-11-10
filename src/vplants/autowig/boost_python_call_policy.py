from .asg import FunctionProxy, MethodProxy, FundamentalTypeProxy, EnumProxy

def default_call_policy(node):
    if not isinstance(node, FunctionProxy):
        raise TypeError('\'node\' parameter')
    result_type = node.result_type
    if result_type.is_pointer:
        return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
    elif result_type.is_reference:
        if result_type.is_const or isinstance(result_type.target, (FundamentalTypeProxy, EnumProxy)):
            return 'boost::python::return_value_policy< boost::python::return_by_value >()'
        else:
            if isinstance(node, MethodProxy):
                return 'boost::python::return_internal_reference<>()'
            else:
                return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
