
class FrontEndDiagnostic(object):
    """Diagnostic class for AutoWIG front-ends.

    This class enable to perform a basic analysis of called front-ends.
    In particular, the time elapsed in the pre-processing step (:attr:`preprocessing`) and diagnostics for the processing and the post-processing time (resp. :attr:`processing` and :attr:`postprocessing`) are stored.
    A brief summary of the Abstract Semantic Graph (ASG, see :class:`vplants.autowig.asg.AbstractSemanticGraph`) state after these steps is also computed:

    * :attr:`current` denotes the total number of nodes (:class:`vplants.autowig.asg.NodeProxy`) of the ASG.
    * :attr:`constants` denotes the number of enumeration constans (:class:`vplants.autowig.asg.EnumConstantProxy`) contained in both anonymous and non-anonymous enumerations of the ASG.
    * :attr:`enums` denotes the number of non-anonymous enumerations (:class:`vplants.autowig.asg.EnumProxy`) present in the ASG.
    * :attr:`variables` denotes the number of free and member variables (:class:`vplants.autowig.asg.VariableProxy`) present in the ASG.
    * :attr:`functions` denotes the number of free and member functions (:class:`vplants.autowig.FunctionProxy`) present in the ASG.
    * :attr:`classes` denotes the number of classes and class template specializations (:class:`vplants.autowig.asg.ClassProxy) present in the ASG.

    .. seealso::
        :var:`front_end` for a detailed documentation about AutoWIG front-end step.
        :func:`vplants.autowig.libclang_front_end.front_end` for an example.
    """

    def __init__(self):
        self.preprocessing = 0.
        self.processing = None
        self.current = 0
        self.constants = 0
        self.enums = 0
        self.variables = 0
        self.functions = 0
        self.classes = 0
        self.postprocessing = None

    def __call__(self, asg):
        """Compute the brief summary of the Abstract Semantic Graph (ASG) given.

        :Parameter:
            `asg` (:class:`vplants.autowig.AbstractSemanticGraph`) - The ASG to summarize.
        """
        self.current = len(asg)
        self.constants = 0
        self.enums = 0
        self.variables = 0
        self.functions = 0
        self.classes = 0
        for node in asg.nodes():
            if isinstance(node, EnumConstantProxy):
                self.constants += 1
            elif isinstance(node, EnumProxy):
                self.enums += 1
            elif isinstance(node, VariableProxy):
                self.variables += 1
            elif isinstance(node, FunctionProxy):
                self.functions += 1
            elif isinstance(node, ClassProxy):
                self.classes += 1

    @property
    def total(self):
        """Total time elapsed in the AutoWIG front-end step"""
        return self.preprocessing + self.processing.total + self.postprocessing.total

    def __str__(self):
        string = "Front-end: " + str(self.total)
        string += "\n * Pre-processing: " + str(self.preprocessing)
        string += "\n * Processing: " + str(self.processing.total)
        string += "\n * Post-Processing: " + str(self.postprocessing.total)
        return string


class PostProcessingDiagnostic(object):
    """Diagnostics for AutoWIG front-ends.

    This class enable to perform a basic analysis of called front-ends.
    In particular, the time elapsed in the pre-processing step (:attr:`preprocessing`) and diagnostics for the processing and the post-processing time (resp. :attr:`processing` and :attr:`postprocessing`) are stored.
    A brief summary of the Abstract Semantic Graph (ASG) state after these steps is also computed:

    * :attr:`current` denotes the total number of nodes (:class:`vplants.autowig.asg.NodeProxy`) of the ASG.
    * :attr:`constants` denotes the number of enumeration constans (:class:`vplants.autowig.EnumConstantProxy`) contained in both anonymous and non-anonymous enumerations of the ASG.
    * :attr:`enums` denotes the number of non-anonymous enumerations (:class:`vplants.autowig.EnumProxy`) present in the ASG.
    * :attr:`variables` denotes the number of free and member variables (:class:`vplants.autowig.VariableProxy`) present in the ASG.
    * :attr:`functions` denotes the number of free and member functions (:class:`vplants.autowig.FunctionProxy`) present in the ASG.
    * :attr:`classes` denotes the number of classes and class template specializations (:class:`vplants.autowig.ClassProxy) present in the ASG.

    .. seealso::
        :class:`FrontEndFunctor` for a detailed documentation about AutoWIG front-end step.
        :func:`postprocessing` and :func:`vplants.autowig.libclang_front_end.front_end` for an example.
    """

    def __init__(self):
        self.overloading = 0.
        self.discarding = 0.
        self.templating = 0.

    @property
    def total(self):
        return self.overloading + self.discarding + self.templating

    def __str__(self):
        string = "Front-end post-processing: " + str(self.total)
        string += "\n\t* Overloading: " + str(round(self.overloading/self.total*100,2))
        string += "\n\t* Discarding: " + str(round(self.discarding/self.total*100,2))
        string += "\n\t* Templating: " + str(round(self.templating/self.total*100,2))
        return string

class LibclangDiagnostic(object):
    """
    """

    name = 'libclang'

    def __init__(self):
        self.parsing = 0.
        self.translating = 0.

    @property
    def total(self):
        return self.parsing + self.translating

    def __str__(self):
        string = "Processing: " + str(self.total)
        string += "\n" + " * Parsing: " + str(self.parsing)
        string += "\n" + " * Translating: " + str(self.translating)
        return string


