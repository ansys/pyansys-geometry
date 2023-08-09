"""Provides for creating and managing a curve."""
from functools import cached_property

from ansys.geometry.core.math import Point3D, Vector3D
from ansys.geometry.core.typing import Real


class CurveEvaluation:
    """Provides for evaluating a curve."""

    def __init__(self, parameter: Real = None) -> None:
        """Initialize the ``CurveEvaluation`` class."""
        self._parameter = parameter

    def is_set(self) -> bool:
        """Determine if the parameter for the evaluation has been set."""
        return self._parameter is not None

    @property
    def parameter(self) -> Real:
        """Parameter that the evaluation is based upon."""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    @cached_property
    def first_derivative(self) -> Vector3D:
        """First derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the first_derivative definition.")

    @cached_property
    def second_derivative(self) -> Vector3D:
        """Second derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the second_derivative definition.")

    @cached_property
    def curvature(self) -> Real:
        """Curvature of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the curvature definition.")
