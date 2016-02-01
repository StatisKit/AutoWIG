from .asg import FunctionProxy, MethodProxy, FundamentalTypeProxy, EnumerationProxy

def boost_python_default_call_policy(node):
    if isinstance(node, FunctionProxy):
        result_type = node.result_type
        if result_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif result_type.is_reference:
            if result_type.is_const or isinstance(result_type.target, (FundamentalTypeProxy, EnumerationProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
    elif isinstance(node, MethodProxy):
        result_type = node.result_type
        if result_type.is_pointer:
            return 'boost::python::return_value_policy< boost::python::reference_existing_object >()'
        elif result_type.is_reference:
            if result_type.is_const or isinstance(result_type.target, (FundamentalTypeProxy, EnumerationProxy)):
                return 'boost::python::return_value_policy< boost::python::return_by_value >()'
            else:
                return 'boost::python::return_internal_reference<>()'
