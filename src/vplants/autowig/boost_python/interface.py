from abc import ABCMeta
from ..header.interface import EnumHeaderInterface, FunctionHeaderInterface, UserDefinedTypeHeaderInterface

class BoostPythonInterface(object):

    __metaclass__ = ABCMeta

BoostPythonInterface.register(EnumHeaderInterface)
BoostPythonInterface.register(FunctionHeaderInterface)
BoostPythonInterface.register(UserDefinedTypeHeaderInterface)
