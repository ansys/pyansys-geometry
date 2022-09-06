"""``CircleShape`` class module."""
from typing import Optional

import numpy as np

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class CircleShape(BaseShape):
    """A class for modelling circles."""

    def __init__(
        self,
        radius: Real,
        origin: Point3D,
        dir_1: UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D([0, 1, 0]),
    ):
        """Initializes the circle shape.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Point3D
            A :class:``Point3D`` representing the origin of the shape.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        """
        super().__init__(origin, dir_1, dir_2)
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

    @classmethod
    def from_radius(
        cls,
        radius: Real,
        origin: Optional[Point3D] = Point3D([0, 0, 0]),
        dir_1: Optional[UnitVector3D] = UnitVector3D([1, 0, 0]),
        dir_2: Optional[UnitVector3D] = UnitVector3D([0, 1, 0]),
    ):
        """Create an circle from its origin and radius.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Point3D
            A :class:``Point3D`` representing the origin of the ellipse.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        Returns
        -------
        CircleShape
            An object for modelling circular shapes.

        """
        # Verify that the radius is a real positive value
        if radius <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Generate all the point instances
        return cls(radius, origin, dir_1, dir_2)
