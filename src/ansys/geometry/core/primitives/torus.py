"""``Torus`` class module."""

from beartype.typing import List, Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    UNITS,
    check_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real, RealSequence


class Torus:
    """
    Provides 3D ``Torus`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D],
        Centered origin of the ``Torus``.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-plane direction.
    major_radius : Real
        Major radius of ``Torus``.
    minor_radius : Real
        Minor radius of ``Torus``.
    unit : Unit, optional
        Units employed to define the radius and minor_radius, by default ``UNIT_LENGTH``.
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        major_radius: Real,
        minor_radius: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for ``Torus``."""

        check_type(origin, (np.ndarray, List, Point3D))
        check_type(direction_x, (np.ndarray, List, UnitVector3D, Vector3D))
        check_type(direction_y, (np.ndarray, List, UnitVector3D, Vector3D))

        check_is_float_int(major_radius, "major_radius")
        check_is_float_int(minor_radius, "minor_radius")

        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction_x = (
            UnitVector3D(direction_x) if not isinstance(direction_x, UnitVector3D) else direction_x
        )
        self._direction_y = (
            UnitVector3D(direction_y) if not isinstance(direction_y, UnitVector3D) else direction_y
        )

        # Store values in base unit
        self._major_radius = UNITS.convert(major_radius, self._unit, self._base_unit)
        self._minor_radius = UNITS.convert(minor_radius, self._unit, self._base_unit)

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
    def major_radius(self) -> Real:
        """Semi-major radius of the ``Torus``."""
        return UNITS.convert(self._major_radius, self._base_unit, self._unit)

    @major_radius.setter
    def major_radius(self, major_radius: Real) -> None:
        check_is_float_int(major_radius, "major_radius")
        self._major_radius = UNITS.convert(major_radius, self._unit, self._base_unit)

    @property
    def minor_radius(self) -> Real:
        """Semi-minor radius of the ``Torus``."""
        return UNITS.convert(self._minor_radius, self._base_unit, self._unit)

    @minor_radius.setter
    def minor_radius(self, minor_radius: Real) -> None:
        check_is_float_int(minor_radius, "minor_radius")
        self._minor_radius = UNITS.convert(minor_radius, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the semi-major radius and semi-minor radius."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Torus``."""
        check_type_equivalence(other, self)

        return (
            self._origin == other.origin
            and self._major_radius == other.major_radius
            and self._minor_radius == other.minor_radius
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Torus``."""
        return not self == other
