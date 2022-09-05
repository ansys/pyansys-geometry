"""``Cone`` class module."""


from typing import Optional

from pint import Unit

from ansys.geometry.core import UNIT_ANGLE, UNIT_LENGTH, UNITS
from ansys.geometry.core.misc import (
    check_is_float_int,
    check_is_pint_unit,
    check_pint_unit_compatibility,
    check_type_equivalence,
)
from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import UnitVector3D
from ansys.geometry.core.typing import Real


class Cone:
    """
    Provides 3D ``Cone`` representation.
    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Cone``.
    direction_x: UnitVector3D
        X-plane direction.
    direction_y: UnitVector3D
        Y-plane direction.
    radius: float
        Radius of ``Cone``.
    half_angle: float
        Angle determine upward angle of ``Cone``.
    length_unit : Unit, optional
        Units employed to define the radius, by default ``UNIT_LENGTH``.
    angle_unit : Unit, optional
        Units employed to define the half_angle, by default ``UNIT_ANGLE``.
    """

    def __init__(
        self,
        origin: Point3D,
        direction_x: UnitVector3D,
        direction_y: UnitVector3D,
        radius: Real,
        half_angle: Real,
        length_unit: Optional[Unit] = UNIT_LENGTH,
        angle_unit: Optional[Unit] = UNIT_ANGLE,
    ):
        """Constructor method for ``Cone``."""

        if not isinstance(direction_x, UnitVector3D):
            raise TypeError(f"direction_x is invalid, type {UnitVector3D} expected.")

        if not isinstance(direction_y, UnitVector3D):
            raise TypeError(f"direction_y is invalid, type {UnitVector3D} expected.")

        check_is_float_int(radius, "radius")
        check_is_float_int(half_angle, "half_angle")

        check_is_pint_unit(length_unit, "length_unit")
        check_pint_unit_compatibility(length_unit, UNIT_LENGTH)

        check_is_pint_unit(angle_unit, "angle_unit")
        check_pint_unit_compatibility(angle_unit, UNIT_ANGLE)

        self._length_unit = length_unit
        _, self._base_length_unit = UNITS.get_base_units(length_unit)

        self._angle_unit = angle_unit
        _, self._base_angle_unit = UNITS.get_base_units(angle_unit)

        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y

        # Store values in base unit
        self._radius = UNITS.convert(radius, self._length_unit, self._base_length_unit)
        self._half_angle = UNITS.convert(half_angle, self._angle_unit, self._base_angle_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the ``Cone``."""
        return self._origin

    @property
    def radius(self) -> Real:
        """Radius of the ``Cone``."""
        return UNITS.convert(self._radius, self._base_length_unit, self._length_unit)

    @radius.setter
    def radius(self, radius: Real) -> None:
        """Set the Radius of the ``Cone``."""
        check_is_float_int(radius, "radius")
        self._radius = UNITS.convert(radius, self._length_unit, self._base_length_unit)

    @property
    def half_angle(self) -> Real:
        """Half Angle of the ``Cone``."""
        return UNITS.convert(self._half_angle, self._base_angle_unit, self._angle_unit)

    @half_angle.setter
    def half_angle(self, half_angle: Real) -> None:
        """Set the Half Angle of the ``Cone``."""
        check_is_float_int(half_angle, "half_angle")
        self._half_angle = UNITS.convert(half_angle, self._angle_unit, self._base_angle_unit)

    @property
    def length_unit(self) -> Unit:
        """Unit of the Radius."""
        return self._length_unit

    @length_unit.setter
    def length_unit(self, length_unit: Unit) -> None:
        """Sets the unit of the object."""
        check_is_pint_unit(length_unit, "length_unit")
        check_pint_unit_compatibility(length_unit, UNIT_LENGTH)
        self._length_unit = length_unit

    @property
    def angle_unit(self) -> Unit:
        """Unit of the Half Radius."""
        return self._angle_unit

    @angle_unit.setter
    def angle_unit(self, angle_unit: Unit) -> None:
        """Sets the unit of the object."""
        check_is_pint_unit(angle_unit, "angle_unit")
        check_pint_unit_compatibility(angle_unit, UNIT_ANGLE)
        self._angle_unit = angle_unit

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Cone``."""
        check_type_equivalence(other, self)

        return (
            self._origin == other.origin
            and self._radius == other.radius
            and self._half_angle == other.half_angle
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Cone``."""
        return not self == other
