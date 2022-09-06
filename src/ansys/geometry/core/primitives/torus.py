"""``Torus`` class module."""


from typing import Optional

from pint import Unit

from ansys.geometry.core import UNIT_LENGTH, UNITS
from ansys.geometry.core.misc import (
    check_is_float_int,
    check_is_pint_unit,
    check_pint_unit_compatibility,
    check_type_equivalence,
)
from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import UnitVector3D
from ansys.geometry.core.typing import Real


class Torus:
    """
    Provides 3D ``Torus`` representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Torus``.
    direction_x: UnitVector3D
        X-plane direction.
    direction_y: UnitVector3D
        Y-plane direction.
    semi_major_radius: Real
        Major radius of ``Torus``.
    semi_minor_radius: Real
        Minor radius of ``Torus``.
    unit : Unit, optional
        Units employed to define the radius and minor_radius, by default ``UNIT_LENGTH``.
    """

    def __init__(
        self,
        origin: Point3D,
        direction_x: UnitVector3D,
        direction_y: UnitVector3D,
        semi_major_radius: Real,
        semi_minor_radius: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for ``Torus``."""

        if not isinstance(origin, Point3D):
            raise TypeError(f"origin is invalid, type {Point3D} expected.")

        if not isinstance(direction_x, UnitVector3D):
            raise TypeError(f"direction_x is invalid, type {UnitVector3D} expected.")

        if not isinstance(direction_y, UnitVector3D):
            raise TypeError(f"direction_y is invalid, type {UnitVector3D} expected.")

        check_is_float_int(semi_major_radius, "semi_major_radius")
        check_is_float_int(semi_minor_radius, "semi_minor_radius")

        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y

        # Store values in base unit
        self._semi_major_radius = UNITS.convert(semi_major_radius, self._unit, self._base_unit)
        self._semi_minor_radius = UNITS.convert(semi_minor_radius, self._unit, self._base_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the ``Torus``."""
        return self._origin

    @origin.setter
    def origin(self, origin: Point3D) -> None:
        if not isinstance(origin, Point3D):
            raise TypeError(f"origin is invalid, type {Point3D} expected.")
        self._origin = origin

    @property
    def semi_major_radius(self) -> Real:
        """Semi-major radius of the ``Torus``."""
        return UNITS.convert(self._semi_major_radius, self._base_unit, self._unit)

    @semi_major_radius.setter
    def semi_major_radius(self, semi_major_radius: Real) -> None:
        check_is_float_int(semi_major_radius, "semi_major_radius")
        self._semi_major_radius = UNITS.convert(semi_major_radius, self._unit, self._base_unit)

    @property
    def semi_minor_radius(self) -> Real:
        """Semi-minor radius of the ``Torus``."""
        return UNITS.convert(self._semi_minor_radius, self._base_unit, self._unit)

    @semi_minor_radius.setter
    def semi_minor_radius(self, semi_minor_radius: Real) -> None:
        check_is_float_int(semi_minor_radius, "semi_minor_radius")
        self._semi_minor_radius = UNITS.convert(semi_minor_radius, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the semi-major radius and semi-minor radius."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Torus``."""
        check_type_equivalence(other, self)

        return (
            self._origin == other.origin
            and self._semi_major_radius == other.semi_major_radius
            and self._semi_minor_radius == other.semi_minor_radius
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Torus``."""
        return not self == other
