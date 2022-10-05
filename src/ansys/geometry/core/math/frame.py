"""``Frame`` class module."""

from typing import List, Union

import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.matrix import Matrix33
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc import check_type, check_type_equivalence
from ansys.geometry.core.typing import RealSequence


class Frame:
    """
    Provides primitive representation of a frame (an origin and three fundamental directions).

    Parameters
    ----------
    origin : Optional[Union[~numpy.ndarray, RealSequence, Point3D]]
        Centered origin of the ``Frame``. By default, cartesian origin.
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector3D]]
        X-axis direction. By default, ``UNITVECTOR3D_X``.
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector3D]]
        Y-axis direction. By default, ``UNITVECTOR3D_Y``.
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Y,
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
    def origin(self) -> Point3D:
        """Return the origin of the ``Frame``."""
        return self._origin

    @property
    def direction_x(self) -> UnitVector3D:
        """Return the X-axis direction of the ``Frame``."""
        return self._direction_x

    @property
    def direction_y(self) -> UnitVector3D:
        """Return the Y-axis direction of the ``Frame``."""
        return self._direction_y

    @property
    def direction_z(self) -> UnitVector3D:
        """Return the Z-axis direction of the ``Frame``."""
        return self._direction_z

    @property
    def global_to_local(self) -> Matrix33:
        """Return the global to local space transformation matrix.

        Returns
        -------
        Matrix33
            A 3x3 matrix representing the transformation from global to local
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
            A 3x3 matrix representing the transformation from local to global
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
