""" Provides the ``Sphere`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Z, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import Distance
from ansys.geometry.core.typing import RealSequence


class Sphere:
    """
    Provides 3D ``Sphere`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the sphere.
    radius : Real
        Radius of the sphere.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-plane direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Union[Quantity, Distance],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Constructor method for the ``Sphere`` class."""

        # check_pint_unit_compatibility(unit, UNIT_LENGTH)
        # self._unit = unit
        # _, self._base_unit = UNITS.get_base_units(unit)

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis
        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Circle reference (dir_x) and axis (dir_z) must be perpendicular.")

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        # # Store values in base unit
        # self._radius = UNITS.convert(radius, self._unit, self._base_unit)

    @property
    def origin(self) -> Point3D:
        """Origin of the sphere."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the sphere."""
        self._origin = origin

    @property
    def radius(self) -> Quantity:
        """Radius of the sphere."""
        return self._radius.value

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the sphere."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the sphere."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the sphere."""
        return self._axis

    @property
    def surface_area(self) -> Quantity:
        """Surface area of the sphere"""
        return 4 * np.pi * self.radius**2

    @property
    def volume(self) -> Quantity:
        return 4.0 / 3.0 * np.pi * self.radius**3

    @check_input_types
    def __eq__(self, other: "Sphere") -> bool:
        """Equals operator for the ``Sphere`` class."""
        return (
            self._origin == other._origin
            and self._radius == other._radius
            and self._reference == other._reference
            and self._axis == other._axis
        )


class SphereEvaluation:
    pass
