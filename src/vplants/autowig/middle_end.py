import time
import uuid
from openalea.core.plugin.functor import PluginFunctor

from .asg import *

__all__ = [ 'middle_end']

class MiddleEndDiagnostic(object):
    """Diagnostic class for AutoWIG middle-ends.

    This class enable to perform a basic analysis of called middle-ends.
    In particular, a diagnostic for the pre-processing step (:attr:`preprocessing`) if any performed and time elapsed during the cleaning and invalidating processes (reps. :attr:`cleaning` and :attr:`invalidating`) are stored.
    A brief summary of the Abstract Semantic Graph (ASG, see :class:`vplants.autowig.asg.AbstractSemanticGraph`) state alteration by the middle-end step is performed:

    * :attr:`previous` denotes the total number of nodes (:class:`vplants.autowig.asg.NodeProxy`) of the ASG before the middle-end step is performed.
    * :attr:`current` denotes the total number of nodes (:class:`vplants.autowig.asg.NodeProxy`) of the ASG after the middle-end step is performed.
    * :attr:`invalidated` denotes the number of nodes invalidated during the middle-end step.

    .. seealso::
        :var:`middle_end` for a detailed documentation about AutoWIG middle-end step.
        :func:`vplants.autowig_plugin.autowig.DefaultMiddleEndPlugin.implementation` for an example.
    """

    def __init__(self):
        self.preprocessing = 0.0
        self.previous = 0
        self.current = 0
        #self.invalidated = 0
        self.cleaning = 0.
        #self.invalidating = 0.

    @property
    def total(self):
        """Total time elapsed in the AutoWIG middle-end step"""
        total = self.cleaning
        if not self.processing is None:
            total += self.preprocessing
        return total

def get_clean(self):
    if not hasattr(self, '_clean'):
        return self._clean_default
    else:
        return self._clean

def set_clean(self, clean):
    self.asg._nodes[self.node]['_clean'] = clean

def del_clean(self):
    self.asg._nodes[self.node].pop('_clean', False)

NodeProxy._clean_default = True
NodeProxy.clean = property(get_clean, set_clean, del_clean, doc = """
""")
del get_clean, set_clean, del_clean

FileProxy._clean_default = False

def _clean_default(self):
    return not self.is_primary

HeaderProxy._clean_default = property(_clean_default, doc = """
""")
del _clean_default

def _clean_default(self):
    header = self.header
    if header is not None and not header.clean:
        parent = self.parent
        if isinstance(parent, ClassProxy) and not self.access == 'public':
            return True
        else:
            return False
    else:
        return True

CodeNodeProxy._clean_default = property(_clean_default, doc="""
""")
del _clean_default

FundamentalTypeProxy._clean_default = False

def clean(self):
    """
    """
    cleanbuffer = [(node, node._clean) for node in self.nodes() if hasattr(node, '_clean')]
    temp = []
    for node in self.nodes():
        if node.clean:
            node.clean = True
        else:
            temp.append(node)
    while len(temp) > 0:
        node = temp.pop()
        node.clean = False
        parent = node.parent
        if parent.clean:
            temp.append(parent)
        else:
            parent.clean = False
        if hasattr(node, 'header'):
            header = node.header
            if not header is None:
                if header.clean:
                    temp.append(header)
                else:
                    header.clean = False
        if isinstance(node, HeaderProxy):
            include = node.include
            if not include is None:
                if include.clean:
                    temp.append(include)
                else:
                    include.clean = False
        elif isinstance(node, (TypedefProxy, VariableProxy)):
            target = node.type.target
            if target.clean:
                temp.append(target)
            else:
                target.clean = False
        elif isinstance(node, FunctionProxy):
            result_type = node.result_type.target
            if result_type.clean:
                temp.append(result_type)
            else:
                result_type.clean = False
            for parameter in node.parameters:
                target = parameter.type.target
                if target.clean:
                    temp.append(target)
                else:
                    target.clean = False
        elif isinstance(node, ConstructorProxy):
            for parameter in node.parameters:
                target = parameter.type.target
                if target.clean:
                    temp.append(target)
                else:
                    target.clean = False
        elif isinstance(node, ClassProxy):
            for base in node.bases():
                if base.access == 'public':
                    if base.clean:
                        temp.append(base)
                    else:
                        base.clean = False
            for dcl in node.declarations(): # constr
                if dcl.access == 'public':
                    if dcl.clean:
                        temp.append(dcl)
                    else:
                        dcl.clean = False
            #for mtd in node.methods():
            #    if mtd.access == 'public':
            #        if mtd.clean:
            #            temp.append(mtd)
            #        else:
            #            mtd.clean = False
            #for fld in node.fields():
            #    if fld.access == 'public':
            #        if fld.clean:
            #            temp.append(fld)
            #        else:
            #            fld.clean = False
            #for tdf in node.typedefs():
            #    if tdf.access == 'public':
            #        if tdf.clean:
            #            temp.append(tdf)
            #        else:
            #            tdf.clean = False
            #for cls in node.classes():
            #    if cls.access == 'public':
            if isinstance(node, ClassTemplateSpecializationProxy):
                specialize = node.specialize
                if specialize.clean:
                    temp.append(node.specialize)
                else:
                    specialize.clean = False
                for template in node.templates:
                    target = template.target
                    if target.clean:
                        temp.append(target)
                    else:
                        target.clean = False
        elif isinstance(node, ClassTemplateProxy):
            pass
            #for specialization in node.specializations():
            #    if specialization.clean:
            #        temp.append(specialization)
            #    else:
            #        specialization.clean = False
    for tdf in self.typedefs():
        if tdf.clean and not tdf.type.target.clean and not tdf.parent.clean:
            tdf.clean = False
            include = tdf.header
            while not include is None:
                include.clean = False
                include = include.include
    nodes = [node for node in self.nodes() if node.clean]
    for node in nodes:
        if not node.node in ['::', '/']:
            self._syntax_edges[node.parent.node].remove(node.node)
            if isinstance(node, (ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)):
                self._specialization_edges[node.specialize.node].remove(node.node)
            #if isinstance(node, ClassProxy):
            #    for inh in node.inheritors():
            #        self._base_edges[inh.node] = [base for base in self._base_edges[inh.node] if not base['base'] == node.node]
    for node in nodes:
        self._nodes.pop(node.node)
        self._include_edges.pop(node.node, None)
        self._syntax_edges.pop(node.node, None)
        self._base_edges.pop(node.node, None)
        self._type_edges.pop(node.node, None)
        self._parameter_edges.pop(node.node, None)
        self._specialization_edges.pop(node.node, None)
    nodes = set([node.node for node in nodes])
    for node in self.nodes():
        if isinstance(node, ClassProxy):
            self._base_edges[node.node] = [base for base in self._base_edges[node.node] if not base['base'] in nodes]
        del node.clean
    for node, clean in cleanbuffer:
        if node.node in self:
            node.clean = clean


AbstractSemanticGraph.clean = clean
del clean

#def get_traverse(self):
#    if not '_traverse' in self.asg._nodes[self.node]:
#        return True
#    else:
#        return self.asg._nodes[self.node]['_traverse']
#
#def set_traverse(self, traverse):
#    if not traverse:
#        self.asg._nodes[self.node]['_traverse'] = traverse
#
#def del_traverse(self):
#    self.asg._nodes[self.node].pop('_traverse', self._clean_default)
#
#NodeProxy.traverse = property(get_traverse, set_traverse, del_traverse)
#del get_traverse, set_traverse, del_traverse
#
#def default_traversal(self):
#    for node in self.nodes():
#        del node.traverse
#    temp = []
#    for node in self.nodes():
#        if not isinstance(node, CodeNodeProxy):
#            node.traverse = False
#        elif hasattr(node, 'access') and not access == 'public':
#            node.traverse = False
#        if isinstance(node, (ClassTemplateProxy, ClassTemplateSpecializationProxy, ClassTemplatePartialSpecializationProxy)) and node.is_smart_pointer:
#            node.traverse = False
#        else:
#            header = self.header
#            if header is None:
#                node.traverse = False
#            else:
#                node.traverse = header.is_primary
#            if node.traverse:
#                temp.append(node)
#    traversed = 0
#    while len(temp) > 0:
#        node = temp.pop()
#        node.traverse = True
#        traversed += 1
#        temp.append(node.parent)
#        if isinstance(node, (TypedefProxy, VariableProxy)):
#            underlying_type = node.type.target
#            if not underlying_type.traverse:
#                temp.append(underlying_type)
#            else:
#                underlying_type.traverse = True
#        elif isinstance(node, FunctionProxy):
#            result_type = node.result_type.target
#            if not result_type.traverse:
#                temp.append(result_type)
#            else:
#                result_type.traverse = True
#            for parameter in node.parameters:
#                if not parameter.traverse:
#                    temp.append(parameter)
#                else:
#                    parameter.traverse = True
#        elif isinstance(node, ConstructorProxy):
#            for parameter in node.parameters:
#                if not parameter.traverse:
#                    temp.append(parameter)
#                else:
#                    parameter.traverse = True
#        elif isinstance(node, ClassProxy):
#            for base in node.bases():
#                if base.access == 'public':
#                    if not base.traverse:
#                        temp.append(base)
#                    else:
#                        base.traverse = True
#    return traversed
#
#AbstractSemanticGraph.default_traversal = default_traversal
#del default_traversal

#def get_is_invalid(self):
#    if hasattr(self, '_is_invalid'):
#        return self._is_invalid
#    else:
#        return False
#
#def set_is_invalid(self, is_invalid):
#    self.asg._nodes[self.node]['_is_invalid'] = is_invalid
#
#def del_is_invalid(self):
#    self.asg._nodes[self.node].pop('_is_invalid', False)
#
#doc_is_invalid = """
#"""
#
#VariableProxy.is_invalid = property(get_is_invalid, set_is_invalid, del_is_invalid, doc = doc_is_invalid)
#FunctionProxy.is_invalid = property(get_is_invalid, set_is_invalid, del_is_invalid, doc = doc_is_invalid)
#ConstructorProxy.is_invalid = property(get_is_invalid, set_is_invalid, del_is_invalid, doc = doc_is_invalid)
#del get_is_invalid, set_is_invalid, del_is_invalid, doc_is_invalid
#
#def mark_invalid_pointers(asg):
#    invalidated = 0
#    for fct in asg.functions(free=None):
#        if fct.result_type.nested.is_pointer:
#            fct.is_invalid = True
#            invalidated += 1
#        elif fct.result_type.is_pointer and isinstance(fct.result_type.target, FundamentalTypeProxy):
#            fct.is_invalid = True
#            invalidated += 1
#        elif any(parameter.type.nested.is_pointer or parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in fct.parameters):
#            fct.is_invalid = True
#            invalidated += 1
#    for var in asg.variables(free=None):
#        if not isinstance(var.parent, (FunctionProxy, ConstructorProxy)):
#            if var.type.nested.is_pointer or var.type.is_pointer and isinstance(var.type.target, FundamentalTypeProxy):
#                var.is_invalid = True
#    for cls in asg.classes():
#        for ctr in cls.constructors:
#            if any(parameter.type.nested.is_pointer or parameter.type.is_pointer and isinstance(parameter.type.target, FundamentalTypeProxy) for parameter in ctr.parameters):
#                ctr.is_invalid = True
#                invalidated += 1
#    return invalidated

def get_is_smart_pointer(self):
    if not hasattr(self, '_is_smart_pointer'):
        return False
    return self._is_smart_pointer

def set_is_smart_pointer(self, is_smart_pointer):
    self.asg._nodes[self.node]['_is_smart_pointer'] = is_smart_pointer

def del_is_smart_pointer(self):
    self.asg._nodes[self.node].pop('_is_smart_pointer', False)

ClassTemplateProxy.is_smart_pointer = property(get_is_smart_pointer, set_is_smart_pointer, del_is_smart_pointer, doc = """
""")
del get_is_smart_pointer, set_is_smart_pointer, del_is_smart_pointer

def get_is_smart_pointer(self):
    return self.specialize.is_smart_pointer

def set_is_smart_pointer(self, is_smart_pointer):
    self.specialize.is_smart_pointer = is_smart_pointer

def del_is_smart_pointer(self):
    del self.specialize.is_smart_pointer

doc_is_smart_pointer = """
"""
ClassTemplateSpecializationProxy.is_smart_pointer = property(get_is_smart_pointer, set_is_smart_pointer, del_is_smart_pointer, doc = doc_is_smart_pointer)
del get_is_smart_pointer

def get_is_smart_pointer(self):
    return self.specialize.is_smart_pointer

doc_is_smart_pointer = """
"""
ClassTemplatePartialSpecializationProxy.is_smart_pointer = property(get_is_smart_pointer, set_is_smart_pointer, del_is_smart_pointer, doc = doc_is_smart_pointer)
del get_is_smart_pointer, set_is_smart_pointer, del_is_smart_pointer, doc_is_smart_pointer

def get_is_error(self):
    if not hasattr(self, '_is_error'):
        if any(base.is_error for base in self.bases()):
            self.is_error = True
        else:
            self.is_error = self.node == 'class ::std::exception'

    return self._is_error

def set_is_error(self, is_error):
    self.asg._nodes[self.node]['_is_error'] = is_error

def del_is_error(self):
    self.asg._nodes[self.node].pop('_is_error', None)

ClassProxy.is_error = property(get_is_error, set_is_error, del_is_error)
del get_is_error, set_is_error, del_is_error

middle_end = PluginFunctor.factory('autowig.middle_end')

#middle_end.__class__.__doc__ = """AutoWIG middle-ends functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""

#class DefaultMiddleEndPlugin(object):
#    """Basic plugin for source line of codes count"""
#
#    implements = 'middle-end'
#
#    def implementation(self, asg, *args, **kwargs):
#        """
#        """
#        from vplants.autowig.middle_end import MiddleEndDiagnostic
#        diagnostic = MiddleEndDiagnostic()
#        diagnostic.previous = len(asg)
#        prev = time.time()
#        asg.clean()
#        curr = time.time()
#        diagnostic.cleaning = curr - prev
#        diagnostic.current = len(asg)
#        return diagnostic
