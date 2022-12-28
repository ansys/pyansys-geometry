""" Provides the ``Circle`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS, check_pint_unit_compatibility
from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.primitives.curve_evaluation import CurveEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Circle:
    """
    Provides 3D ``Circle`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the circle.
    radius : Real
        Radius of the circle.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-plane direction.
    unit : Unit, default: UNIT_LENGTH
        Units for defining the radius.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Real,
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UnitVector3D(
            [1, 0, 0]
        ),
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UnitVector3D([0, 0, 1]),
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis

        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Circle reference (dir_x) and axis (dir_z) must be perpendicular.")

        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

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
    def radius(self) -> Real:
        """Radius of the circle."""
        return UNITS.convert(self._radius, self._base_unit, self._unit)

    @radius.setter
    @check_input_types
    def radius(self, radius: Real) -> None:
        """Set the radius of the circle."""
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def dir_x(self) -> UnitVector3D:
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        return self._axis

    @property
    def unit(self) -> Unit:
        """Unit of the radius."""
        return self._unit

    @unit.setter
    @check_input_types
    def unit(self, unit: Unit) -> None:
        """Set the unit of the object."""
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    @check_input_types
    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Circle`` class."""
        if isinstance(other, Circle):
            return (
                self._origin == other.origin
                and self._radius == other.radius
                and self._reference == other._reference
                and self._axis == other._axis
            )
        return False

    def evaluate(self, parameter: float) -> "CircleEvaluation":
        return CircleEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "CircleEvaluation":
        origin_to_point = point - self.origin
        dir_in_plane = UnitVector3D.from_points(
            Point3D([0, 0, 0]), origin_to_point - ((origin_to_point * self.dir_z) * self.dir_z)
        )
        if dir_in_plane.is_zero:
            return CircleEvaluation(self, 0)

        t = np.arctan2(self.dir_y.dot(dir_in_plane), self.dir_x.dot(dir_in_plane))
        return CircleEvaluation(self, t)

    def is_coincident_circle(self, other: "Circle") -> bool:
        return (
            Accuracy.length_is_equal(self.radius, other.radius)
            and self.origin == other.origin
            and self.dir_z == other.dir_z
        )


class CircleEvaluation(CurveEvaluation):
    def __init__(self, circle: Circle, parameter: float = None) -> None:
        self._circle = circle
        self._parameter = parameter

    @property
    def circle(self) -> Circle:
        return self._circle

    @property
    def parameter(self) -> float:
        return self._parameter

    def position(self) -> Point3D:
        return (
            self.circle.origin
            + (self.circle.radius * np.cos(self.parameter)) * self.circle.dir_x
            + (self.circle.radius * np.sin(self.parameter)) * self.circle.dir_y
        )

    def tangent(self) -> UnitVector3D:
        return (
            np.cos(self.parameter) * self.circle.dir_y - np.sin(self.parameter) * self.circle.dir_x
        )

    def first_derivative(self) -> Vector3D:
        return self.circle.radius * (
            np.cos(self.parameter) * self.circle.dir_y - np.sin(self.parameter) * self.circle.dir_x
        )

    def second_derivative(self) -> Vector3D:
        return -self.circle.radius * (
            np.cos(self.parameter) * self.circle.dir_x + np.sin(self.parameter) * self.circle.dir_y
        )

    def curvature(self) -> float:
        return 1 / np.abs(self.circle.radius)
