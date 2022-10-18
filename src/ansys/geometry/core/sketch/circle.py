"""``Circle`` class module."""
from typing import Union

import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, Distance, check_type
from ansys.geometry.core.sketch.face import SketchFace


class Circle(SketchFace):
    """A sketch class for modeling circles.

    Parameters
    ----------
    center: Point2D
        A :class:`Point2D` representing the center of the circle.
    radius : Union[Quantity, Distance]
        The radius of the circle.
    """

    def __init__(
        self,
        center: Point2D,
        radius: Union[Quantity, Distance],
    ):
        """Initializes the circle shape."""
        super().__init__()

        check_type(center, Point2D)
        self._center = center

        check_type(radius, (Quantity, Distance))
        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

    @property
    def center(self) -> Point2D:
        """The center of the circle.

        Returns
        -------
        Point2D
            The center of the circle.
        """
        return self._center

    @property
    def radius(self) -> Quantity:
        """The radius of the circle.

        Returns
        -------
        Quantity
            The radius of the circle.
        """
        return self._radius.value

    @property
    def diameter(self) -> Quantity:
        """The diameter of the circle.

        Returns
        -------
        Quantity
            The diameter of the circle.
        """
        return 2 * self.radius

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the circle.

        Returns
        -------
        Quantity
            The perimeter of the circle.
        """
        return 2 * np.pi * self.radius

    @property
    def area(self) -> Quantity:
        """Return the area of the circle.

        Returns
        -------
        Quantity
            The area of the circle.
        """
        return np.pi * self.radius**2

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        Return the vtk polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            The vtk pyvista.Polydata configuration.
        """
        circle = pv.Circle(self.radius.m_as(UNIT_LENGTH))
        return circle.translate(
            [self.center.x.m_as(UNIT_LENGTH), self.center.y.m_as(UNIT_LENGTH), 0], inplace=True
        )
