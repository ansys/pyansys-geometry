""" Provides the ``Sphere`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Unit

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS, check_pint_unit_compatibility
from ansys.geometry.core.typing import Real, RealSequence


class Sphere:
    """
    Provides 3D ``Sphere`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Centered origin of the sphere.
    radius : Real
        Radius of the sphere.
    unit : Unit, optional
        Units for defining the radius and height. The default
        is ``UNIT_LENGTH``.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Real,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor method for the ``Sphere`` class."""

        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        # Store values in base unit
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the sphere."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        self._origin = origin

    @property
    def radius(self) -> Real:
        """Radius of the sphere."""
        return UNITS.convert(self._radius, self._base_unit, self._unit)

    @radius.setter
    @check_input_types
    def radius(self, radius: Real) -> None:
        self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def unit(self) -> Unit:
        """Unit of the radius."""
        return self._unit

    @unit.setter
    @check_input_types
    def unit(self, unit: Unit) -> None:
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    @check_input_types
    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Sphere`` class."""
        return self._origin == other.origin and self._radius == other.radius

    def __ne__(self, other) -> bool:
        """Not equals operator for the ``Sphere`` class."""
        return not self == other
