"""``Sphere`` class module."""


from beartype.typing import List, Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    UNITS,
    check_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real, RealSequence


class Sphere:
    """
    Provides 3D ``Sphere`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Centered origin of the ``Sphere``.
    radius : Real
        Radius of ``Sphere``.
    unit : Unit, optional
        Units employed to define the radius and height, by default ``UNIT_LENGTH``.
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for ``Sphere``."""

        check_type(origin, (np.ndarray, List, Point3D))

        check_is_float_int(radius, "radius")

        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        # Store values in base unit
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the ``Sphere``."""
        return self._origin

    @origin.setter
    def origin(self, origin: Point3D) -> None:
        if not isinstance(origin, Point3D):
            raise TypeError(f"origin is invalid, type {Point3D} expected.")
        self._origin = origin

    @property
    def radius(self) -> Real:
        """Radius of the ``Sphere``."""
        return UNITS.convert(self._radius, self._base_unit, self._unit)

    @radius.setter
    def radius(self, radius: Real) -> None:
        check_is_float_int(radius, "radius")
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the radius."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Sphere``."""
        check_type_equivalence(other, self)

        return self._origin == other.origin and self._radius == other.radius

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Sphere``."""
        return not self == other
