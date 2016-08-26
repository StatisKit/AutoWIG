from .asg import (HeaderProxy,
                  TypedefProxy,
                  EnumerationProxy,
                  FunctionProxy,
                  ConstructorProxy,
                  ClassProxy,
                  ClassTemplateSpecializationProxy,
                  ClassTemplateProxy,
                  VariableProxy,
                  ClassTemplatePartialSpecializationProxy)

from ._controller import refactoring, cleaning

__all__ = []

def default_controller(asg, **kwargs):
    """Post-processing step of an AutoWIG front-end

    During this step, three distinct operations are executed:

        * The **overloading** operation.
          During this operation functions and methods of the Abstract Semantic Graph (ASG) are traversed in order to determine if they are overloaded or not.
          This operation has at worst a time-complexity in :math:`\mathcal{O}\left(F^2\right)` where :math:`F` denotes the number of functions and methods in the ASG.
          Therefore, its default behavior is altered and all functions and methods are considered as overloaded which induces a time-complexity of :math:`\mathcal{O}\left(N\right)` where :math:`N` denotes the number of nodes in the ASG.

        * The **discarding** operation.

        * The **templating** operation.

    :Parameter:
        `overload` (bool) - The boolean considered in order to determine if the behavior of the **overloading** operation is altered or not.

    :Return Type:
        `None`

    .. seealso::
        :func:`autowig.libclang_parser.parser` for an example.
        :func:`compute_overloads`, :func:`discard_forward_declarations` and :func:`resolve_templates` for a more detailed documentatin about AutoWIG front-end post-processing step.
    """
    if kwargs.pop('refactoring', True):
        asg = refactoring(asg)
    if kwargs.pop('clean', True):
        asg = cleaning(asg)
    return asg
