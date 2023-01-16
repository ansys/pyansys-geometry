""" Provides the ``Circle`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Z, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import Accuracy, Distance
from ansys.geometry.core.primitives.curve_evaluation import CurveEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Circle:
    """
    Provides 3D ``Circle`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the circle.
    radius : Union[Quantity, Distance]
        Radius of the circle.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-plane direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Union[Quantity, Distance],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis

        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Circle reference (dir_x) and axis (dir_z) must be perpendicular.")

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

    @property
    def origin(self) -> Point3D:
        """Origin of the circle."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the circle"""
        self._origin = origin

    @property
    def radius(self) -> Quantity:
        """Radius of the circle."""
        return self._radius.value

    @property
    def diameter(self) -> Quantity:
        """Diameter of the circle."""
        return 2 * self.radius

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the circle."""
        return 2 * np.pi * self.radius

    @property
    def area(self) -> Quantity:
        """Area of the circle."""
        return np.pi * self.radius**2

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the circle"""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the circle"""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the circle"""
        return self._axis

    @check_input_types
    def __eq__(self, other: "Circle") -> bool:
        """Equals operator for the ``Circle`` class."""
        return (
            self._origin == other._origin
            and self._radius == other._radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def evaluate(self, parameter: float) -> "CircleEvaluation":
        """Evaluate the circle at the given parameter"""
        return CircleEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "CircleEvaluation":
        """Project a point onto the circle and return its CircleEvaluation"""
        origin_to_point = point - self.origin
        dir_in_plane = UnitVector3D.from_points(
            Point3D([0, 0, 0]), origin_to_point - ((origin_to_point * self.dir_z) * self.dir_z)
        )
        if dir_in_plane.is_zero:
            return CircleEvaluation(self, 0)

        t = np.arctan2(self.dir_y.dot(dir_in_plane), self.dir_x.dot(dir_in_plane))
        return CircleEvaluation(self, t)

    def is_coincident_circle(self, other: "Circle") -> bool:
        """Determine if this circle is coincident with another"""
        return (
            Accuracy.length_is_equal(self.radius.m, other.radius.m)
            and self.origin == other.origin
            and self.dir_z == other.dir_z
        )


class CircleEvaluation(CurveEvaluation):
    """
    Provides ``Circle`` evaluation at a certain parameter.
    Parameters
    ----------
    circle: ~ansys.geometry.core.primitives.circle.Circle
        The ``Circle`` object to be evaluated.
    parameter: float, int
        The parameter at which the ``Circle`` evaluation is requested.
    """

    def __init__(self, circle: Circle, parameter: Real) -> None:
        self._circle = circle
        self._parameter = parameter

    @property
    def circle(self) -> Circle:
        """The circle being evaluated"""
        return self._circle

    @property
    def parameter(self) -> Real:
        """The parameter that the evaluation is based upon"""
        return self._parameter

    def position(self) -> Point3D:
        """The position of the evaluation"""
        return (
            self.circle.origin
            + ((self.circle.radius * np.cos(self.parameter)) * self.circle.dir_x).m
            + ((self.circle.radius * np.sin(self.parameter)) * self.circle.dir_y).m
        )

    def tangent(self) -> UnitVector3D:
        """The tangent of the evaluation"""
        return (
            np.cos(self.parameter) * self.circle.dir_y - np.sin(self.parameter) * self.circle.dir_x
        )

    def first_derivative(self) -> Vector3D:
        """The first derivative of the evaluation"""
        return self.circle.radius.m * (
            np.cos(self.parameter) * self.circle.dir_y - np.sin(self.parameter) * self.circle.dir_x
        )

    def second_derivative(self) -> Vector3D:
        """The second derivative of the evaluation"""
        return -self.circle.radius.m * (
            np.cos(self.parameter) * self.circle.dir_x + np.sin(self.parameter) * self.circle.dir_y
        )

    def curvature(self) -> Real:
        """The curvature of the evaluation"""
        return 1 / np.abs(self.circle.radius.m)
