"""Provides the ``Cone`` class."""


from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNIT_ANGLE, UNIT_LENGTH, UNITS, check_pint_unit_compatibility
from ansys.geometry.core.typing import Real, RealSequence


class Cone:
    """
    Provides 3D ``Cone`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Centered origin of the cone.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-plane direction.
    radius : Real
        Radius of the cone.
    half_angle : Real
        Half angle of the apex, determining the upward angle.
    length_unit : Unit, default: UNIT_LENGTH
        Units for defining the radius.
    angle_unit : Unit, default: UNIT_ANGLE
        Units for defining the half angle.
        ````.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        radius: Real,
        half_angle: Real,
        length_unit: Optional[Unit] = UNIT_LENGTH,
        angle_unit: Optional[Unit] = UNIT_ANGLE,
    ):
        """Constructor method for the ``Cone`` class."""
        check_pint_unit_compatibility(length_unit, UNIT_LENGTH)
        check_pint_unit_compatibility(angle_unit, UNIT_ANGLE)

        self._length_unit = length_unit
        _, self._base_length_unit = UNITS.get_base_units(length_unit)

        self._angle_unit = angle_unit
        _, self._base_angle_unit = UNITS.get_base_units(angle_unit)

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction_x = (
            UnitVector3D(direction_x) if not isinstance(direction_x, UnitVector3D) else direction_x
        )
        self._direction_y = (
            UnitVector3D(direction_y) if not isinstance(direction_y, UnitVector3D) else direction_y
        )

        # Store values in base unit
        self._radius = UNITS.convert(radius, self._length_unit, self._base_length_unit)
        self._half_angle = UNITS.convert(half_angle, self._angle_unit, self._base_angle_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the cone."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        self._origin = origin

    @property
    def radius(self) -> Real:
        """Radius of the cone."""
        return UNITS.convert(self._radius, self._base_length_unit, self._length_unit)

    @radius.setter
    @check_input_types
    def radius(self, radius: Real) -> None:
        self._radius = UNITS.convert(radius, self._length_unit, self._base_length_unit)

    @property
    def half_angle(self) -> Real:
        """Half angle of the apex."""
        return UNITS.convert(self._half_angle, self._base_angle_unit, self._angle_unit)

    @half_angle.setter
    @check_input_types
    def half_angle(self, half_angle: Real) -> None:
        self._half_angle = UNITS.convert(half_angle, self._angle_unit, self._base_angle_unit)

    @property
    def length_unit(self) -> Unit:
        """Unit of the radius."""
        return self._length_unit

    @length_unit.setter
    @check_input_types
    def length_unit(self, length_unit: Unit) -> None:
        check_pint_unit_compatibility(length_unit, UNIT_LENGTH)
        self._length_unit = length_unit

    @property
    def angle_unit(self) -> Unit:
        """Unit of the angle."""
        return self._angle_unit

    @angle_unit.setter
    @check_input_types
    def angle_unit(self, angle_unit: Unit) -> None:
        check_pint_unit_compatibility(angle_unit, UNIT_ANGLE)
        self._angle_unit = angle_unit

    @check_input_types
    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Cone`` class."""
        return (
            self._origin == other.origin
            and self._radius == other.radius
            and self._half_angle == other.half_angle
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for the ``Cone`` class."""
        return not self == other
