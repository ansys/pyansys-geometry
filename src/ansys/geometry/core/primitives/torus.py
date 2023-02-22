"""Provides the ``Torus`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import Distance
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
    major_radius : Union[Quantity, Distance, Real]
        Major radius of the torus.
    minor_radius : Union[Quantity, Distance, Real]
        Minor radius of ``Torus``.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        major_radius: Union[Quantity, Distance, Real],
        minor_radius: Union[Quantity, Distance, Real],
    ):
        """Constructor method for the ``Torus`` class."""

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction_x = (
            UnitVector3D(direction_x) if not isinstance(direction_x, UnitVector3D) else direction_x
        )
        self._direction_y = (
            UnitVector3D(direction_y) if not isinstance(direction_y, UnitVector3D) else direction_y
        )

        # Store values in base unit
        self._major_radius = (
            major_radius if isinstance(major_radius, Distance) else Distance(major_radius)
        )
        self._minor_radius = (
            minor_radius if isinstance(minor_radius, Distance) else Distance(minor_radius)
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the torus."""
        return self._origin

    @property
    def major_radius(self) -> Quantity:
        """Semi-major radius of the torus."""
        return self._major_radius.value

    @property
    def minor_radius(self) -> Quantity:
        """Semi-minor radius of the torus."""
        return self._minor_radius.value

    @check_input_types
    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Torus`` class."""
        return (
            self._origin == other._origin
            and self._major_radius == other._major_radius
            and self._minor_radius == other._minor_radius
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for the ``Torus`` class."""
        return not self == other
