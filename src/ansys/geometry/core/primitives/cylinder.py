""" Provides the ``Cylinder`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS, check_pint_unit_compatibility
from ansys.geometry.core.typing import Real, RealSequence


class Cylinder:
    """
    Provides 3D ``Cylinder`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the cylinder.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-plane direction.
    radius : Real
        Radius of the cylinder.
    height : Real
        Height of the cylinder.
    unit : Unit, optional
        Units for defining the radius and height. The default is ``UNIT_LENGTH``.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        radius: Real,
        height: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for the ``Cylinder`` class."""

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
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)
        self._height = UNITS.convert(height, self._unit, self._base_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the cylinder."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        self._origin = origin

    @property
    def radius(self) -> Real:
        """Radius of the cylinder."""
        return UNITS.convert(self._radius, self._base_unit, self._unit)

    @radius.setter
    @check_input_types
    def radius(self, radius: Real) -> None:
        """Set the radius of the cylinder."""
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def height(self) -> Real:
        """height of the cylinder."""
        return UNITS.convert(self._height, self._base_unit, self._unit)

    @height.setter
    @check_input_types
    def height(self, height: Real) -> None:
        """Set the height of the cylinder."""
        self._height = UNITS.convert(height, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the radius and height."""
        return self._unit

    @unit.setter
    @check_input_types
    def unit(self, unit: Unit) -> None:
        """Set the unit of the object."""
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    @check_input_types
    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Cylinder`` class."""
        return (
            self._origin == other.origin
            and self._radius == other.radius
            and self._height == other.height
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for the ``Cylinder`` class."""
        return not self == other
