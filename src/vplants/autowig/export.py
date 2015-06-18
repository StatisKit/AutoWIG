import os
import warnings
import itertools

__all__ = []

from .asg import AbstractSemanticGraph
#, NamespaceProxy, EnumConstantProxy, EnumProxy, VariableProxy, FunctionProxy, ClassProxy, ClassTemplateProxy
#from .boost_python import BoostPythonExportFileProxy, BoostPythonModuleFileProxy

def export(self):
    for node in self.files():
        if hasattr(node, 'export') and node.export:
            node.write()
    #nodes = self[pattern]
    #if not isinstance(nodes, list):
    #    nodes = [nodes]
    #exported = {node.id for node in itertools.chain(*[export.exports for export in self.files() if isinstance(export, BoostPythonExportFileProxy)])}
    #for node in nodes:
    #    if node.traverse and isinstance(node, BoostPythonExportFileProxy):
    #        for variable in node.variables:
    #            if not variable.type.target.id in exported:
    #                warnings.warn(variable.type.target.id, UserWarning)
    #        for function in node.functions:
    #            for parameter in function.parameters:
    #                if not parameter.type.target.id in exported:
    #                    warnings.warn(parameter.type.target.id, UserWarning)
    #            if not function.result_type.target.id in exported:
    #                warnings.warn(function.result_type.target.id, UserWarning)
    #        for clss in node.classes:
    #            for field in clss.fields():
    #                if field.access == 'public':
    #                    if not field.type.target.id in exported:
    #                        warnings.warn(field.type.target.id, UserWarning)
    #            for method in clss.methods():
    #                if method.access == 'public':
    #                    for parameter in method.parameters:
    #                        if not parameter.type.target.id in exported:
    #                            warnings.warn(parameter.type.target.id, UserWarning)
    #                    if not method.result_type.target.id in exported:
    #                        warnings.warn(method.result_type.target.id, UserWarning)
    #            for constructor in clss.constructors:
    #                if constructor.access == 'public':
    #                    for parameter in constructor.parameters:
    #                        if not parameter.type.target.id in exported:
    #                            warnings.warn(parameter.type.target.id, UserWarning)
    #        node.write()
    #    elif node.traverse and isinstance(node, BoostPythonModuleFileProxy):
    #        node.write()

AbstractSemanticGraph.export = export
del export
