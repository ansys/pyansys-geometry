"""Provides the ``Curve`` class."""
from abc import ABC, abstractmethod

from ansys.geometry.core.geometry.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.geometry.parameterization import Parameterization
from ansys.geometry.core.math import Matrix44, Point3D
from ansys.geometry.core.typing import Real


class Curve(ABC):
    """
    Curve abstract base class.

    Represents a 3D curve.
    """

    @abstractmethod
    def parameterization(self) -> Parameterization:
        """Parameterization of the curve."""
        return

    @abstractmethod
    def contains_param(self, param: Real) -> bool:
        """Test whether a parameter is within the parametric range of the curve."""
        return

    @abstractmethod
    def contains_point(self, point: Point3D) -> bool:
        """
        Test whether the point is contained by the curve.

        The point can either lie within it, or on its boundary.
        """
        return

    @abstractmethod
    def transformed_copy(self, matrix: Matrix44) -> "Curve":
        """Create a transformed copy of the curve."""
        return

    @abstractmethod
    def __eq__(self, other: "Curve") -> bool:
        """Determine if two curves are equal."""
        return

    @abstractmethod
    def evaluate(self, parameter: Real) -> CurveEvaluation:
        """Evaluate the curve at the given parameter."""
        return

    @abstractmethod
    def project_point(self, point: Point3D) -> CurveEvaluation:
        """
        Project a point to the curve.

        This returns the evaluation at the closest point.
        """
        return

    # TODO: Implement more curve methods
    # as_spline
    # get_length
    # get_polyline
    # intersect_curve
    # is_coincident
