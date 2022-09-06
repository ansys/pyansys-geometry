"""``Cylinder`` class module."""


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


class Cylinder:
    """
    Provides 3D ``Cylinder`` representation.

    Parameters
    ----------
    origin : Point3D
        Origin of the ``Cylinder``.
    direction_x : UnitVector3D
        X-plane direction.
    direction_y : UnitVector3D
        Y-plane direction.
    radius : Real
        Radius of the ``Cylinder``.
    height : Real
        Height of the ``Cylinder``.
    unit : Unit, optional
        Units employed to define the radius and height, by default ``UNIT_LENGTH``.
    """

    def __init__(
        self,
        origin: Point3D,
        direction_x: UnitVector3D,
        direction_y: UnitVector3D,
        radius: Real,
        height: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for ``Cylinder``."""

        if not isinstance(origin, Point3D):
            raise TypeError(f"origin is invalid, type {Point3D} expected.")

        if not isinstance(direction_x, UnitVector3D):
            raise TypeError(f"direction_x is invalid, type {UnitVector3D} expected.")

        if not isinstance(direction_y, UnitVector3D):
            raise TypeError(f"direction_y is invalid, type {UnitVector3D} expected.")

        check_is_float_int(radius, "radius")
        check_is_float_int(height, "height")

        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y

        # Store values in base unit
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)
        self._height = UNITS.convert(height, self._unit, self._base_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the ``Cylinder``."""
        return self._origin

    @origin.setter
    def origin(self, origin: Point3D) -> None:
        if not isinstance(origin, Point3D):
            raise TypeError(f"origin is invalid, type {Point3D} expected.")
        self._origin = origin

    @property
    def radius(self) -> Real:
        """Radius of the ``Cylinder``."""
        return UNITS.convert(self._radius, self._base_unit, self._unit)

    @radius.setter
    def radius(self, radius: Real) -> None:
        """Set the Radius of the ``Cylinder``."""
        check_is_float_int(radius, "radius")
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def height(self) -> Real:
        """Height of the ``Cylinder``."""
        return UNITS.convert(self._height, self._base_unit, self._unit)

    @height.setter
    def height(self, height: Real) -> None:
        """Set the Height of the ``Cylinder``."""
        check_is_float_int(height, "height")
        self._height = UNITS.convert(height, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the radius and height."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the object."""
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Cylinder``."""
        check_type_equivalence(other, self)

        return (
            self._origin == other.origin
            and self._radius == other.radius
            and self._height == other.height
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Cylinder``."""
        return not self == other
