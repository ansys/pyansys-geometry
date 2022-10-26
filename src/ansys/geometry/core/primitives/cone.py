"""``Cone`` class module."""


from beartype.typing import List, Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import (
    UNIT_ANGLE,
    UNIT_LENGTH,
    UNITS,
    check_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real, RealSequence


class Cone:
    """
    Provides 3D ``Cone`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Centered origin of the ``Cone``.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-plane direction.
    radius : Real
        Radius of ``Cone``.
    half_angle : Real
        Half angle of the apex, determining the upward angle.
    length_unit : Unit, optional
        Units employed to define the radius, by default ``UNIT_LENGTH``.
    angle_unit : Unit, optional
        Units employed to define the half_angle, by default ``UNIT_ANGLE``.
    """

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
        """Constructor method for ``Cone``."""

        check_type(origin, (np.ndarray, List, Point3D))
        check_type(direction_x, (np.ndarray, List, UnitVector3D, Vector3D))
        check_type(direction_y, (np.ndarray, List, UnitVector3D, Vector3D))

        check_is_float_int(radius, "radius")
        check_is_float_int(half_angle, "half_angle")

        check_type(length_unit, Unit)
        check_pint_unit_compatibility(length_unit, UNIT_LENGTH)

        check_type(angle_unit, Unit)
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
        """Origin of the ``Cone``."""
        return self._origin

    @origin.setter
    def origin(self, origin: Point3D) -> None:
        if not isinstance(origin, Point3D):
            raise TypeError(f"origin is invalid, type {Point3D} expected.")
        self._origin = origin

    @property
    def radius(self) -> Real:
        """Radius of the ``Cone``."""
        return UNITS.convert(self._radius, self._base_length_unit, self._length_unit)

    @radius.setter
    def radius(self, radius: Real) -> None:
        check_is_float_int(radius, "radius")
        self._radius = UNITS.convert(radius, self._length_unit, self._base_length_unit)

    @property
    def half_angle(self) -> Real:
        """Half angle of the apex."""
        return UNITS.convert(self._half_angle, self._base_angle_unit, self._angle_unit)

    @half_angle.setter
    def half_angle(self, half_angle: Real) -> None:
        check_is_float_int(half_angle, "half_angle")
        self._half_angle = UNITS.convert(half_angle, self._angle_unit, self._base_angle_unit)

    @property
    def length_unit(self) -> Unit:
        """Unit of the radius."""
        return self._length_unit

    @length_unit.setter
    def length_unit(self, length_unit: Unit) -> None:
        check_type(length_unit, Unit)
        check_pint_unit_compatibility(length_unit, UNIT_LENGTH)
        self._length_unit = length_unit

    @property
    def angle_unit(self) -> Unit:
        """Unit of the angle."""
        return self._angle_unit

    @angle_unit.setter
    def angle_unit(self, angle_unit: Unit) -> None:
        check_type(angle_unit, Unit)
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
