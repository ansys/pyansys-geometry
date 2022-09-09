"""``Cylinder`` class module."""

from typing import List, Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point, UnitVector, Vector
from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    UNITS,
    check_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real, RealSequence


class Cylinder:
    """
    Provides 3D ``Cylinder`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point]
        Origin of the ``Cylinder``.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector, Vector]
        X-plane direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector, Vector]
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
        origin: Union[np.ndarray, RealSequence, Point],
        direction_x: Union[np.ndarray, RealSequence, UnitVector, Vector],
        direction_y: Union[np.ndarray, RealSequence, UnitVector, Vector],
        radius: Real,
        height: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for ``Cylinder``."""

        check_type(origin, (np.ndarray, List, Point))
        check_type(direction_x, (np.ndarray, List, UnitVector, Vector))
        check_type(direction_y, (np.ndarray, List, UnitVector, Vector))

        check_is_float_int(radius, "radius")
        check_is_float_int(height, "height")

        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = Point(origin) if not isinstance(origin, Point) else origin
        self._direction_x = (
            UnitVector(direction_x) if not isinstance(direction_x, UnitVector) else direction_x
        )
        self._direction_y = (
            UnitVector(direction_y) if not isinstance(direction_y, UnitVector) else direction_y
        )

        # Store values in base unit
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)
        self._height = UNITS.convert(height, self._unit, self._base_unit)

    @property
    def origin(self) -> Point:
        """Origin of the ``Cylinder``."""
        return self._origin

    @origin.setter
    def origin(self, origin: Point) -> None:
        if not isinstance(origin, Point):
            raise TypeError(f"origin is invalid, type {Point} expected.")
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
        check_type(unit, Unit)
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
