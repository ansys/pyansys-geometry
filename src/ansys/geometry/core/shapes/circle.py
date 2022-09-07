"""``CircleShape`` class module."""
from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class CircleShape(BaseShape):
    """A class for modelling circles.

    Parameters
    ----------
    radius : Real
        The radius of the circle.
    origin : Point3D
        A :class:`Point3D` representing the origin of the shape.
    dir_1 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the first fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_X``.
    dir_2 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the second fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_Y``.
    """

    def __init__(
        self,
        radius: Real,
        origin: Point3D,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Initializes the circle shape."""
        super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=True)
        self._radius = radius

    @property
    def radius(self) -> Real:
        """The radius of the circle.

        Returns
        -------
        Real
            The radius of the circle.
        """
        return self._radius

    @property
    def r(self) -> Real:
        """The radius of the circle.

        Returns
        -------
        Real
            The radius of the circle.
        """
        return self.radius

    @property
    def diameter(self) -> Real:
        """The diameter of the circle.

        Returns
        -------
        Real
            The diameter of the circle.
        """
        return 2 * self.r

    @property
    def d(self) -> Real:
        """The diameter of the circle.

        Returns
        -------
        Real
            The diameter of the circle.
        """
        return self.diameter

    @property
    def perimeter(self) -> Real:
        """Return the perimeter of the circle.

        Returns
        -------
        Real
            The perimeter of the circle.
        """
        return 2 * np.pi * self.r

    @property
    def area(self) -> Real:
        """Return the area of the circle.

        Returns
        -------
        Real
            The area of the circle.
        """
        return np.pi * self.r**2

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """Returns a list containing all the points belonging to the shape.

        Points are given in the local space.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point3D]
            A list of points representing the shape.
        """
        theta = np.linspace(0, 2 * np.pi, num_points)
        x_local = self.r * np.cos(theta)
        y_local = self.r * np.sin(theta)
        z_local = np.zeros(num_points)
        return [x_local, y_local, z_local]

    @classmethod
    def from_radius(
        cls,
        radius: Real,
        origin: Optional[Point3D] = Point3D([0, 0, 0]),
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Create a circle from its origin and radius.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Optional[Point3D]
            A :class:`Point3D` representing the origin of the ellipse.
            By default, [0, 0, 0].
        dir_1 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the first fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_X``.
        dir_2 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the second fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_Y``.

        Returns
        -------
        CircleShape
            An object for modelling circular shapes.
        """
        # Verify that the radius is a real positive value
        if radius <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Generate all the point instances
        return cls(radius, origin, dir_1=dir_1, dir_2=dir_2)
