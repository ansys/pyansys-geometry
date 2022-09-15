"""``Frame`` class module."""

from typing import List, Union

import numpy as np

from ansys.geometry.core.math.constants import UNIT_VECTOR_X, UNIT_VECTOR_Y, ZERO_POINT3D
from ansys.geometry.core.math.matrix import Matrix33
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import UnitVector, Vector
from ansys.geometry.core.misc import check_type, check_type_equivalence
from ansys.geometry.core.typing import RealSequence


class Frame:
    """
    Provides primitive representation of a frame (an origin and three fundamental directions).

    Parameters
    ----------
    origin : Optional[Union[~numpy.ndarray, RealSequence, Point]]
        Centered origin of the ``Frame``. By default, cartesian origin.
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector]]
        X-axis direction. By default, ``UNIT_VECTOR_X``
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector]]
        Y-axis direction. By default, ``UNIT_VECTOR_Y``
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector, Vector] = UNIT_VECTOR_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector, Vector] = UNIT_VECTOR_Y,
    ):
        """Constructor method for ``Frame``."""

        check_type(origin, (np.ndarray, List, Point))
        check_type(direction_x, (np.ndarray, List, UnitVector, Vector))
        check_type(direction_y, (np.ndarray, List, UnitVector, Vector))

        self._origin = Point(origin) if not isinstance(origin, Point) else origin
        self._direction_x = (
            UnitVector(direction_x) if not isinstance(direction_x, UnitVector) else direction_x
        )
        self._direction_y = (
            UnitVector(direction_y) if not isinstance(direction_y, UnitVector) else direction_y
        )

        # origin is fixed once the frame is built
        self._origin.setflags(write=False)

        if not self._direction_x.is_perpendicular_to(self._direction_y):
            raise ValueError("Direction x and direction y must be perpendicular")

        self._direction_z = UnitVector(self._direction_x % self._direction_y)

    @property
    def origin(self) -> Point:
        """Return the origin of the ``Frame``."""
        return self._origin

    @property
    def direction_x(self) -> UnitVector:
        """Return the X-axis direction of the ``Frame``."""
        return self._direction_x

    @property
    def direction_y(self) -> UnitVector:
        """Return the Y-axis direction of the ``Frame``."""
        return self._direction_y

    @property
    def direction_z(self) -> UnitVector:
        """Return the Z-axis direction of the ``Frame``."""
        return self._direction_z

    @property
    def global_to_local(self) -> Matrix33:
        """Return the global to local space transformation matrix.

        Returns
        -------
        Matrix33
            A 3x3 matrix representing the transformation from local to global
            coordinate space.

        """
        return Matrix33(
            np.array(
                [
                    self.direction_x.tolist(),
                    self.direction_y.tolist(),
                    self.direction_z.tolist(),
                ]
            )
        )

    @property
    def local_to_global(self) -> Matrix33:
        """Return the local to global space transformation matrix.

        Returns
        -------
        Matrix33
            A 3x3 matrix representing the transformation from global to local
            coordinate space.

        """
        return self.global_to_local.T

    def __eq__(self, other: "Frame") -> bool:
        """Equals operator for ``Frame``."""
        check_type_equivalence(other, self)

        return (
            self.origin == other.origin
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
            and self._direction_z == other._direction_z
        )

    def __ne__(self, other: "Frame") -> bool:
        """Not equals operator for ``Frame``."""
        return not self == other
