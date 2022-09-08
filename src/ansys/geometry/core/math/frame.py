"""``Frame`` class module."""

from typing import List, Union

import numpy as np

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.checks import check_type, check_type_equivalence
from ansys.geometry.core.typing import RealSequence


class Frame:
    """
    Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Centered origin of the ``Frame``.
    direction_x: Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    direction_y: Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-plane direction.
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
    ):
        """Constructor method for ``Frame``."""

        check_type(origin, (np.ndarray, List, Point3D))
        check_type(direction_x, (np.ndarray, List, UnitVector3D, Vector3D))
        check_type(direction_y, (np.ndarray, List, UnitVector3D, Vector3D))

        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction_x = (
            UnitVector3D(direction_x) if not isinstance(direction_x, UnitVector3D) else direction_x
        )
        self._direction_y = (
            UnitVector3D(direction_y) if not isinstance(direction_y, UnitVector3D) else direction_y
        )

        # origin is fixed once the frame is built
        self._origin.setflags(write=False)

        if not self._direction_x.is_perpendicular_to(self._direction_y):
            raise ValueError("Direction x and direction y must be perpendicular")

        self._direction_z = UnitVector3D(self._direction_x % self._direction_y)

    @property
    def origin(self):
        """Return the origin of the ``Frame``."""
        return self._origin

    @property
    def direction_x(self):
        """Return the direction_x of the ``Frame``."""
        return self._direction_z

    @property
    def direction_y(self):
        """Return the direction_y of the ``Frame``."""
        return self._direction_y

    @property
    def direction_z(self):
        """Return the direction_z of the ``Frame``."""
        return self._direction_z

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Frame``."""
        check_type_equivalence(other, self)

        return (
            self.origin == other.origin
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
            and self._direction_z == other._direction_z
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Frame``."""
        return not self == other
