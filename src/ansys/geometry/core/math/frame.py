"""``Frame`` class module."""

from typing import List, Union

import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.matrix import Matrix33, Matrix44
from ansys.geometry.core.math.point import Point2D, Point3D
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
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]]
        X-axis direction. By default, ``UNITVECTOR3D_X``.
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]]
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

        self._rotation_matrix = Matrix33(
            np.array(
                [
                    self.direction_x.tolist(),
                    self.direction_y.tolist(),
                    self.direction_z.tolist(),
                ]
            )
        )

        self._transformation_matrix = Matrix44(
            [
                [
                    self.direction_x.x,
                    self.direction_y.x,
                    self.direction_z.x,
                    self.origin.x.to_base_units().m,
                ],
                [
                    self.direction_x.y,
                    self.direction_y.y,
                    self.direction_z.y,
                    self.origin.y.to_base_units().m,
                ],
                [
                    self.direction_x.z,
                    self.direction_y.z,
                    self.direction_z.z,
                    self.origin.z.to_base_units().m,
                ],
                [0, 0, 0, 1],
            ]
        )

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
    def global_to_local_rotation(self) -> Matrix33:
        """Return the global to local space transformation matrix.

        Returns
        -------
        Matrix33
            A 3x3 matrix representing the transformation from global to local
            coordinate space excluding origin translation.

        """
        return self._rotation_matrix

    @property
    def local_to_global_rotation(self) -> Matrix33:
        """Return the local to global space transformation matrix.

        Returns
        -------
        Matrix33
            A 3x3 matrix representing the transformation from local to global
            coordinate space.

        """
        return self._rotation_matrix.T

    @property
    def transformation_matrix(self) -> Matrix44:
        """Returns the full 4x4 transformation matrix.

        Returns
        -------
        Matrix44
            A 4x4 matrix representing the transformation from global to local
            coordinate space.
        """
        return self._transformation_matrix

    def transform_point2d_local_to_global(self, point: Point2D) -> Point3D:
        """Expresses a local, plane-contained ``Point2D`` object in the global
        coordinate system, and thus it is represented as a ``Point3D``.

        Parameters
        ----------
        point : Point2D
            The ``Point2D`` local object to be expressed in global coordinates.

        Returns
        -------
        Point3D
            The global coordinates ``Point3D`` object.
        """
        local_point_as_3d = Point3D(
            [point.x.to_base_units().m, point.y.to_base_units().m, 0], point.base_unit
        )
        return self.origin + Point3D(
            self.local_to_global_rotation @ local_point_as_3d, point.base_unit
        )

    def __eq__(self, other: "Frame") -> bool:
        """Equals operator for ``Frame``."""
        check_type_equivalence(other, self)

        return (
            self.origin == other.origin
            and self.direction_x == other.direction_x
            and self.direction_y == other.direction_y
            and self.direction_z == other.direction_z
        )

    def __ne__(self, other: "Frame") -> bool:
        """Not equals operator for ``Frame``."""
        return not self == other
