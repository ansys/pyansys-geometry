"""
Module containing the BaseEntity class.

This is the base class for the entire abstraction layer for models in PyGeometry.
"""

from abc import ABC, abstractmethod


class BaseEntity(ABC):
    """Abstract Base Class for ansys.geometry.core.models.entity.

    Contains abstract methods for all geometry primitives. Contains a set of methods that
    must be created within any child classes built from the abstract class.
    Abstract classes are not instantiated, and its abstract methods must
    be implemented by its subclasses.
    The goal of this BaseEntity class is to provide a common parent to all
    entities of the PyGeometry abstraction layer.
    """

    def __init__(self):
        """Abstract BaseEntity class constructor."""
        self._msg = None

    @abstractmethod
    def _update_message(self):
        """Abstract method for updating the gRPC message."""
        raise NotImplementedError("This operation is not implemented")

    @classmethod
    @abstractmethod
    def _from_message(cls, value):
        """Abstract method to obtain the pythonic object from its related gRPC message."""
        raise NotImplementedError("This operation is not implemented")
