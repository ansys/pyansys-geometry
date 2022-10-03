"""``Plane`` class module."""

from typing import Union

import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.checks import check_type, check_type_equivalence
from ansys.geometry.core.typing import RealSequence


class Plane(Frame):
    """
    Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : Optional[Union[~numpy.ndarray, RealSequence, Point]]
        Centered origin of the ``Frame``. By default, cartesian origin.
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector]]
        X-axis direction. By default, ``UNITVECTOR3D_X``
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector]]
        Y-axis direction. By default, ``UNITVECTOR3D_Y``
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Y,
    ):
        """Constructor method for ``Plane``."""
        super().__init__(origin, direction_x, direction_y)

    def is_point_contained(self, point: Point3D) -> bool:
        """Method for checking if a Point is contained in the plane.

        Parameters
        ----------
        point : Point
            The :class:`Point` to be checked.

        Returns
        -------
        bool
            Returns ``True`` if contained in the plane.
        """
        check_type(point, Point3D)
        if point.is_2d:
            raise ValueError("The point provided should be 3D.")

        # Compute the plane equation A*(x-x0) + B*(y-y0) + C*(z-z0)
        plane_eq = (
            self.direction_z.x * (point.x - self.origin.x).m
            + self.direction_z.y * (point.y - self.origin.y).m
            + self.direction_z.z * (point.z - self.origin.z).m
        )

        # If plane equation is equal to 0, your point is contained
        return True if np.isclose(plane_eq, 0.0) else False

    def __eq__(self, other: "Plane") -> bool:
        """Equals operator for ``Plane``."""
        check_type_equivalence(other, self)
        return (
            self.origin == other.origin
            and self.direction_x == other.direction_x
            and self.direction_y == other.direction_y
            and self.direction_z == other.direction_z
        )

    def __ne__(self, other: "Plane") -> bool:
        """Not equals operator for ``Plane``."""
        return not self == other
