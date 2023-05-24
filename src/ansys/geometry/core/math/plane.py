"""Provides the ``Plane`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.typing import RealSequence


class Plane(Frame):
    """
    Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D], default: ZERO_POINT3D
        Centered origin of the frame. The default is the Cartesian origin.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D], default: UNITVECTOR3D_X
        X-axis direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D], default: UNITVECTOR3D_Y
        Y-axis direction.
    """  # noqa : E501

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Y,
    ):
        """Initialize ``Plane`` class."""
        super().__init__(origin, direction_x, direction_y)

    @check_input_types
    def is_point_contained(self, point: Point3D) -> bool:
        """
        Check if a 3D point is contained in the plane.

        Parameters
        ----------
        point : Point3D
            :class:`Point3D <ansys.geometry.core.math.point.Point3D>` class to check.

        Returns
        -------
        bool
            ``True`` if the 3D point is contained in the plane.
        """
        # Compute the plane equation A*(x-x0) + B*(y-y0) + C*(z-z0)
        plane_eq = (
            self.direction_z.x * (point.x - self.origin.x).m
            + self.direction_z.y * (point.y - self.origin.y).m
            + self.direction_z.z * (point.z - self.origin.z).m
        )

        # If plane equation is equal to 0, your point is contained
        return True if np.isclose(plane_eq, 0.0) else False

    @check_input_types
    def __eq__(self, other: "Plane") -> bool:
        """Equals operator for the ``Plane`` class."""
        return (
            self.origin == other.origin
            and self.direction_x == other.direction_x
            and self.direction_y == other.direction_y
            and self.direction_z == other.direction_z
        )

    def __ne__(self, other: "Plane") -> bool:
        """Not equals operator for the ``Plane`` class."""
        return not self == other
