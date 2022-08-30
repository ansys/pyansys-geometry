"""
Module containing the GRPCWrapper class.
This is the base class for the entire abstraction layer of PyDiscovery.
It contains a simple interface for all gRPC-related messages so that
they are easily extandable as actual Python objects.
"""

from abc import ABC, abstractmethod


class GRPCWrapper(ABC):
    """Abstract Base Class for ansys.discovery.models contains abstract methods for
    updating gRPC messages and create Pythonic objects. Contains a set of methods that
    must be created within any child classes built from the abstract class.
    Abstract classes are not instantiated, and its abstract methods must
    be implemented by its subclasses.
    The goal of this GRPCWrapper class is to provide a common parent to all
    Python objects of the PyDiscovery abstraction layer, as well as a common interface for
    its interaction with the raw gRPC messages.
    """

    def __init__(self):
        """Constructor for the abstract GRPCWrapper class."""
        self._msg = None

    @abstractmethod
    def _update_message(self):
        """Abstract method for updating the gRPC message."""
        raise NotImplementedError("This operation is not implemented")

    @classmethod
    @abstractmethod
    def _from_message(cls, value):
        """Abstract method for obtaining the pythonic object from its related gRPC
        message."""
        raise NotImplementedError("This operation is not implemented")