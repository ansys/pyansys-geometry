"""
Module containing the BaseEntity class.

This is the base class for the entire abstraction layer for models in PyGeometry.
"""

from abc import ABC


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
        pass
