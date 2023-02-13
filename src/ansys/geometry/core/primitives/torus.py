"""Provides the ``Torus`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, check_pint_unit_compatibility
from ansys.geometry.core.typing import Real, RealSequence


class Torus:
    """
    Provides 3D ``Torus`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D],
        Centered origin of the torus.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-axis direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-axis direction.
    major_radius : Real
        Major radius of the torus.
    minor_radius : Real
        Minor radius of ``Torus``.
    unit : ~pint.Unit, optional
        Units for defining the radius and minor radius. By default, ``DEFAULT_UNITS.LENGTH``
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        major_radius: Real,
        minor_radius: Real,
        unit: Optional[Unit] = DEFAULT_UNITS.LENGTH,
    ):
        """Constructor method for the ``Torus`` class."""

        check_pint_unit_compatibility(unit, DEFAULT_UNITS.LENGTH)
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
        """Origin of the torus."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        self._origin = origin

    @property
    def major_radius(self) -> Real:
        """Semi-major radius of the torus."""
        return UNITS.convert(self._major_radius, self._base_unit, self._unit)

    @major_radius.setter
    @check_input_types
    def major_radius(self, major_radius: Real) -> None:
        self._major_radius = UNITS.convert(major_radius, self._unit, self._base_unit)

    @property
    def minor_radius(self) -> Real:
        """Semi-minor radius of the torus."""
        return UNITS.convert(self._minor_radius, self._base_unit, self._unit)

    @minor_radius.setter
    @check_input_types
    def minor_radius(self, minor_radius: Real) -> None:
        self._minor_radius = UNITS.convert(minor_radius, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the semi-major radius and semi-minor radius."""
        return self._unit

    @unit.setter
    @check_input_types
    def unit(self, unit: Unit) -> None:
        check_pint_unit_compatibility(unit, DEFAULT_UNITS.LENGTH)
        self._unit = unit

    @check_input_types
    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Torus`` class."""
        return (
            self._origin == other.origin
            and self._major_radius == other.major_radius
            and self._minor_radius == other.minor_radius
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for the ``Torus`` class."""
        return not self == other
